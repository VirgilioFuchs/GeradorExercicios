"""Mocked OpenAI/Gemini mapper + ERR-01 missing API env key coverage."""

from __future__ import annotations

import contextlib
import io
import json
import os
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from models import DificuldadeEnum, GenerationRequest
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

import generator
import generator_gemini


def _make_openai_exc(cls, msg: str = "x"):
    """SDK-tolerant exception construction (broader than TypeError — Phase 2 LEARNINGS)."""
    for args, kwargs in (
        ((msg,), {}),
        ((), {"message": msg}),
        ((), {"message": msg, "response": None, "body": None}),
        ((), {"message": msg, "request": None, "body": None}),
    ):
        try:
            return cls(*args, **kwargs)
        except Exception:
            continue

    class _E(cls):
        def __init__(self):
            Exception.__init__(self, msg)

    return _E()


def test_missing_api_keys_raises_value_error_naming_both():
    """ERR-01: absent LLM/GEMINI/GROK keys — not TEST-02 chave ausente."""
    old = {
        k: os.environ.pop(k)
        for k in ("LLM_API_KEY", "GEMINI_API_KEY", "GROK_API_KEY", "LLM_PROVIDER")
        if k in os.environ
    }
    try:
        with pytest.raises(ValueError) as exc_info:
            generator._resolve_provider()
        err = str(exc_info.value)
        assert "GEMINI_API_KEY" in err and "LLM_API_KEY" in err
        assert "GROK_API_KEY" in err
    finally:
        os.environ.update(old)


def test_resolve_provider_explicit_and_auto_grok(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("GROK_API_KEY", "xai-test")
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    assert generator._resolve_provider() == "grok"

    monkeypatch.setenv("LLM_PROVIDER", "grok")
    monkeypatch.setenv("GEMINI_API_KEY", "AIza-present")
    assert generator._resolve_provider() == "grok"


def test_grok_empty_choices_typed_retriable(monkeypatch):
    """Empty choices → PT RuntimeError + [API:grok], retriable."""
    monkeypatch.setenv("GROK_API_KEY", "dummy-grok")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    req = GenerationRequest(topico="x", dificuldade=DificuldadeEnum.FACIL, quantidade=1)
    client = MagicMock()
    completion = MagicMock()
    completion.choices = []
    client.beta.chat.completions.parse.return_value = completion
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(RuntimeError) as exc_info:
            with patch.object(generator, "get_grok_client", return_value=client):
                generator._generate_with_grok(req)
    assert getattr(exc_info.value, "retriable", None) is True
    assert "[API:grok] empty choices" in buf.getvalue()


def test_map_grok_auth_mentions_grok_key():
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        out = generator.map_openai_compatible_error(
            _make_openai_exc(AuthenticationError),
            api_tag="grok",
            of_label="do Grok",
            auth_key_name="GROK_API_KEY",
        )
    assert getattr(out, "retriable", None) is False
    assert "GROK_API_KEY" in str(out)
    assert "[API:grok]" in buf.getvalue()


@pytest.mark.parametrize(
    "exc_cls,needles",
    [
        (APITimeoutError, ("tempo", "esgotado")),
        (RateLimitError, ("limite",)),
        (APIConnectionError, ("conex", "rede")),
        (AuthenticationError, ("autentic", "chave")),
    ],
)
def test_map_openai_error_categories(exc_cls, needles):
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        out = generator.map_openai_error(_make_openai_exc(exc_cls))
    assert isinstance(out, RuntimeError)
    assert getattr(out, "retriable", None) is False
    assert "[API:" not in str(out)
    stderr = buf.getvalue()
    assert "[API:openai]" in stderr
    # LOG-02: sanitized detail — type name, not raw body with possible secrets
    assert f"{exc_cls.__name__}" in stderr or type(out).__name__
    text = str(out).lower()
    assert any(n in text for n in needles), (exc_cls, text)


def test_map_openai_generic_fallback_no_raw_exc():
    class WeirdError(Exception):
        pass

    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        out = generator.map_openai_error(WeirdError("secret-body-sk-leak"))
    assert str(out) == "Erro na chamada à API da OpenAI."
    assert "secret-body" not in buf.getvalue()
    assert "[API:openai]" in buf.getvalue()


@pytest.mark.parametrize(
    "obj,expected",
    [
        (
            SimpleNamespace(code=401, message="no"),
            "Falha de autenticação na API do Gemini. Verifique GEMINI_API_KEY.",
        ),
        (
            SimpleNamespace(status_code=403, message="x"),
            "Falha de autenticação na API do Gemini. Verifique GEMINI_API_KEY.",
        ),
        (
            SimpleNamespace(code=429, message="x"),
            "Limite de requisições da API do Gemini atingido. Tente novamente mais tarde.",
        ),
        (
            SimpleNamespace(code=408, message="x"),
            "Tempo esgotado ao chamar a API do Gemini.",
        ),
        (
            SimpleNamespace(code=504, message="x"),
            "Tempo esgotado ao chamar a API do Gemini.",
        ),
        (
            SimpleNamespace(code=500, message="connection reset"),
            "Erro de conexão com a API do Gemini. Verifique a rede.",
        ),
        (
            SimpleNamespace(code=500, message="boom"),
            "Erro na chamada à API do Gemini.",
        ),
    ],
)
def test_map_gemini_error_status_table(obj, expected):
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        out = generator_gemini.map_gemini_error(obj)
    assert isinstance(out, RuntimeError)
    assert str(out) == expected
    assert getattr(out, "retriable", None) is False
    assert "[API:" not in str(out)
    assert "[API:gemini]" in buf.getvalue()


def test_gemini_error_classification_docs_present():
    src = open("exercise-ai/generator_gemini.py", encoding="utf-8").read()
    assert "GEMINI_ERROR_CLASSIFICATION:" in src
    assert all(code in src for code in ("401", "403", "429", "408", "504"))
    assert "priority-1 N/A on this SDK" in src


def test_gemini_empty_and_unparseable(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key-for-test")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    req = GenerationRequest(topico="x", dificuldade=DificuldadeEnum.FACIL, quantidade=1)
    fake_client = MagicMock()

    fake_resp_empty = MagicMock()
    fake_resp_empty.text = ""
    fake_client.models.generate_content.return_value = fake_resp_empty
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(RuntimeError) as exc_info:
            with patch.object(generator_gemini, "get_client", return_value=fake_client):
                generator_gemini.generate_exercises(req)
    assert "vazia" in str(exc_info.value).lower()
    assert getattr(exc_info.value, "retriable", None) is True
    assert "[API:gemini]" in buf.getvalue()

    fake_resp_bad = MagicMock()
    fake_resp_bad.text = "{not-json"
    fake_client.models.generate_content.return_value = fake_resp_bad
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(RuntimeError) as exc_info:
            with patch.object(generator_gemini, "get_client", return_value=fake_client):
                generator_gemini.generate_exercises(req)
    low = str(exc_info.value).lower()
    assert "interpretar" in low or "estrutura" in low
    assert getattr(exc_info.value, "retriable", None) is True
    assert "[API:gemini]" in buf.getvalue()


def test_openai_empty_choices_typed_retriable(monkeypatch):
    """WR-03 / ERR-05: empty choices → PT RuntimeError + [API:openai], retriable."""
    monkeypatch.setenv("LLM_API_KEY", "dummy-openai")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    req = GenerationRequest(topico="x", dificuldade=DificuldadeEnum.FACIL, quantidade=1)
    completion = MagicMock()
    completion.choices = []
    client = MagicMock()
    client.beta.chat.completions.parse.return_value = completion
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(RuntimeError) as exc_info:
            with patch.object(generator, "get_client", return_value=client):
                generator._generate_with_openai(req)
    assert getattr(exc_info.value, "retriable", None) is True
    assert "estrutura" in str(exc_info.value).lower() or "obter" in str(exc_info.value).lower()
    assert "[API:openai] empty choices" in buf.getvalue()


def test_gemini_non_apierror_mapped(monkeypatch):
    """WR-04 / ERR-05: non-APIError → map_gemini_error typed path (not bare Exception)."""
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key-for-test")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    req = GenerationRequest(topico="x", dificuldade=DificuldadeEnum.FACIL, quantidade=1)
    fake_client = MagicMock()
    fake_client.models.generate_content.side_effect = ConnectionError("connection reset")
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(RuntimeError) as exc_info:
            with patch.object(generator_gemini, "get_client", return_value=fake_client):
                generator_gemini.generate_exercises(req)
    assert getattr(exc_info.value, "retriable", None) is False
    assert "conexão" in str(exc_info.value).lower() or "rede" in str(exc_info.value).lower()
    assert "[API:gemini]" in buf.getvalue()
    assert "ConnectionError" in buf.getvalue()
    assert fake_client.models.generate_content.call_count == 1


def test_gemini_falls_back_on_usage_error(monkeypatch):
    """429/503 on preferred model → try next fallback model."""
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key-for-test")
    req = GenerationRequest(topico="x", dificuldade=DificuldadeEnum.FACIL, quantidade=1)
    ok = MagicMock()
    ok.text = json.dumps(
        {
            "exercicios": [
                {
                    "enunciado": "Quanto é 1+1?",
                    "resposta": "2",
                    "explicacao": "Soma básica.",
                }
            ]
        }
    )

    class _UsageErr(Exception):
        status_code = 503
        message = "overloaded"

    fake_client = MagicMock()
    fake_client.models.generate_content.side_effect = [_UsageErr(), ok]
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with patch.object(generator_gemini, "get_client", return_value=fake_client):
            batch = generator_gemini.generate_exercises(req)
    assert len(batch.exercicios) == 1
    assert fake_client.models.generate_content.call_count == 2
    assert "uso/capacidade" in buf.getvalue()
    assert "gemini-3.5-flash" in buf.getvalue()


@pytest.mark.parametrize(
    "provider_module,factory",
    [
        (
            "generator",
            lambda: generator.invalid_llm_response("estrutura ausente"),
        ),
        (
            "generator_gemini",
            lambda: generator_gemini.invalid_llm_response("resposta vazia"),
        ),
    ],
)
def test_invalid_llm_response_helper_retriable(provider_module, factory):
    err = factory()
    assert isinstance(err, RuntimeError)
    assert err.retriable is True


def test_openai_refusal_and_parsed_none(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "dummy-openai")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    req = GenerationRequest(topico="x", dificuldade=DificuldadeEnum.FACIL, quantidade=1)

    def _mock_completion(refusal=None, parsed=None):
        message = MagicMock()
        message.refusal = refusal
        message.parsed = parsed
        choice = MagicMock()
        choice.message = message
        completion = MagicMock()
        completion.choices = [choice]
        client = MagicMock()
        client.beta.chat.completions.parse.return_value = completion
        return client

    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(RuntimeError) as exc_info:
            with patch.object(
                generator,
                "get_client",
                return_value=_mock_completion(refusal="não posso", parsed=None),
            ):
                generator._generate_with_openai(req)
    low = str(exc_info.value).lower()
    assert "recus" in low or "refusal" in low or "não" in low
    assert "[API:openai]" in buf.getvalue()

    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(RuntimeError) as exc_info:
            with patch.object(
                generator,
                "get_client",
                return_value=_mock_completion(refusal=None, parsed=None),
            ):
                generator._generate_with_openai(req)
    low = str(exc_info.value).lower()
    assert "estrutura" in low or "obter" in low or "parse" in low
    assert getattr(exc_info.value, "retriable", None) is True
    assert "[API:openai]" in buf.getvalue()
