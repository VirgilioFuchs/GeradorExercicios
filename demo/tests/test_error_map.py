"""Offline unit tests for demo error_payload (D-10)."""

from __future__ import annotations

import sys
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = DEMO_DIR.parent
EXERCISE_AI = REPO_ROOT / "exercise-ai"
for path in (DEMO_DIR, EXERCISE_AI):
    s = str(path)
    if s not in sys.path:
        sys.path.insert(0, s)

from error_map import error_payload  # noqa: E402
from service import ConfigError, GenerationFailedError, InvalidRequestError  # noqa: E402


def test_config_error_shape() -> None:
    exc = ConfigError("chave ausente", kind="missing_key")
    payload = error_payload(exc)
    assert payload["class"] == "ConfigError"
    assert payload["message"] == "chave ausente"
    assert payload["kind"] == "missing_key"


def test_invalid_request_error_shape() -> None:
    exc = InvalidRequestError("lote inválido", kind="validation")
    payload = error_payload(exc)
    assert payload["class"] == "InvalidRequestError"
    assert payload["message"] == "lote inválido"
    assert payload["kind"] == "validation"


def test_generation_failed_maps_api_error_kind() -> None:
    exc = GenerationFailedError("falha API", api_error_kind="rate_limit")
    payload = error_payload(exc)
    assert payload["class"] == "GenerationFailedError"
    assert payload["message"] == "falha API"
    assert payload["kind"] == "rate_limit"


def test_generation_failed_without_kind_omits_or_none() -> None:
    exc = GenerationFailedError("falha genérica")
    payload = error_payload(exc)
    assert payload["class"] == "GenerationFailedError"
    assert payload["message"] == "falha genérica"
    # kind may be absent or None when api_error_kind was not set
    assert payload.get("kind") in (None, "")
