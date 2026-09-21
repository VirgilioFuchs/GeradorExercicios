"""LLM_MODEL env is honored by generate_exercises when model arg is omitted."""

from __future__ import annotations

from unittest.mock import patch

from models import Exercise, ExerciseBatch, GenerationRequest


def test_generate_exercises_reads_llm_model_env(monkeypatch) -> None:
    import generator

    batch = ExerciseBatch(
        exercicios=[Exercise(enunciado="1", resposta="1", explicacao="1")]
    )
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("LLM_API_KEY", "sk-test")

    with patch.object(generator, "_generate_with_openai", return_value=batch) as mock_oai:
        out = generator.generate_exercises(
            GenerationRequest(
                materia="Matemática",
                topico="soma",
                dificuldade="facil",
                quantidade=1,
            )
        )
        assert out is batch
        assert mock_oai.call_args.kwargs["model"] == "gpt-4o-mini"
