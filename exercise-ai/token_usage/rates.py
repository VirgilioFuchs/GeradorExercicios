"""Local approximate USD rates per 1M tokens (input + output) by model string.

Rates are approximate / update manually — never scrape pricing pages (D-17).
Currency is USD only (D-15).
"""

from __future__ import annotations

from typing import Literal

INDISPONIVEL = "indisponível"
UsdSource = Literal["api", "rate_table", "indisponivel"]

# Approximate USD per 1M tokens: (input_per_1m, output_per_1m)
# Update manually when provider prices change.
_RATE_TABLE: dict[str, tuple[float, float]] = {
    # OpenAI
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
    # Gemini (ids used in generator_gemini.GEMINI_MODEL_FALLBACKS)
    "gemini-3.1-flash-lite": (0.075, 0.30),
    "gemini-3.5-flash": (0.075, 0.30),
    "gemini-3.6-flash": (0.075, 0.30),
    "gemini-3.7-flash": (0.075, 0.30),
    "gemini-3.8-flash": (0.075, 0.30),
    "gemini-2.0-flash": (0.10, 0.40),
    "gemini-2.5-flash": (0.15, 0.60),
    # Grok fallback when cost_in_usd_ticks absent
    "grok-4.6": (3.00, 15.00),
    "grok-3-mini": (0.30, 0.50),
}


def estimate_usd_from_rates(
    model: str,
    prompt_tokens: int | str,
    completion_tokens: int | str,
) -> tuple[float | str, UsdSource]:
    """Estimate USD from local rate table; missing model/tokens → indisponível."""
    if not isinstance(prompt_tokens, int) or not isinstance(completion_tokens, int):
        return INDISPONIVEL, "indisponivel"
    rates = _RATE_TABLE.get(model)
    if rates is None:
        return INDISPONIVEL, "indisponivel"
    in_rate, out_rate = rates
    usd = (prompt_tokens / 1_000_000) * in_rate + (completion_tokens / 1_000_000) * out_rate
    return usd, "rate_table"
