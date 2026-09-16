"""Bounded regeneration after retriable validation / invalid LLM response failures.

Phase 6 hook: math failures (MATH-02) reuse ``generate_validated_batch``
(raise a retriable ``ValueError`` from validation, or ``RuntimeError`` with
``retriable=True``) — do not invent a second retry path.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from models import ExerciseBatch, GenerationRequest
from generator import generate_exercises
from validator import validate_exercise_batch
from math_check import (
    clear_math_buffers,
    drain_inconsistency_records,
    drain_uninterpretable_records,
)
from output_paths import DEFAULT_POSTMORTEM_PATH
from token_usage import get_collector

_ALLOWED = frozenset({0, 1, 2, 3})
_DEFAULT = 1

# Injectable for tests; default under exercicios-gerados/fail/postmortem/.
POSTMORTEM_PATH: Path = DEFAULT_POSTMORTEM_PATH


def resolve_max_retries(cli_value: int | None) -> int:
    """Resolve regenerations after first try: CLI > RELY_MAX_RETRIES > 1 (D-01..D-04)."""
    from service import ConfigError

    if cli_value is not None:
        n = cli_value
    else:
        raw = os.getenv("RELY_MAX_RETRIES", "").strip()
        if not raw:
            n = _DEFAULT
        else:
            try:
                n = int(raw)
            except ValueError as exc:
                raise ConfigError(
                    f"max-retries inválido '{raw}': use um inteiro 0, 1, 2 ou 3.",
                    kind="invalid_retries",
                ) from exc
    if n not in _ALLOWED:
        raise ConfigError(
            f"max-retries inválido '{n}': use um inteiro 0, 1, 2 ou 3.",
            kind="invalid_retries",
        )
    return n


def is_permanent_api_error(exc: BaseException) -> bool:
    """True when mappers marked the error non-retriable (auth/timeout/rate/conn)."""
    return getattr(exc, "retriable", None) is False


def is_retriable_invalid_response(exc: BaseException) -> bool:
    """True for invalid LLM response edges marked retriable=True (D-05, D-19)."""
    return getattr(exc, "retriable", None) is True


def _write_postmortem(path: Path) -> None:
    """Write diagnostic jsonl on final failure only (D-08; LOG-02 — no secrets)."""
    records = drain_inconsistency_records() + drain_uninterpretable_records()
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(rec, ensure_ascii=False) for rec in records]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def generate_validated_batch(
    request: GenerationRequest,
    max_retries: int,
) -> ExerciseBatch:
    """Generate → validate with bounded regenerations (Phase 5 + Phase 6 hook).

    Same ``request`` (hence same prompt) on every attempt. Only validator
    ``ValueError`` and ``RuntimeError`` with ``retriable=True`` regenerate.
    Permanent API errors and unmarked RuntimeError fail through immediately.
    Config ``ValueError`` from generate (missing keys) is never retried.
    """
    t0 = time.perf_counter()
    calls = 0
    last_err: BaseException | None = None

    try:
        for attempt in range(0, max_retries + 1):
            if attempt == 0:
                print("Gerando…", file=sys.stderr)
            else:
                print(f"{attempt}ª Regeneração", file=sys.stderr)
                print("Gerando…", file=sys.stderr)

            try:
                calls += 1
                batch = generate_exercises(request)
            except RuntimeError as exc:
                last_err = exc
                if is_permanent_api_error(exc):
                    raise
                if is_retriable_invalid_response(exc) and attempt < max_retries:
                    get_collector().retag_last(
                        "attempt",
                        error_kind=type(exc).__name__,
                    )
                    continue
                raise

            print("Validando…", file=sys.stderr)
            try:
                validated = validate_exercise_batch(batch, request)
                clear_math_buffers()
                return validated
            except ValueError as exc:
                last_err = exc
                if attempt < max_retries:
                    get_collector().retag_last(
                        "attempt",
                        error_kind="validation",
                    )
                    continue
                # Final failure: postmortem + optional exhaustion prefix (D-08, D-13)
                get_collector().retag_last(
                    "error",
                    error_kind="validation",
                )
                reason = str(exc)
                from service import InvalidRequestError

                if max_retries > 0:
                    raise InvalidRequestError(
                        f"após {max_retries} regenerações: {reason}",
                        kind="validation_exhausted",
                    ) from exc
                raise InvalidRequestError(
                    reason, kind="validation_exhausted"
                ) from exc

        assert last_err is not None
        raise last_err
    finally:
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        print(
            f"duração total_ms={elapsed_ms} chamadas={calls}",
            file=sys.stderr,
        )
