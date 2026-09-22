"""Local throwaway demo server: POST /gerar → generate_batch on [::1]:8642."""

from __future__ import annotations

import functools
import json
import os
import re
import socket
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from pydantic import ValidationError

DEMO_DIR = Path(__file__).resolve().parent
REPO_ROOT = DEMO_DIR.parent
EXERCISE_AI = REPO_ROOT / "exercise-ai"

_ea = str(EXERCISE_AI)
if _ea not in sys.path:
    sys.path.insert(0, _ea)

_demo = str(DEMO_DIR)
if _demo not in sys.path:
    sys.path.insert(0, _demo)

from error_map import error_payload  # noqa: E402
from guards import assert_loopback, check_post_headers, lock_busy_response  # noqa: E402
from models import GenerationRequest  # noqa: E402
from service import (  # noqa: E402
    ConfigError,
    GenerationFailedError,
    InvalidRequestError,
    generate_batch,
)
from token_usage.collector import TOKEN_USAGE_DIR  # noqa: E402

HOST = "::1"
PORT = 8642

_VALID_PROVIDER = frozenset({"openai", "gemini", "grok"})
_VALID_REASONING = frozenset({"none", "low", "medium", "high"})
_SCOPED_ENV_KEYS = ("LLM_PROVIDER", "LLM_REASONING_EFFORT", "LLM_MODEL")
_DAY_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_INDISPONIVEL = "indisponível"

_GEN_LOCK = threading.Lock()
# Injectable for tests; default is exercise-ai/token-usage/.
_USAGE_DIR: Path = TOKEN_USAGE_DIR


def _iter_usage_events(base: Path) -> list[dict[str, Any]]:
    """Read UsageEvent dicts from {base}/YYYY-MM-DD/*.ndjson; skip corrupt lines."""
    if not base.exists() or not base.is_dir():
        return []
    try:
        base_resolved = base.resolve()
    except OSError:
        return []

    events: list[dict[str, Any]] = []
    try:
        day_dirs = sorted(p for p in base.iterdir() if p.is_dir())
    except OSError:
        return []

    for day_dir in day_dirs:
        if not _DAY_DIR_RE.match(day_dir.name):
            continue
        try:
            day_resolved = day_dir.resolve()
        except OSError:
            continue
        if not day_resolved.is_relative_to(base_resolved):
            continue
        try:
            ndjson_files = sorted(
                p for p in day_dir.iterdir() if p.is_file() and p.name.endswith(".ndjson")
            )
        except OSError:
            continue
        for path in ndjson_files:
            try:
                file_resolved = path.resolve()
            except OSError:
                continue
            if not file_resolved.is_relative_to(base_resolved):
                continue
            if not file_resolved.is_file():
                continue
            try:
                text = file_resolved.read_text(encoding="utf-8")
            except OSError:
                continue
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict):
                    events.append(obj)
    return events


def _sum_token_field(events: list[dict[str, Any]], key: str) -> int | str:
    nums = [ev[key] for ev in events if isinstance(ev.get(key), int)]
    if not nums:
        return _INDISPONIVEL
    return sum(nums)


def _sum_usd(events: list[dict[str, Any]]) -> float | str:
    vals = [
        float(ev["usd"])
        for ev in events
        if isinstance(ev.get("usd"), (int, float))
    ]
    if not vals:
        return _INDISPONIVEL
    return sum(vals)


def _empty_summary() -> dict[str, Any]:
    return {
        "prompt_tokens": _INDISPONIVEL,
        "completion_tokens": _INDISPONIVEL,
        "total_tokens": _INDISPONIVEL,
        "duration_ms": 0,
        "usd": _INDISPONIVEL,
        "tentativas": 0,
        "sucessos": 0,
        "erros": 0,
        "event_count": 0,
    }


def _summarize_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    duration = sum(
        int(ev["duration_ms"])
        for ev in events
        if isinstance(ev.get("duration_ms"), int)
    )
    return {
        "prompt_tokens": _sum_token_field(events, "prompt_tokens"),
        "completion_tokens": _sum_token_field(events, "completion_tokens"),
        "total_tokens": _sum_token_field(events, "total_tokens"),
        "duration_ms": duration,
        "usd": _sum_usd(events),
        "tentativas": sum(1 for ev in events if ev.get("status") == "attempt"),
        "sucessos": sum(1 for ev in events if ev.get("status") == "success"),
        "erros": sum(1 for ev in events if ev.get("status") == "error"),
        "event_count": len(events),
    }


def _usage_sessions_payload(base: Path) -> dict[str, Any]:
    events = _iter_usage_events(base)
    by_run: dict[str, list[dict[str, Any]]] = {}
    for ev in events:
        run_id = ev.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            continue
        by_run.setdefault(run_id, []).append(ev)

    sessions: list[dict[str, Any]] = []
    for run_id, subset in by_run.items():
        timestamps = [str(ev.get("ts", "")) for ev in subset if ev.get("ts")]
        timestamps_sorted = sorted(timestamps)
        providers = sorted(
            {
                str(ev["provider"])
                for ev in subset
                if isinstance(ev.get("provider"), str) and ev["provider"]
            }
        )
        sessions.append(
            {
                "run_id": run_id,
                "event_count": len(subset),
                "first_ts": timestamps_sorted[0] if timestamps_sorted else "",
                "last_ts": timestamps_sorted[-1] if timestamps_sorted else "",
                "providers": providers,
            }
        )
    sessions.sort(key=lambda s: s["last_ts"], reverse=True)
    return {"ok": True, "sessions": sessions}


def _is_safe_run_id(run_id: str) -> bool:
    if not run_id or ".." in run_id:
        return False
    if "/" in run_id or "\\" in run_id:
        return False
    return True


def _usage_session_payload(base: Path, run_id: str) -> dict[str, Any]:
    events = [
        ev
        for ev in _iter_usage_events(base)
        if isinstance(ev.get("run_id"), str) and ev["run_id"] == run_id
    ]
    events.sort(key=lambda ev: str(ev.get("ts", "")))
    summary = _summarize_events(events) if events else _empty_summary()
    return {
        "ok": True,
        "run_id": run_id,
        "events": events,
        "summary": summary,
    }


class DemoServer(ThreadingHTTPServer):
    """IPv6 loopback ThreadingHTTPServer (AF_INET6 required for ::1)."""

    address_family = socket.AF_INET6


def _apply_env(
    provider: str | None,
    reasoning: str | None,
    model: str | None = None,
) -> dict[str, Any]:
    """Snapshot env, apply provider/reasoning/model; caller must restore."""
    snapshot: dict[str, Any] = {
        key: os.environ.get(key) for key in _SCOPED_ENV_KEYS
    }
    snapshot["_present"] = {key: key in os.environ for key in _SCOPED_ENV_KEYS}

    prov = (provider or "").strip().lower()
    if prov in _VALID_PROVIDER:
        os.environ["LLM_PROVIDER"] = prov
    else:
        os.environ.pop("LLM_PROVIDER", None)

    reason = (reasoning or "").strip().lower()
    if reason in _VALID_REASONING:
        os.environ["LLM_REASONING_EFFORT"] = reason
    else:
        os.environ["LLM_REASONING_EFFORT"] = "medium"

    model_id = (model or "").strip()
    if model_id:
        os.environ["LLM_MODEL"] = model_id
    else:
        os.environ.pop("LLM_MODEL", None)

    return snapshot


def _restore_scoped_env(snapshot: dict[str, Any]) -> None:
    present: dict[str, bool] = snapshot.get("_present", {})
    for key in _SCOPED_ENV_KEYS:
        if present.get(key):
            value = snapshot.get(key)
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        else:
            os.environ.pop(key, None)


def _models_payload() -> dict[str, Any]:
    """Generation fallback lists for the demo model picker."""
    from model_catalog import (
        DEFAULT_GEMINI_MODEL,
        DEFAULT_GROK_MODEL,
        DEFAULT_OPENAI_MODEL,
        GEMINI_MODEL_FALLBACKS,
        GROK_MODEL_FALLBACKS,
        OPENAI_MODEL_FALLBACKS,
    )

    return {
        "openai": list(OPENAI_MODEL_FALLBACKS),
        "gemini": list(GEMINI_MODEL_FALLBACKS),
        "grok": list(GROK_MODEL_FALLBACKS),
        "defaults": {
            "openai": DEFAULT_OPENAI_MODEL,
            "gemini": DEFAULT_GEMINI_MODEL,
            "grok": DEFAULT_GROK_MODEL,
        },
    }


class DemoHandler(SimpleHTTPRequestHandler):
    """Static files from demo/ plus POST /gerar → generate_batch under Lock."""

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/models":
            self._send_json(200, _models_payload())
            return
        if path == "/usage/sessions":
            self._send_json(200, _usage_sessions_payload(_USAGE_DIR))
            return
        if path == "/usage/session":
            qs = parse_qs(parsed.query)
            raw_ids = qs.get("run_id") or []
            run_id = raw_ids[0] if raw_ids else ""
            if not _is_safe_run_id(run_id):
                self._send_json(
                    400,
                    {
                        "ok": False,
                        "error": {
                            "class": "InvalidRequestError",
                            "message": "run_id inválido",
                            "kind": "validation",
                        },
                    },
                )
                return
            self._send_json(200, _usage_session_payload(_USAGE_DIR, run_id))
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        if self.path.split("?", 1)[0] != "/gerar":
            self.send_error(404, "Not Found")
            return

        header_status = check_post_headers(
            self.headers.get("Host"),
            self.headers.get("Origin"),
            self.headers.get("Content-Type"),
        )
        if header_status is not None:
            self._send_json(
                header_status,
                {
                    "ok": False,
                    "error": {
                        "class": "HeaderError",
                        "message": f"Rejected headers (HTTP {header_status})",
                    },
                },
            )
            return

        if not _GEN_LOCK.acquire(blocking=False):
            status, payload = lock_busy_response()
            self._send_json(status, payload)
            return

        try:
            length = int(self.headers.get("Content-Length") or "0")
            raw = self.rfile.read(length) if length > 0 else b"{}"
            try:
                body = json.loads(raw.decode("utf-8") or "{}")
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                self._send_json(
                    400,
                    {
                        "ok": False,
                        "error": {
                            "class": "InvalidRequestError",
                            "message": f"JSON inválido: {exc}",
                            "kind": "invalid_json",
                        },
                    },
                )
                return

            if not isinstance(body, dict):
                self._send_json(
                    400,
                    {
                        "ok": False,
                        "error": {
                            "class": "InvalidRequestError",
                            "message": "Body JSON deve ser um objeto",
                            "kind": "invalid_json",
                        },
                    },
                )
                return

            provider = body.get("provider")
            reasoning = body.get("reasoning")
            model = body.get("model")
            snapshot = _apply_env(
                provider if isinstance(provider, str) else None,
                reasoning if isinstance(reasoning, str) else None,
                model if isinstance(model, str) else None,
            )
            try:
                try:
                    # D-15: pass plano when present; do not force dificuldade="medio"
                    # (mixed clients omit top-level dificuldade).
                    req_kwargs: dict[str, Any] = {
                        "materia": body.get("materia", "Matemática"),
                        "topico": body.get("topico", ""),
                        "quantidade": body.get("quantidade", 1),
                    }
                    if body.get("plano") is not None:
                        req_kwargs["plano"] = body["plano"]
                    dificuldade = body.get("dificuldade")
                    if dificuldade is not None and dificuldade != "":
                        req_kwargs["dificuldade"] = dificuldade
                    request = GenerationRequest(**req_kwargs)
                except ValidationError as exc:
                    self._send_json(
                        400,
                        {
                            "ok": False,
                            "error": {
                                "class": "InvalidRequestError",
                                "message": str(exc),
                                "kind": "validation",
                            },
                        },
                    )
                    return

                try:
                    batch = generate_batch(request)
                except (ConfigError, InvalidRequestError, GenerationFailedError) as exc:
                    self._send_json(200, {"ok": False, "error": error_payload(exc)})
                    return

                self._send_json(200, {"ok": True, "batch": batch.model_dump()})
            finally:
                _restore_scoped_env(snapshot)
        finally:
            _GEN_LOCK.release()

    def _send_json(self, status: int, obj: dict[str, Any]) -> None:
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        # Keep terminal quiet during tests; __main__ still gets default via subclass? 
        # Use stderr lightly without secrets.
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))


def make_handler() -> type[DemoHandler]:
    """Bind handler to demo/ directory without os.chdir."""
    return functools.partial(DemoHandler, directory=str(DEMO_DIR))  # type: ignore[return-value]


def create_server(
    host: str = HOST,
    port: int = PORT,
) -> DemoServer:
    handler = make_handler()
    return DemoServer((host, port), handler)


if __name__ == "__main__":
    from dotenv import load_dotenv

    # Multi-path .env: repo root then exercise-ai/
    load_dotenv(REPO_ROOT / ".env")
    load_dotenv(EXERCISE_AI / ".env")

    assert_loopback(HOST)
    with create_server(HOST, PORT) as httpd:
        print(f"Demo em http://[{HOST}]:{PORT}/  (Ctrl+C para parar)")
        httpd.serve_forever()
