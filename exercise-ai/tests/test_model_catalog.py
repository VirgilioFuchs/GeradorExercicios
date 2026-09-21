"""Tests for Modelos.txt catalogs and generation fallbacks."""

from __future__ import annotations

from pathlib import Path

import model_catalog as catalog


def test_catalogs_load_from_modelos_txt() -> None:
    assert len(catalog.OPENAI_MODELS) > 20
    assert "gpt-4o-mini" in catalog.OPENAI_MODELS
    assert "gpt-5.6-luna" in catalog.OPENAI_MODELS
    assert "gemini-3.1-flash-lite" in catalog.GEMINI_MODELS
    assert "grok-4.6" in catalog.GROK_MODELS


def test_fallbacks_exclude_non_chat_models() -> None:
    assert all("image" not in m for m in catalog.OPENAI_MODEL_FALLBACKS)
    assert all("tts" not in m for m in catalog.OPENAI_MODEL_FALLBACKS)
    assert all("realtime" not in m for m in catalog.OPENAI_MODEL_FALLBACKS)
    assert all("image" not in m for m in catalog.GEMINI_MODEL_FALLBACKS)
    assert all("tts" not in m for m in catalog.GEMINI_MODEL_FALLBACKS)
    assert all("multi-agent" not in m for m in catalog.GROK_MODEL_FALLBACKS)


def test_fallbacks_capped_and_prefer_defaults() -> None:
    assert len(catalog.OPENAI_MODEL_FALLBACKS) <= catalog._FALLBACK_CAP
    assert len(catalog.GEMINI_MODEL_FALLBACKS) <= catalog._FALLBACK_CAP
    assert len(catalog.GROK_MODEL_FALLBACKS) <= catalog._FALLBACK_CAP
    assert catalog.DEFAULT_OPENAI_MODEL == "gpt-5.6-luna"
    assert catalog.DEFAULT_GEMINI_MODEL == "gemini-3.1-flash-lite"
    assert catalog.DEFAULT_GROK_MODEL == "grok-4.6"


def test_model_candidates_preferred_first() -> None:
    got = catalog.model_candidates(
        "gpt-4o",
        ("gpt-5.6-luna", "gpt-4o-mini", "gpt-4o"),
    )
    assert got[0] == "gpt-4o"
    assert got == ["gpt-4o", "gpt-5.6-luna", "gpt-4o-mini"]


def test_parse_custom_modelos(tmp_path: Path) -> None:
    path = tmp_path / "Modelos.txt"
    path.write_text(
        "GPT\ngpt-a\ngpt-image-1\n\nGemini\ngemini-x\ngemini-x-image\n\nGrok\ngrok-y\n",
        encoding="utf-8",
    )
    parsed = catalog.load_catalogs(path)
    assert parsed["GPT"] == ("gpt-a", "gpt-image-1")
    assert parsed["Gemini"] == ("gemini-x", "gemini-x-image")
    assert parsed["Grok"] == ("grok-y",)
    openai_fb = catalog._capped(
        catalog._filter_exclude(parsed["GPT"], catalog._OPENAI_EXCLUDE_PARTS)
    )
    assert openai_fb == ("gpt-a",)
