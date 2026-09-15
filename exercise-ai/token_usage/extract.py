"""Extract usage metadata from provider SDK responses (D-11).

Missing fields → string ``indisponível`` — never fabricate numeric 0 (D-09).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from token_usage.rates import INDISPONIVEL, UsdSource, estimate_usd_from_rates

TokenField = int | Literal["indisponível"]


@dataclass(frozen=True)
class UsageFields:
    prompt_tokens: TokenField
    completion_tokens: TokenField
    total_tokens: TokenField
    usd: float | Literal["indisponível"]
    usd_source: UsdSource


def _token_or_indisponivel(value: Any) -> TokenField:
    if value is None:
        return INDISPONIVEL
    if isinstance(value, bool):
        return INDISPONIVEL
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return INDISPONIVEL


def _openai_compatible_tokens(completion: object) -> tuple[TokenField, TokenField, TokenField]:
    usage = getattr(completion, "usage", None)
    if usage is None:
        return INDISPONIVEL, INDISPONIVEL, INDISPONIVEL
    return (
        _token_or_indisponivel(getattr(usage, "prompt_tokens", None)),
        _token_or_indisponivel(getattr(usage, "completion_tokens", None)),
        _token_or_indisponivel(getattr(usage, "total_tokens", None)),
    )


def extract_openai_usage(completion: object, *, model: str = "") -> UsageFields:
    """Read OpenAI ``completion.usage`` token counts; USD via rate table."""
    prompt, completion_tok, total = _openai_compatible_tokens(completion)
    usd, usd_source = estimate_usd_from_rates(model, prompt, completion_tok)
    return UsageFields(
        prompt_tokens=prompt,
        completion_tokens=completion_tok,
        total_tokens=total,
        usd=usd,
        usd_source=usd_source,
    )


def extract_grok_usage(completion: object, *, model: str = "") -> UsageFields:
    """OpenAI-compatible tokens; prefer ``cost_in_usd_ticks / 1e10`` for USD (D-14)."""
    prompt, completion_tok, total = _openai_compatible_tokens(completion)
    usage = getattr(completion, "usage", None)
    ticks = getattr(usage, "cost_in_usd_ticks", None) if usage is not None else None
    if ticks is not None:
        try:
            usd = float(ticks) / 1e10
            return UsageFields(
                prompt_tokens=prompt,
                completion_tokens=completion_tok,
                total_tokens=total,
                usd=usd,
                usd_source="api",
            )
        except (TypeError, ValueError):
            pass
    usd, usd_source = estimate_usd_from_rates(model, prompt, completion_tok)
    return UsageFields(
        prompt_tokens=prompt,
        completion_tokens=completion_tok,
        total_tokens=total,
        usd=usd,
        usd_source=usd_source,
    )


def extract_gemini_usage(response: object, *, model: str = "") -> UsageFields:
    """Read Gemini ``usage_metadata`` token counts; USD via rate table."""
    meta = getattr(response, "usage_metadata", None)
    if meta is None:
        prompt = completion_tok = total = INDISPONIVEL
    else:
        prompt = _token_or_indisponivel(getattr(meta, "prompt_token_count", None))
        completion_tok = _token_or_indisponivel(
            getattr(meta, "candidates_token_count", None)
        )
        total = _token_or_indisponivel(getattr(meta, "total_token_count", None))
    usd, usd_source = estimate_usd_from_rates(model, prompt, completion_tok)
    return UsageFields(
        prompt_tokens=prompt,
        completion_tokens=completion_tok,
        total_tokens=total,
        usd=usd,
        usd_source=usd_source,
    )
