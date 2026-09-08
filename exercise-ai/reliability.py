"""Bounded regeneration after retriable validation / invalid LLM response failures.

Phase 6 hook: future math failures (MATH-02) must reuse ``generate_validated_batch``
(raise a retriable ``ValueError`` from validation, or ``RuntimeError`` with
``retriable=True``) — do not invent a second retry path.
"""

from __future__ import annotations

import os
import sys
import time

from models import ExerciseBatch, GenerationRequest
from generator import generate_exercises
from validator import validate_exercise_batch

_ALLOWED = frozenset({0, 1, 2, 3})
_DEFAULT = 1


def resolve_max_retries(cli_value: int | None) -> int:
    """Resolve regenerations after first try: CLI > RELY_MAX_RETRIES > 1 (D-01..D-04)."""
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
                raise ValueError(
                    f"max-retries inválido '{raw}': use um inteiro 0, 1, 2 ou 3."
                ) from exc
    if n not in _ALLOWED:
        raise ValueError(
            f"max-retries inválido '{n}': use um inteiro 0, 1, 2 ou 3."
        )
    return n


def is_permanent_api_error(exc: BaseException) -> bool:
    """True when mappers marked the error non-retriable (auth/timeout/rate/conn)."""
    return getattr(exc, "retriable", None) is False


def is_retriable_invalid_response(exc: BaseException) -> bool:
    """True for invalid LLM response edges marked retriable=True (D-05, D-19)."""
    return getattr(exc, "retriable", None) is True


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
                    continue
                raise

            print("Validando…", file=sys.stderr)
            try:
                return validate_exercise_batch(batch, request)
            except ValueError as exc:
                last_err = exc
                if attempt < max_retries:
                    continue
                raise

        assert last_err is not None
        raise last_err
    finally:
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        print(
            f"duração total_ms={elapsed_ms} chamadas={calls}",
            file=sys.stderr,
        )
