"""Unified reasoning / thinking effort for OpenAI, Gemini, and Grok.

Operator surface: CLI ``--reasoning`` / env ``LLM_REASONING_EFFORT``
(``none|low|medium|high``, default ``medium``).

GPT-6 (and some GPT-5.6) APIs also accept ``xhigh`` / ``max``; those are
intentionally omitted from this shared surface — they are not compatible with
Gemini/Grok or non-reasoning OpenAI models in the same picker.
"""

from __future__ import annotations

import os
import sys
from typing import Literal

ReasoningLevel = Literal["none", "low", "medium", "high"]

REASONING_LEVELS: tuple[ReasoningLevel, ...] = ("none", "low", "medium", "high")
# API-only levels stripped for cross-model compatibility (do not expose in UI/CLI).
_API_ONLY_REASONING_LEVELS: frozenset[str] = frozenset({"xhigh", "max"})
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
    if level in _API_ONLY_REASONING_LEVELS:
        raise ConfigError(
            f"reasoning '{level}' não é compatível com o surface compartilhado "
            f"(use {', '.join(REASONING_LEVELS)}).",
            kind="invalid_reasoning",
        )
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


def supported_reasoning_levels(api_tag: str, model: str = "") -> tuple[ReasoningLevel, ...]:
    """Levels this provider/model may use on the shared operator surface.

    Empty tuple = model does not accept reasoning (UI should hide options).
    Never includes ``xhigh`` / ``max`` (API-only; incompatible with other models).
    """
    tag = (api_tag or "").strip().lower()
    if tag in ("gemini", "grok"):
        return REASONING_LEVELS
    if tag == "openai":
        if openai_supports_reasoning_effort(model):
            return REASONING_LEVELS
        return ()
    # auto / unknown: shared surface when no model pinned
    if not (model or "").strip():
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
        if raw and raw not in ("",) and raw in _API_ONLY_REASONING_LEVELS:
            raise ConfigError(
                f"reasoning '{raw}' não é compatível com o surface compartilhado.",
                kind="invalid_reasoning",
            )
        return None
    if not raw:
        return DEFAULT_REASONING_EFFORT
    if raw in _API_ONLY_REASONING_LEVELS:
        raise ConfigError(
            f"reasoning '{raw}' não é compatível com outros modelos "
            f"(use {', '.join(supported)}).",
            kind="invalid_reasoning",
        )
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
