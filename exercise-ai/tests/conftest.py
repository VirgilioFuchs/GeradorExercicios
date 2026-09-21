"""Pytest fixtures and path grounding for exercise-ai tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Align imports with Phase 2 verifies: package modules live in exercise-ai/
_PACKAGE_DIR = Path(__file__).resolve().parents[1]
if str(_PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_DIR))

from models import (  # noqa: E402
    DificuldadeEnum,
    Exercise,
    ExerciseBatch,
    GenerationRequest,
)


@pytest.fixture
def make_request():
    """Factory for GenerationRequest with sensible defaults."""

    def _make(
        *,
        materia: str = "Matemática",
        topico: str = "Frações",
        dificuldade: DificuldadeEnum = DificuldadeEnum.FACIL,
        quantidade: int = 2,
    ) -> GenerationRequest:
        return GenerationRequest(
            materia=materia,
            topico=topico,
            dificuldade=dificuldade,
            quantidade=quantidade,
        )

    return _make


@pytest.fixture
def make_exercise():
    """Factory for a single Exercise (supplies required dificuldade echo)."""

    def _make(
        *,
        enunciado: str = "enunciado",
        resposta: str = "resposta",
        explicacao: str = "explicacao",
        dificuldade: DificuldadeEnum = DificuldadeEnum.FACIL,
    ) -> Exercise:
        return Exercise(
            enunciado=enunciado,
            resposta=resposta,
            explicacao=explicacao,
            dificuldade=dificuldade,
        )

    return _make


@pytest.fixture
def make_batch(make_exercise):
    """Factory for ExerciseBatch with N filled exercises + dificuldades echo."""

    def _make(
        n: int = 2,
        *,
        dificuldades: list[DificuldadeEnum] | None = None,
        **field_overrides,
    ) -> ExerciseBatch:
        exercises = []
        for i in range(n):
            kwargs = {
                "enunciado": f"enunciado-{i}",
                "resposta": f"resposta-{i}",
                "explicacao": f"explicacao-{i}",
            }
            kwargs.update(field_overrides)
            exercises.append(make_exercise(**kwargs))
        if dificuldades is None:
            bands = {ex.dificuldade for ex in exercises}
            order = (
                DificuldadeEnum.FACIL,
                DificuldadeEnum.MEDIO,
                DificuldadeEnum.DIFICIL,
            )
            dificuldades = [b for b in order if b in bands] or [DificuldadeEnum.FACIL]
        return ExerciseBatch(exercicios=exercises, dificuldades=dificuldades)

    return _make
