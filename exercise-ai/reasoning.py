"""Unified reasoning / thinking effort for OpenAI, Gemini, and Grok.

Operator surface: CLI ``--reasoning`` / env ``LLM_REASONING_EFFORT``
(``none|low|medium|high``, default ``medium``).
"""

from __future__ import annotations

import os
import sys
from typing import Literal

ReasoningLevel = Literal["none", "low", "medium", "high"]

REASONING_LEVELS: tuple[ReasoningLevel, ...] = ("none", "low", "medium", "high")
DEFAULT_REASONING_EFFORT: ReasoningLevel = "medium"
ENV_REASONING = "LLM_REASONING_EFFORT"

# Conservative allowlist prefixes for OpenAI models that accept reasoning_effort.
_OPENAI_REASONING_PREFIXES: tuple[str, ...] = (
    "gpt-5",
    "o1",
    "o3",
    "o4",
)


def resolve_reasoning_effort(explicit: str | None = None) -> ReasoningLevel:
    """Return validated effort; CLI/explicit wins over env; default ``medium``."""
    from service import ConfigError

    raw = (explicit if explicit is not None else os.getenv(ENV_REASONING, "")).strip()
    if not raw:
        return DEFAULT_REASONING_EFFORT
    level = raw.lower()
    if level not in REASONING_LEVELS:
        raise ConfigError(
            f"reasoning inválido '{raw}': use {', '.join(REASONING_LEVELS)}.",
            kind="invalid_reasoning",
        )
    return level  # type: ignore[return-value]


def to_gemini_thinking_level(effort: ReasoningLevel) -> str:
    """Map unified level to Gemini ``thinking_level`` (``none`` → ``minimal``)."""
    if effort == "none":
        return "minimal"
    return effort


def openai_supports_reasoning_effort(model: str) -> bool:
    """True when the OpenAI model id is known to accept ``reasoning_effort``."""
    m = (model or "").strip().lower()
    return any(m.startswith(prefix) for prefix in _OPENAI_REASONING_PREFIXES)


def openai_compatible_effort_kwargs(
    *,
    api_tag: str,
    model: str,
    effort: ReasoningLevel | None = None,
) -> dict[str, str]:
    """Kwargs for ``chat.completions.parse``.

    Grok: always pass ``reasoning_effort``.
    OpenAI: pass only when the model supports it; otherwise omit + stderr tip.
    """
    level = effort if effort is not None else resolve_reasoning_effort()
    if api_tag == "grok":
        return {"reasoning_effort": level}
    if api_tag == "openai":
        if openai_supports_reasoning_effort(model):
            return {"reasoning_effort": level}
        print(
            f"[API:openai] reasoning_effort não suportado por {model}; ignorado.",
            file=sys.stderr,
        )
        return {}
    return {}
