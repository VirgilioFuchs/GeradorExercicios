"""In-memory token usage collector with end-of-run NDJSON flush (D-01…D-04, D-20)."""

from __future__ import annotations

import json
import sys
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from token_usage.rates import INDISPONIVEL

# Injectable for tests; default data dir under exercise-ai/token-usage/ (hyphen).
TOKEN_USAGE_DIR: Path = Path(__file__).resolve().parent.parent / "token-usage"

Status = Literal["success", "error", "attempt"]
UsdSource = Literal["api", "rate_table", "indisponivel"]

_MISSING = object()


@dataclass
class UsageEvent:
    ts: str
    provider: str
    model: str
    status: Status
    prompt_tokens: int | str
    completion_tokens: int | str
    total_tokens: int | str
    duration_ms: int
    usd: float | str
    usd_source: UsdSource
    run_id: str
    error_kind: str | None = None


@dataclass
class TokenUsageCollector:
    """Process-local event buffer; flush appends NDJSON then clears (idempotent)."""

    run_id: str = ""
    events: list[UsageEvent] = field(default_factory=list)

    def begin_run(self, run_id: str | None = None) -> str:
        self.run_id = run_id or uuid.uuid4().hex[:12]
        self.events.clear()
        return self.run_id

    def record(
        self,
        *,
        provider: str,
        model: str,
        status: Status,
        prompt_tokens: int | str = INDISPONIVEL,
        completion_tokens: int | str = INDISPONIVEL,
        total_tokens: int | str = INDISPONIVEL,
        duration_ms: int = 0,
        usd: float | str = INDISPONIVEL,
        usd_source: UsdSource = "indisponivel",
        error_kind: str | None = None,
        print_usage: bool = True,
    ) -> UsageEvent:
        """Append one event (never replaces prior events — TOKEN-01)."""
        event = UsageEvent(
            ts=datetime.now().astimezone().isoformat(timespec="seconds"),
            provider=provider,
            model=model,
            status=status,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            duration_ms=duration_ms,
            usd=usd,
            usd_source=usd_source,
            run_id=self.run_id or uuid.uuid4().hex[:12],
            error_kind=error_kind,
        )
        self.events.append(event)
        if print_usage:
            _print_usage_line(event)
        return event

    def retag_last(
        self,
        status: Status,
        *,
        error_kind: str | None | object = _MISSING,
    ) -> UsageEvent | None:
        """Update status of the most recent event (RELY attempt tagging)."""
        if not self.events:
            return None
        last = self.events[-1]
        last.status = status
        if error_kind is not _MISSING:
            last.error_kind = error_kind  # type: ignore[assignment]
        return last

    def flush(self, base_dir: Path | None = None) -> None:
        """Append NDJSON under {day}/{provider}.ndjson; clear buffer (D-01, D-04)."""
        if not self.events:
            return
        root = base_dir if base_dir is not None else TOKEN_USAGE_DIR
        day = datetime.now().astimezone().date().isoformat()
        day_dir = root / day
        try:
            day_dir.mkdir(parents=True, exist_ok=True)

            by_provider: dict[str, list[UsageEvent]] = {}
            for ev in self.events:
                by_provider.setdefault(ev.provider, []).append(ev)

            for provider, evs in by_provider.items():
                path = day_dir / f"{provider}.ndjson"
                with path.open("a", encoding="utf-8") as fh:
                    for ev in evs:
                        fh.write(json.dumps(_event_to_dict(ev), ensure_ascii=False) + "\n")

            _print_run_summary(self.events)
        except OSError:
            # Never mask an in-flight exception from the caller's finally (D-07).
            pass
        finally:
            self.events.clear()


_collector = TokenUsageCollector()


def get_collector() -> TokenUsageCollector:
    return _collector


def begin_run(run_id: str | None = None) -> str:
    return _collector.begin_run(run_id)


def flush_token_usage() -> None:
    try:
        _collector.flush()
    except OSError:
        pass


def _event_to_dict(ev: UsageEvent) -> dict[str, Any]:
    data = asdict(ev)
    if data.get("error_kind") is None:
        del data["error_kind"]
    return data


def _fmt_field(value: int | float | str) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _print_usage_line(ev: UsageEvent) -> None:
    # Token counts only — never prompts, completions, or secrets (D-07, D-08).
    parts = [
        f"[USAGE] provider={ev.provider}",
        f"model={ev.model}",
        f"status={ev.status}",
        f"in={_fmt_field(ev.prompt_tokens)}",
        f"out={_fmt_field(ev.completion_tokens)}",
        f"total={_fmt_field(ev.total_tokens)}",
        f"duration_ms={ev.duration_ms}",
        f"usd={_fmt_field(ev.usd)}",
    ]
    print(" ".join(parts), file=sys.stderr)


def _print_run_summary(events: list[UsageEvent]) -> None:
    """End-of-run totals per provider; USD sum of numeric values only (D-18)."""
    providers = sorted({e.provider for e in events})
    unpriced = 0
    for provider in providers:
        subset = [e for e in events if e.provider == provider]
        in_sum = _sum_numeric([e.prompt_tokens for e in subset])
        out_sum = _sum_numeric([e.completion_tokens for e in subset])
        total_sum = _sum_numeric([e.total_tokens for e in subset])
        usd_vals = [e.usd for e in subset if isinstance(e.usd, (int, float))]
        unpriced += sum(1 for e in subset if not isinstance(e.usd, (int, float)))
        usd_sum = sum(float(v) for v in usd_vals)
        usd_part = f"{usd_sum:.6g}" if usd_vals else INDISPONIVEL
        print(
            f"[USAGE] resumo provider={provider} "
            f"in={in_sum if in_sum is not None else INDISPONIVEL} "
            f"out={out_sum if out_sum is not None else INDISPONIVEL} "
            f"total={total_sum if total_sum is not None else INDISPONIVEL} "
            f"usd={usd_part} eventos={len(subset)}",
            file=sys.stderr,
        )
    print(
        f"[USAGE] resumo run eventos_sem_preco={unpriced}",
        file=sys.stderr,
    )


def _sum_numeric(values: list[int | str]) -> int | None:
    nums = [v for v in values if isinstance(v, int)]
    if not nums:
        return None
    return sum(nums)
