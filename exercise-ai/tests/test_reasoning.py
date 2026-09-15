"""Unit tests for unified reasoning / thinking effort (offline)."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest
from models import DificuldadeEnum, Exercise, ExerciseBatch, GenerationRequest

import generator
import generator_gemini
import reasoning


def test_resolve_reasoning_default_low(monkeypatch):
    monkeypatch.delenv("LLM_REASONING_EFFORT", raising=False)
    assert reasoning.resolve_reasoning_effort() == "low"


def test_resolve_reasoning_env_and_explicit(monkeypatch):
    monkeypatch.setenv("LLM_REASONING_EFFORT", "high")
    assert reasoning.resolve_reasoning_effort() == "high"
    assert reasoning.resolve_reasoning_effort("medium") == "medium"


def test_resolve_reasoning_invalid():
    with pytest.raises(ValueError, match="reasoning inválido"):
        reasoning.resolve_reasoning_effort("turbo")


def test_gemini_map_none_to_minimal():
    assert reasoning.to_gemini_thinking_level("none") == "minimal"
    assert reasoning.to_gemini_thinking_level("low") == "low"


def test_openai_supports_gate():
    assert reasoning.openai_supports_reasoning_effort("gpt-4o-mini") is False
    assert reasoning.openai_supports_reasoning_effort("gpt-5-mini") is True
    assert reasoning.openai_supports_reasoning_effort("o3-mini") is True


def test_openai_compatible_kwargs_grok_always(monkeypatch):
    monkeypatch.delenv("LLM_REASONING_EFFORT", raising=False)
    kw = reasoning.openai_compatible_effort_kwargs(
        api_tag="grok", model="grok-4.6"
    )
    assert kw == {"reasoning_effort": "low"}


def test_openai_compatible_kwargs_openai_omit_gpt4o(monkeypatch, capsys):
    monkeypatch.setenv("LLM_REASONING_EFFORT", "low")
    kw = reasoning.openai_compatible_effort_kwargs(
        api_tag="openai", model="gpt-4o-mini"
    )
    assert kw == {}
    err = capsys.readouterr().err
    assert "reasoning_effort não suportado" in err
    assert "gpt-4o-mini" in err


def test_openai_compatible_kwargs_openai_allowlisted(monkeypatch):
    monkeypatch.setenv("LLM_REASONING_EFFORT", "medium")
    kw = reasoning.openai_compatible_effort_kwargs(
        api_tag="openai", model="gpt-5-mini"
    )
    assert kw == {"reasoning_effort": "medium"}


def test_grok_parse_receives_reasoning_effort(monkeypatch):
    monkeypatch.setenv("GROK_API_KEY", "dummy")
    monkeypatch.setenv("LLM_REASONING_EFFORT", "low")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    batch = ExerciseBatch(
        exercicios=[
            Exercise(enunciado="1+1", resposta="2", explicacao="soma")
        ]
    )
    message = MagicMock()
    message.refusal = None
    message.parsed = batch
    completion = MagicMock()
    completion.choices = [MagicMock(message=message)]
    completion.usage = None

    client = MagicMock()
    client.beta.chat.completions.parse.return_value = completion

    req = GenerationRequest(
        topico="x", dificuldade=DificuldadeEnum.FACIL, quantidade=1
    )
    with patch.object(generator, "get_grok_client", return_value=client):
        out = generator._generate_with_grok(req)

    assert out is batch
    kwargs = client.beta.chat.completions.parse.call_args.kwargs
    assert kwargs.get("reasoning_effort") == "low"


def test_openai_parse_omits_reasoning_for_gpt4o_mini(monkeypatch, capsys):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    monkeypatch.setenv("LLM_REASONING_EFFORT", "low")

    batch = ExerciseBatch(
        exercicios=[
            Exercise(enunciado="1+1", resposta="2", explicacao="soma")
        ]
    )
    message = MagicMock()
    message.refusal = None
    message.parsed = batch
    completion = MagicMock()
    completion.choices = [MagicMock(message=message)]
    completion.usage = None

    client = MagicMock()
    client.beta.chat.completions.parse.return_value = completion

    req = GenerationRequest(
        topico="x", dificuldade=DificuldadeEnum.FACIL, quantidade=1
    )
    with patch.object(generator, "get_client", return_value=client):
        generator._generate_with_openai(req, model="gpt-4o-mini")

    kwargs = client.beta.chat.completions.parse.call_args.kwargs
    assert "reasoning_effort" not in kwargs


def test_gemini_config_includes_thinking_level(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AIza-test")
    monkeypatch.setenv("LLM_REASONING_EFFORT", "low")
    monkeypatch.setattr(
        generator_gemini,
        "GEMINI_MODEL_FALLBACKS",
        ("gemini-3.1-flash-lite",),
    )

    batch = ExerciseBatch(
        exercicios=[
            Exercise(enunciado="1+1", resposta="2", explicacao="soma")
        ]
    )
    response = MagicMock()
    response.text = batch.model_dump_json()
    response.parsed = None
    response.usage_metadata = None

    client = MagicMock()
    client.models.generate_content.return_value = response

    req = GenerationRequest(
        topico="x", dificuldade=DificuldadeEnum.FACIL, quantidade=1
    )
    with patch.object(generator_gemini, "get_client", return_value=client):
        generator_gemini.generate_exercises(req)

    config = client.models.generate_content.call_args.kwargs["config"]
    assert config.thinking_config is not None
    level = config.thinking_config.thinking_level
    # SDK may normalize to enum; compare string form
    assert str(level).lower().endswith("low") or level == "low"


def test_cli_reasoning_sets_env(tmp_path, monkeypatch):
    import main as main_mod

    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    out = tmp_path / "o.json"
    captured: dict[str, str] = {}

    def fake_run(request, out_path, max_retries=None):
        captured["effort"] = os.environ.get("LLM_REASONING_EFFORT", "")
        __import__("pathlib").Path(out_path).write_text("{}", encoding="utf-8")

    monkeypatch.setattr(main_mod, "run", fake_run)
    main_mod.main(
        ["--reasoning", "high", "--out", str(out), "--provider", "openai"]
    )
    assert captured["effort"] == "high"
