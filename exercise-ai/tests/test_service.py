"""Tracer: host path returns batch / raises without process exit."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from models import DificuldadeEnum, Exercise, ExerciseBatch, GenerationRequest

import service


def _fixture_batch() -> ExerciseBatch:
    return ExerciseBatch(
        exercicios=[
            Exercise(enunciado="1+1", resposta="2", explicacao="soma"),
        ]
    )


def _fixture_request() -> GenerationRequest:
    return GenerationRequest(
        materia="Matemática",
        topico="soma",
        dificuldade=DificuldadeEnum.FACIL,
        quantidade=1,
    )


def test_generate_batch_returns_batch_without_stdout_dump(capsys):
    batch = _fixture_batch()
    with patch.object(service, "generate_with_failover", return_value=batch) as gen:
        with patch.object(service, "resolve_max_retries", return_value=0):
            with patch.object(service, "begin_run"):
                with patch.object(service, "flush_token_usage"):
                    result = service.generate_batch(_fixture_request())
    assert isinstance(result, ExerciseBatch)
    assert result is batch
    assert gen.call_count == 1
    out = capsys.readouterr().out
    assert "### Exercício" not in out
    assert "Enunciado:" not in out


@pytest.mark.parametrize(
    "exc",
    [
        ValueError("config inválida"),
        RuntimeError("geração falhou"),
    ],
)
def test_generate_batch_raises_normal_exception(exc):
    with patch.object(service, "generate_with_failover", side_effect=exc):
        with patch.object(service, "resolve_max_retries", return_value=0):
            with patch.object(service, "begin_run"):
                with patch.object(service, "flush_token_usage"):
                    with pytest.raises(Exception) as caught:
                        service.generate_batch(_fixture_request())
    assert caught.value is exc
    assert not isinstance(caught.value, BaseException) or isinstance(
        caught.value, Exception
    )
    # Library path must not require catching BaseException (no SystemExit).
    assert not isinstance(caught.value, SystemExit)


def test_service_source_does_not_import_main():
    src = Path("exercise-ai/service.py").read_text(encoding="utf-8")
    assert "import main" not in src
    assert "from main" not in src


def test_run_still_writes_out_and_exits_on_failure(tmp_path, monkeypatch, capsys):
    """CLI adapter keeps presentation/exit after service delegation."""
    import main as main_mod

    batch = _fixture_batch()
    out_path = tmp_path / "out.json"
    monkeypatch.setattr(main_mod, "generate_batch", lambda req: batch)
    main_mod.run(_fixture_request(), out_path=out_path, max_retries=0)
    assert out_path.is_file()
    assert "### Exercício" in capsys.readouterr().out

    def boom(_req):
        raise ValueError("falha tracer")

    monkeypatch.setattr(main_mod, "generate_batch", boom)
    with pytest.raises(SystemExit) as se:
        main_mod.run(_fixture_request(), out_path=tmp_path / "x.json", max_retries=0)
    assert se.value.code == 1


def test_config_error_kind_missing_key(monkeypatch):
    """Host can discriminate ConfigError via isinstance + .kind (D-03/D-04)."""
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GROK_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "openai")

    import generator

    with pytest.raises(service.ConfigError) as caught:
        generator.get_client()
    assert caught.value.kind == "missing_key"
    assert isinstance(caught.value, ValueError)


def test_validation_exhaustion_raises_invalid_request_error():
    """Reliability final failure is InvalidRequestError with kind (EMBED-02)."""
    bad = ExerciseBatch(
        exercicios=[Exercise(enunciado="e1", resposta="", explicacao="x1")]
    )
    import reliability

    with patch.object(reliability, "generate_exercises", return_value=bad):
        with pytest.raises(service.InvalidRequestError) as caught:
            reliability.generate_validated_batch(_fixture_request(), max_retries=0)
    assert caught.value.kind == "validation_exhausted"
    assert isinstance(caught.value, ValueError)
