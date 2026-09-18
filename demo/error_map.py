"""Map service exceptions to typed demo error JSON (D-10)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_EXERCISE_AI = Path(__file__).resolve().parents[1] / "exercise-ai"
_ea = str(_EXERCISE_AI)
if _ea not in sys.path:
    sys.path.insert(0, _ea)

from service import ConfigError, GenerationFailedError, InvalidRequestError  # noqa: E402


def error_payload(exc: BaseException) -> dict[str, Any]:
    """Build ``{class, message, kind?}`` for the three generate_batch error types.

    EN class names; include ``kind`` when present. For ``GenerationFailedError``,
    map ``api_error_kind`` into the client-facing ``kind`` field (D-10).
    """
    name = type(exc).__name__
    message = str(exc)
    if isinstance(exc, ConfigError):
        return {"class": name, "message": message, "kind": exc.kind}
    if isinstance(exc, InvalidRequestError):
        return {"class": name, "message": message, "kind": exc.kind}
    if isinstance(exc, GenerationFailedError):
        payload: dict[str, Any] = {"class": name, "message": message}
        api_kind = getattr(exc, "api_error_kind", None)
        if api_kind is not None:
            payload["kind"] = api_kind
        else:
            payload["kind"] = None
        return payload
    return {"class": name, "message": message}
