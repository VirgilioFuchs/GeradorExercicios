"""LOG-02 anti-leakage: dummy API key values must never appear in stderr."""

from __future__ import annotations

import contextlib
import io
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from models import DificuldadeEnum, GenerationRequest

import generator
import generator_gemini
import main


DUMMY_LLM_KEY = "sk-TEST-LEAK-LLM-KEY-9f3a2b1c"
DUMMY_GEMINI_KEY = "AIzaSy-TEST-LEAK-GEMINI-KEY-7d4e"
DUMMY_GROK_KEY = "xai-TEST-LEAK-GROK-KEY-4c8e"


def test_openai_mapper_auth_stderr_never_contains_key(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", DUMMY_LLM_KEY)
    monkeypatch.setenv("GEMINI_API_KEY", DUMMY_GEMINI_KEY)

    class _AuthLeak(Exception):
        """Simulates provider body that embeds the API key."""

        def __str__(self) -> str:
            return f"Invalid API key: {DUMMY_LLM_KEY}"

    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        err = generator.map_openai_error(_AuthLeak())
    stderr = buf.getvalue()
    assert "[API:openai]" in stderr
    assert DUMMY_LLM_KEY not in stderr
    assert DUMMY_GEMINI_KEY not in stderr
    assert DUMMY_LLM_KEY not in str(err)
    # User message may name the env var, never the value
    assert "LLM_API_KEY" in str(err) or "OpenAI" in str(err)


def test_gemini_mapper_auth_stderr_never_contains_key(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", DUMMY_LLM_KEY)
    monkeypatch.setenv("GEMINI_API_KEY", DUMMY_GEMINI_KEY)

    class _GemLeak:
        status_code = 401
        message = f"API key {DUMMY_GEMINI_KEY} rejected"

        def __str__(self) -> str:
            return self.message

    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        err = generator_gemini.map_gemini_error(_GemLeak())
    stderr = buf.getvalue()
    assert "[API:gemini]" in stderr
    assert DUMMY_LLM_KEY not in stderr
    assert DUMMY_GEMINI_KEY not in stderr
    assert DUMMY_GEMINI_KEY not in str(err)


def test_grok_mapper_auth_stderr_never_contains_key(monkeypatch):
    monkeypatch.setenv("GROK_API_KEY", DUMMY_GROK_KEY)
    monkeypatch.setenv("LLM_API_KEY", DUMMY_LLM_KEY)

    class _AuthLeak(Exception):
        def __str__(self) -> str:
            return f"Invalid API key: {DUMMY_GROK_KEY}"

    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        err = generator.map_openai_compatible_error(
            _AuthLeak(),
            api_tag="grok",
            of_label="do Grok",
            auth_key_name="GROK_API_KEY",
        )
    stderr = buf.getvalue()
    assert "[API:grok]" in stderr
    assert DUMMY_GROK_KEY not in stderr
    assert DUMMY_LLM_KEY not in stderr
    assert DUMMY_GROK_KEY not in str(err)
    assert "GROK_API_KEY" in str(err) or "Grok" in str(err)


def test_grok_refusal_redacts_key(monkeypatch):
    monkeypatch.setenv("GROK_API_KEY", DUMMY_GROK_KEY)
    req = GenerationRequest(topico="x", dificuldade=DificuldadeEnum.FACIL, quantidade=1)
    message = MagicMock()
    message.refusal = f"key leak {DUMMY_GROK_KEY}"
    message.parsed = None
    choice = MagicMock()
    choice.message = message
    completion = MagicMock()
    completion.choices = [choice]
    client = MagicMock()
    client.beta.chat.completions.parse.return_value = completion
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(RuntimeError):
            with patch.object(generator, "get_grok_client", return_value=client):
                generator._generate_with_grok(req)
    assert DUMMY_GROK_KEY not in buf.getvalue()
    assert "[API:grok]" in buf.getvalue()


def test_gemini_unparseable_redacts_key_in_response(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", DUMMY_GEMINI_KEY)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    req = GenerationRequest(topico="x", dificuldade=DificuldadeEnum.FACIL, quantidade=1)
    fake_client = MagicMock()
    fake_resp = MagicMock()
    fake_resp.text = f'{{"leak": "{DUMMY_GEMINI_KEY}"'
    fake_client.models.generate_content.return_value = fake_resp
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(RuntimeError):
            with patch.object(generator_gemini, "get_client", return_value=fake_client):
                generator_gemini.generate_exercises(req)
    assert DUMMY_GEMINI_KEY not in buf.getvalue()
    assert "[API:gemini]" in buf.getvalue()


def test_run_failure_logs_omit_key_values(monkeypatch, tmp_path):
    monkeypatch.setenv("LLM_API_KEY", DUMMY_LLM_KEY)
    monkeypatch.setenv("GEMINI_API_KEY", DUMMY_GEMINI_KEY)
    from models import DificuldadeEnum, GenerationRequest

    import reliability

    request = GenerationRequest(
        materia="Matemática",
        topico="Equação do primeiro grau",
        dificuldade=DificuldadeEnum.FACIL,
        quantidade=3,
    )
    out, err = io.StringIO(), io.StringIO()
    with patch.object(
        reliability,
        "generate_exercises",
        side_effect=ValueError("quantidade incorreta: esperado 3 exercícios, recebido 1"),
    ):
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with pytest.raises(SystemExit):
                main.run(request, out_path=tmp_path / "out.json", max_retries=0)
    combined = err.getvalue()
    assert DUMMY_LLM_KEY not in combined
    assert DUMMY_GEMINI_KEY not in combined
    assert "quantidade incorreta" in combined or "Falha" in combined
    assert "chamadas=" in combined
    assert "total_ms=" in combined


def test_duration_aggregate_never_contains_keys(monkeypatch, tmp_path):
    monkeypatch.setenv("LLM_API_KEY", DUMMY_LLM_KEY)
    monkeypatch.setenv("GEMINI_API_KEY", DUMMY_GEMINI_KEY)
    import reliability
    from models import Exercise, ExerciseBatch

    batch = ExerciseBatch(
        exercicios=[Exercise(enunciado="e1", resposta="r1", explicacao="x1")]
    )
    request = GenerationRequest(
        materia="Matemática",
        topico="t",
        dificuldade=DificuldadeEnum.FACIL,
        quantidade=1,
    )
    err = io.StringIO()
    with patch.object(reliability, "generate_exercises", return_value=batch):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            main.run(request, out_path=tmp_path / "ok.json", max_retries=0)
    combined = err.getvalue()
    assert "chamadas=1" in combined
    assert "total_ms=" in combined
    assert DUMMY_LLM_KEY not in combined
    assert DUMMY_GEMINI_KEY not in combined
