"""Unified reasoning / thinking effort for OpenAI, Gemini, and Grok.

Operator surface: CLI ``--reasoning`` / env ``LLM_REASONING_EFFORT``
(``none|low|medium|high`` plus OpenAI-extended ``xhigh|max``, default ``medium``).

``xhigh`` / ``max`` belong to OpenAI reasoning models (GPT-5*/GPT-6*/o*).
Gemini and Grok do not get them — the demo hides those options when the
selected provider/model does not support them.
"""

from __future__ import annotations

import os
import sys
from typing import Literal

ReasoningLevel = Literal["none", "low", "medium", "high", "xhigh", "max"]

# Shared by Gemini / Grok / non-extended surfaces.
REASONING_LEVELS: tuple[ReasoningLevel, ...] = ("none", "low", "medium", "high")
# OpenAI reasoning models (GPT-5*, GPT-6*, o*): include API extended efforts.
OPENAI_REASONING_LEVELS: tuple[ReasoningLevel, ...] = (
    "none",
    "low",
    "medium",
    "high",
    "xhigh",
    "max",
)
DEFAULT_REASONING_EFFORT: ReasoningLevel = "medium"
ENV_REASONING = "LLM_REASONING_EFFORT"

# Conservative allowlist prefixes for OpenAI models that accept reasoning_effort.
_OPENAI_REASONING_PREFIXES: tuple[str, ...] = (
    "gpt-5",
    "gpt-6",
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
    if level not in OPENAI_REASONING_LEVELS:
        raise ConfigError(
            f"reasoning inválido '{raw}': use {', '.join(OPENAI_REASONING_LEVELS)}.",
            kind="invalid_reasoning",
        )
    return level  # type: ignore[return-value]


def to_gemini_thinking_level(effort: ReasoningLevel) -> str:
    """Map unified level to Gemini ``thinking_level`` (``none`` → ``minimal``)."""
    if effort == "none":
        return "minimal"
    if effort in ("xhigh", "max"):
        # Should not reach here after assert_reasoning_compatible; clamp defensively.
        return "high"
    return effort


def openai_supports_reasoning_effort(model: str) -> bool:
    """True when the OpenAI model id is known to accept ``reasoning_effort``."""
    m = (model or "").strip().lower()
    return any(m.startswith(prefix) for prefix in _OPENAI_REASONING_PREFIXES)


def supported_reasoning_levels(api_tag: str, model: str = "") -> tuple[ReasoningLevel, ...]:
    """Levels this provider/model may expose in UI / accept in validation.

    Empty tuple = model does not accept reasoning (UI shows N/A).
    OpenAI reasoning models include ``xhigh`` / ``max``; Gemini/Grok do not.
    """
    tag = (api_tag or "").strip().lower()
    mid = (model or "").strip()
    if tag in ("gemini", "grok"):
        return REASONING_LEVELS
    if tag == "openai":
        if not mid or openai_supports_reasoning_effort(mid):
            return OPENAI_REASONING_LEVELS
        return ()
    # auto / unknown provider
    if not mid:
        return REASONING_LEVELS
    return ()


def assert_reasoning_compatible(
    api_tag: str,
    model: str,
    effort: str | None,
) -> ReasoningLevel | None:
    """Validate ``effort`` for model; return normalized level or None if N/A.

    Raises ConfigError when the level is invalid or unsupported for the model.
    When the model has no reasoning surface, returns None (caller should omit).
    """
    from service import ConfigError

    supported = supported_reasoning_levels(api_tag, model)
    raw = (effort or "").strip().lower()
    if not supported:
        return None
    if not raw:
        return DEFAULT_REASONING_EFFORT
    if raw not in supported:
        raise ConfigError(
            f"reasoning '{raw}' não suportado por {model or api_tag}: "
            f"use {', '.join(supported)}.",
            kind="invalid_reasoning",
        )
    return raw  # type: ignore[return-value]


def openai_compatible_effort_kwargs(
    *,
    api_tag: str,
    model: str,
    effort: ReasoningLevel | None = None,
) -> dict[str, str]:
    """Kwargs for ``chat.completions.parse``.

    Grok: always pass ``reasoning_effort`` (base levels only in practice).
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
