"""Mocked reliability loop: retries, resolve_max_retries, duration aggregate."""

from __future__ import annotations

import contextlib
import io
import json
from unittest.mock import patch

import pytest
from models import DificuldadeEnum, Exercise, ExerciseBatch, GenerationRequest

import reliability
import main


@pytest.fixture
def demo_batch():
    return ExerciseBatch(
        exercicios=[
            Exercise(enunciado="e1", resposta="r1", explicacao="x1"),
            Exercise(enunciado="e2", resposta="r2", explicacao="x2"),
            Exercise(enunciado="e3", resposta="r3", explicacao="x3"),
        ]
    )


@pytest.fixture
def request_demo():
    return GenerationRequest(
        materia="Matemática",
        topico="Equação do primeiro grau",
        dificuldade=DificuldadeEnum.FACIL,
        quantidade=3,
    )


def test_resolve_cli_overrides_env(monkeypatch):
    monkeypatch.setenv("RELY_MAX_RETRIES", "2")
    assert reliability.resolve_max_retries(0) == 0
    assert reliability.resolve_max_retries(3) == 3


def test_resolve_missing_env_defaults_to_one(monkeypatch):
    monkeypatch.delenv("RELY_MAX_RETRIES", raising=False)
    assert reliability.resolve_max_retries(None) == 1


def test_resolve_env_value(monkeypatch):
    monkeypatch.setenv("RELY_MAX_RETRIES", "2")
    assert reliability.resolve_max_retries(None) == 2


def test_resolve_invalid_env_raises(monkeypatch):
    monkeypatch.setenv("RELY_MAX_RETRIES", "9")
    with pytest.raises(ValueError, match="max-retries inválido"):
        reliability.resolve_max_retries(None)
    monkeypatch.setenv("RELY_MAX_RETRIES", "abc")
    with pytest.raises(ValueError, match="max-retries inválido"):
        reliability.resolve_max_retries(None)


def test_resolve_invalid_cli_raises(monkeypatch):
    monkeypatch.delenv("RELY_MAX_RETRIES", raising=False)
    with pytest.raises(ValueError, match="max-retries inválido"):
        reliability.resolve_max_retries(4)


def test_validation_fail_once_then_success(demo_batch, request_demo, tmp_path):
    """Validation fails once then succeeds → 2 LLM calls + regen label + --out."""
    out_path = tmp_path / "batch.json"
    bad = ExerciseBatch(
        exercicios=[Exercise(enunciado="e1", resposta="", explicacao="x1")]
    )
    calls = {"n": 0}

    def fake_gen(_req):
        calls["n"] += 1
        return bad if calls["n"] == 1 else demo_batch

    out, err = io.StringIO(), io.StringIO()
    with patch.object(reliability, "generate_exercises", side_effect=fake_gen) as gen:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            main.run(request_demo, out_path=out_path, max_retries=1)
    assert gen.call_count == 2
    stderr = err.getvalue()
    assert "1ª Regeneração" in stderr
    assert "Gerando" in stderr and "Validando" in stderr
    assert "chamadas=2" in stderr
    assert "total_ms=" in stderr
    assert "### Exercício 1" in out.getvalue()
    assert out_path.exists()
    parsed = json.loads(out_path.read_text(encoding="utf-8"))
    assert len(parsed["exercicios"]) == 3


def test_math_fail_once_then_success(request_demo, tmp_path):
    """Structurally OK but math-wrong once, then correct → regen via RELY (MATH-02)."""
    out_path = tmp_path / "batch.json"
    wrong = ExerciseBatch(
        exercicios=[
            Exercise(enunciado="2 + 2 = ?", resposta="5", explicacao="errado"),
            Exercise(enunciado="3 + 1 = ?", resposta="4", explicacao="ok"),
            Exercise(enunciado="1 + 1 = ?", resposta="2", explicacao="ok"),
        ]
    )
    good = ExerciseBatch(
        exercicios=[
            Exercise(enunciado="2 + 2 = ?", resposta="4", explicacao="ok"),
            Exercise(enunciado="3 + 1 = ?", resposta="4", explicacao="ok"),
            Exercise(enunciado="1 + 1 = ?", resposta="2", explicacao="ok"),
        ]
    )
    calls = {"n": 0}

    def fake_gen(_req):
        calls["n"] += 1
        return wrong if calls["n"] == 1 else good

    out, err = io.StringIO(), io.StringIO()
    with patch.object(reliability, "generate_exercises", side_effect=fake_gen) as gen:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            main.run(request_demo, out_path=out_path, max_retries=1)
    assert gen.call_count == 2
    stderr = err.getvalue()
    assert "1ª Regeneração" in stderr
    assert "[MATH]" in stderr
    assert out_path.exists()
    assert "### Exercício 1" in out.getvalue()


def test_max_retries_zero_fail_fast(request_demo, tmp_path):
    out_path = tmp_path / "batch.json"
    bad = ExerciseBatch(
        exercicios=[Exercise(enunciado="e1", resposta="", explicacao="x1")]
    )
    out, err = io.StringIO(), io.StringIO()
    with patch.object(reliability, "generate_exercises", return_value=bad) as gen:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with pytest.raises(SystemExit) as se:
                main.run(request_demo, out_path=out_path, max_retries=0)
    assert se.value.code == 1
    assert gen.call_count == 1
    stderr = err.getvalue()
    assert "1ª Regeneração" not in stderr
    assert "resposta" in stderr.lower() or "vazio" in stderr.lower()
    assert "chamadas=1" in stderr
    assert out.getvalue() == ""
    assert not out_path.exists()


def test_exhaustion_default_one_retry(request_demo, tmp_path):
    out_path = tmp_path / "batch.json"
    bad = ExerciseBatch(
        exercicios=[Exercise(enunciado="e1", resposta="", explicacao="x1")]
    )
    out, err = io.StringIO(), io.StringIO()
    with patch.object(reliability, "generate_exercises", return_value=bad) as gen:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with pytest.raises(SystemExit) as se:
                main.run(request_demo, out_path=out_path, max_retries=1)
    assert se.value.code == 1
    assert gen.call_count == 2
    stderr = err.getvalue()
    assert "1ª Regeneração" in stderr
    assert "chamadas=2" in stderr
    assert "total_ms=" in stderr
    # Final PT reason once (validation message present)
    assert "resposta" in stderr.lower() or "vazio" in stderr.lower()
    assert out.getvalue() == ""
    assert not out_path.exists()


def test_unmarked_runtime_error_no_retry(request_demo, tmp_path):
    """Unmarked RuntimeError fails through (permanent until ERR-05 markers)."""
    out_path = tmp_path / "batch.json"
    out, err = io.StringIO(), io.StringIO()
    with patch.object(
        reliability,
        "generate_exercises",
        side_effect=RuntimeError("Erro na chamada à API da OpenAI."),
    ) as gen:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with pytest.raises(SystemExit) as se:
                main.run(request_demo, out_path=out_path, max_retries=2)
    assert se.value.code == 1
    assert gen.call_count == 1
    assert "1ª Regeneração" not in err.getvalue()
    assert not out_path.exists()


def test_retriable_invalid_response_then_success(demo_batch, request_demo, tmp_path):
    """Invalid LLM response once then success → regen + call_count == 2."""
    out_path = tmp_path / "batch.json"
    retriable = RuntimeError("estrutura ausente")
    retriable.retriable = True
    effects = [retriable, demo_batch]
    out, err = io.StringIO(), io.StringIO()
    with patch.object(reliability, "generate_exercises", side_effect=effects) as gen:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            main.run(request_demo, out_path=out_path, max_retries=1)
    assert gen.call_count == 2
    assert gen.call_count <= 1 + 1
    stderr = err.getvalue()
    assert "1ª Regeneração" in stderr
    assert "chamadas=2" in stderr
    assert out_path.exists()
    assert "### Exercício 1" in out.getvalue()


def test_permanent_auth_no_regen(request_demo, tmp_path):
    """Permanent auth RuntimeError → call_count == 1, no regen label."""
    out_path = tmp_path / "batch.json"
    auth = RuntimeError("Falha de autenticação na API da OpenAI. Verifique LLM_API_KEY.")
    auth.retriable = False
    out, err = io.StringIO(), io.StringIO()
    with patch.object(reliability, "generate_exercises", side_effect=auth) as gen:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with pytest.raises(SystemExit) as se:
                main.run(request_demo, out_path=out_path, max_retries=3)
    assert se.value.code == 1
    assert gen.call_count == 1
    assert gen.call_count <= 1 + 3
    assert "1ª Regeneração" not in err.getvalue()
    assert "autentic" in err.getvalue().lower()
    assert not out_path.exists()
