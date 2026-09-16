"""Thin OpenAI ↔ Gemini provider failover envelope (Phase 8).

Re-invokes ``generate_validated_batch`` at most once on the peer after an
eligible permanent API error. Does not nest a second RELY/math loop.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Callable

from generator import _resolve_provider
from models import ExerciseBatch, GenerationRequest
from reliability import generate_validated_batch

_ELIGIBLE_KINDS = frozenset({"timeout", "rate_limit", "connection", "generic"})

_KEY_ENV = {
    "openai": "LLM_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "grok": "GROK_API_KEY",
}


def is_failover_eligible(exc: BaseException) -> bool:
    """True only for permanent API errors with an eligible availability kind (D-01; D-02)."""
    if getattr(exc, "retriable", None) is not False:
        return False
    kind = getattr(exc, "api_error_kind", None)
    return kind in _ELIGIBLE_KINDS


def failover_peer(provider: str) -> str | None:
    """OpenAI ↔ Gemini only; Grok/unknown → None (D-04; D-06)."""
    if provider == "openai":
        return "gemini"
    if provider == "gemini":
        return "openai"
    return None


def ensure_secondary_key(provider: str) -> None:
    """Raise ConfigError if the secondary provider key is missing (D-03)."""
    from service import ConfigError

    env_name = _KEY_ENV.get(provider)
    if env_name is None:
        raise ConfigError(
            f"Provedor secundário desconhecido: {provider}.",
            kind="unknown_provider",
        )
    if not os.getenv(env_name, "").strip():
        raise ConfigError(
            f"Chave ausente para o provedor {provider}. Defina {env_name} no arquivo .env.",
            kind="secondary_missing_key",
        )


def _default_switch_provider(name: str) -> None:
    os.environ["LLM_PROVIDER"] = name


def generate_with_failover(
    request: GenerationRequest,
    max_retries: int,
    *,
    generate_fn: Callable[..., ExerciseBatch] = generate_validated_batch,
    resolve_provider: Callable[[], str] = _resolve_provider,
    switch_provider: Callable[[str], None] = _default_switch_provider,
) -> ExerciseBatch:
    """Call generate_fn on primary; on eligible failure, switch once to peer (D-07; D-09)."""
    primary = resolve_provider()
    peer = failover_peer(primary)

    if peer is None:
        return generate_fn(request, max_retries)

    try:
        return generate_fn(request, max_retries)
    except Exception as primary_exc:
        if not is_failover_eligible(primary_exc):
            raise

        kind = getattr(primary_exc, "api_error_kind", "generic")
        print(f"[FAILOVER] {primary} -> {peer} ({kind})", file=sys.stderr)
        ensure_secondary_key(peer)
        switch_provider(peer)

        try:
            batch = generate_fn(request, max_retries)
        except Exception:
            raise

        print(f"[FAILOVER] usado: {peer}", file=sys.stderr)
        return batch
