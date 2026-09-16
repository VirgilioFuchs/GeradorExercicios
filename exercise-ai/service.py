"""Host-callable embed seam for exercise batch generation."""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager

from models import ExerciseBatch, GenerationRequest

logger = logging.getLogger("exercise_ai.service")

_SCOPED_ENV_KEYS = ("LLM_PROVIDER", "LLM_REASONING_EFFORT")


class ConfigError(ValueError):
    """Invalid or missing configuration; host must fix before retrying."""

    def __init__(self, message: str, *, kind: str) -> None:
        super().__init__(message)
        self.kind = kind


class InvalidRequestError(ValueError):
    """Request/batch rejected after validation (including exhaustion)."""

    def __init__(self, message: str, *, kind: str) -> None:
        super().__init__(message)
        self.kind = kind


class GenerationFailedError(RuntimeError):
    """Provider/API generation failure with optional failover attrs."""

    def __init__(
        self,
        message: str,
        *,
        retriable: bool | None = None,
        api_error_kind: str | None = None,
    ) -> None:
        super().__init__(message)
        if retriable is not None:
            self.retriable = retriable
        if api_error_kind is not None:
            self.api_error_kind = api_error_kind


# Pipeline imports after error types so sibling modules can import them safely.
from failover import generate_with_failover  # noqa: E402
from reliability import resolve_max_retries  # noqa: E402
from token_usage import begin_run, flush_token_usage  # noqa: E402


@contextmanager
def _scoped_env() -> Iterator[None]:
    """Always snapshot/restore provider and reasoning env (D-08)."""
    snapshot: dict[str, str | None] = {
        key: os.environ.get(key) for key in _SCOPED_ENV_KEYS
    }
    present = {key: key in os.environ for key in _SCOPED_ENV_KEYS}
    try:
        yield
    finally:
        for key in _SCOPED_ENV_KEYS:
            if present[key]:
                os.environ[key] = snapshot[key]  # type: ignore[assignment]
            else:
                os.environ.pop(key, None)


def generate_batch(request: GenerationRequest) -> ExerciseBatch:
    """Run the generation pipeline and return a validated batch.

    Library path only: no exercise dump, ``--out`` write, fail-log, or process exit.
    Token lifecycle (begin/flush) is owned here; callers may flush again idempotently.
    """
    with _scoped_env():
        begin_run()
        try:
            n = resolve_max_retries(None)
            return generate_with_failover(request, max_retries=n)
        except (ConfigError, InvalidRequestError, GenerationFailedError) as exc:
            kind = getattr(exc, "kind", None) or getattr(exc, "api_error_kind", None)
            logger.error(
                "generate_batch failed type=%s kind=%s",
                type(exc).__name__,
                kind,
            )
            raise
        finally:
            try:
                flush_token_usage()
            except OSError:
                pass
