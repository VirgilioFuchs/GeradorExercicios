"""LLM model catalogs and generation fallbacks (source: Modelos.txt)."""

from __future__ import annotations

from pathlib import Path

_MODELOS_PATH = Path(__file__).resolve().parent.parent / "Modelos.txt"

# Exclude non-chat / non-structured-output-friendly ids from generation fallbacks.
_OPENAI_EXCLUDE_PARTS: tuple[str, ...] = (
    "image",
    "audio",
    "tts",
    "realtime",
    "transcribe",
    "live",
    "whisper",
    "search-preview",
    "search-api",
    "astra",  # GPT-6 flagship — omit from generation/selection fallbacks
)
_GEMINI_EXCLUDE_PARTS: tuple[str, ...] = (
    "image",
    "tts",
    "computer-use",
    "robotics",
    "transcribe",
)
_GROK_EXCLUDE_PARTS: tuple[str, ...] = (
    "multi-agent",
    "build",
    "code-fast",
)

_FALLBACK_CAP = 12


def _parse_modelos(text: str) -> dict[str, tuple[str, ...]]:
    """Parse Modelos.txt sections GPT / Gemini / Grok into id tuples."""
    sections: dict[str, list[str]] = {"GPT": [], "Gemini": [], "Grok": []}
    current: str | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line in sections:
            current = line
            continue
        if current is None:
            continue
        sections[current].append(line)
    return {k: tuple(v) for k, v in sections.items()}


def load_catalogs(path: Path | None = None) -> dict[str, tuple[str, ...]]:
    """Load catalogs from Modelos.txt (repo root by default)."""
    src = path if path is not None else _MODELOS_PATH
    return _parse_modelos(src.read_text(encoding="utf-8"))


def _filter_exclude(
    models: tuple[str, ...],
    exclude_parts: tuple[str, ...],
) -> tuple[str, ...]:
    out: list[str] = []
    for name in models:
        lower = name.lower()
        if any(part in lower for part in exclude_parts):
            continue
        out.append(name)
    return tuple(out)


def _capped(models: tuple[str, ...], *, cap: int = _FALLBACK_CAP) -> tuple[str, ...]:
    return models[:cap] if cap > 0 else models


_CATALOGS = load_catalogs()

OPENAI_MODELS: tuple[str, ...] = _CATALOGS["GPT"]
GEMINI_MODELS: tuple[str, ...] = _CATALOGS["Gemini"]
GROK_MODELS: tuple[str, ...] = _CATALOGS["Grok"]


def _prefer(fallbacks: tuple[str, ...], preferred: tuple[str, ...]) -> tuple[str, ...]:
    """Pin preferred ids first when present in the filtered catalog."""
    ordered: list[str] = []
    for name in preferred:
        if name in fallbacks and name not in ordered:
            ordered.append(name)
    for name in fallbacks:
        if name not in ordered:
            ordered.append(name)
    return tuple(ordered)


def _build_fallbacks(
    models: tuple[str, ...],
    exclude_parts: tuple[str, ...],
    preferred: tuple[str, ...],
    *,
    cap: int = _FALLBACK_CAP,
) -> tuple[str, ...]:
    filtered = _filter_exclude(models, exclude_parts)
    return _capped(_prefer(filtered, preferred), cap=cap)


OPENAI_MODEL_FALLBACKS: tuple[str, ...] = _build_fallbacks(
    OPENAI_MODELS,
    _OPENAI_EXCLUDE_PARTS,
    (
        "gpt-5.6-luna",
        "gpt-6-luna",
        "gpt-6-sol",
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-5-mini",
        "gpt-5",
    ),
)
GEMINI_MODEL_FALLBACKS: tuple[str, ...] = _build_fallbacks(
    GEMINI_MODELS,
    _GEMINI_EXCLUDE_PARTS,
    (
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.6-flash",
        "gemini-3.7-flash",
        "gemini-3.8-flash",
        "gemini-2.5-flash",
    ),
)
GROK_MODEL_FALLBACKS: tuple[str, ...] = _build_fallbacks(
    GROK_MODELS,
    _GROK_EXCLUDE_PARTS,
    ("grok-4.6", "grok-4.5", "grok-4.3", "grok-4.20"),
)

DEFAULT_OPENAI_MODEL = OPENAI_MODEL_FALLBACKS[0]
DEFAULT_GEMINI_MODEL = GEMINI_MODEL_FALLBACKS[0]
DEFAULT_GROK_MODEL = GROK_MODEL_FALLBACKS[0]


def model_candidates(preferred: str, fallbacks: tuple[str, ...]) -> list[str]:
    """Preferred first, then remaining fallbacks (deduped)."""
    ordered: list[str] = [preferred]
    for name in fallbacks:
        if name not in ordered:
            ordered.append(name)
    return ordered
