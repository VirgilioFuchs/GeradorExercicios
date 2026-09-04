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


def test_run_demo_failure_logs_omit_key_values(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", DUMMY_LLM_KEY)
    monkeypatch.setenv("GEMINI_API_KEY", DUMMY_GEMINI_KEY)
    out, err = io.StringIO(), io.StringIO()
    with patch.object(
        main,
        "generate_exercises",
        side_effect=ValueError("quantidade incorreta: esperado 3 exercícios, recebido 1"),
    ):
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with pytest.raises(SystemExit):
                main.run_demo()
    combined = err.getvalue()
    assert DUMMY_LLM_KEY not in combined
    assert DUMMY_GEMINI_KEY not in combined
    assert "quantidade incorreta" in combined or "Falha" in combined
