"""Domain bounds and plan-contract tracers for GenerationRequest (Phase 13)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from models import (
    DificuldadeEnum,
    Exercise,
    ExerciseBatch,
    GenerationRequest,
    MAX_QUANTIDADE,
    PlanoDificuldade,
    verify_plan_echo,
)


def _req(**overrides):
    base = {
        "materia": "Matemática",
        "topico": "Equação do primeiro grau",
        "dificuldade": DificuldadeEnum.FACIL,
        "quantidade": 3,
    }
    base.update(overrides)
    return GenerationRequest(**base)


def test_quantidade_zero_rejected():
    with pytest.raises(ValidationError):
        _req(quantidade=0)


def test_quantidade_above_max_rejected():
    with pytest.raises(ValidationError):
        _req(quantidade=41)


def test_quantidade_one_accepted():
    assert _req(quantidade=1).quantidade == 1


def test_quantidade_forty_accepted():
    assert _req(quantidade=40).quantidade == 40


def test_empty_topico_rejected():
    with pytest.raises(ValidationError):
        _req(topico="")


def test_whitespace_topico_rejected():
    with pytest.raises(ValidationError):
        _req(topico="   ")


def test_max_quantidade_cap_unchanged():
    assert MAX_QUANTIDADE == 40


def test_uniform_legacy_normalizes_dificuldades():
    """D-05/D-06 / BATCH-04: scalar dificuldade → dificuldades length 1."""
    req = GenerationRequest(
        topico="Frações",
        dificuldade="medio",
        quantidade=3,
    )
    assert req.dificuldades == [DificuldadeEnum.MEDIO]
    assert req.dificuldade == DificuldadeEnum.MEDIO
    assert req.itens is None
    assert len(req.itens_ordenados) == 3
    assert all(s.dificuldade == DificuldadeEnum.MEDIO for s in req.itens_ordenados)


def test_mixed_plano_expands_facil_medio():
    """D-01/D-02/D-04: plano expands fácil→médio; dificuldades summary."""
    req = GenerationRequest(
        topico="Frações",
        quantidade=2,
        plano=PlanoDificuldade(facil=1, medio=1, dificil=0),
    )
    assert [s.dificuldade for s in req.itens_ordenados] == [
        DificuldadeEnum.FACIL,
        DificuldadeEnum.MEDIO,
    ]
    assert req.dificuldades == [DificuldadeEnum.FACIL, DificuldadeEnum.MEDIO]
    assert req.dificuldade == DificuldadeEnum.FACIL
    assert req.itens is not None


def test_exercise_and_batch_require_echo_fields():
    """D-09/D-10 / BATCH-03: dificuldade on Exercise; dificuldades on batch."""
    ex = Exercise(
        enunciado="e",
        resposta="r",
        explicacao="x",
        dificuldade=DificuldadeEnum.MEDIO,
    )
    batch = ExerciseBatch(exercicios=[ex], dificuldades=[DificuldadeEnum.MEDIO])
    assert ex.dificuldade == DificuldadeEnum.MEDIO
    assert batch.dificuldades == [DificuldadeEnum.MEDIO]


def test_verify_plan_echo_passes_and_fails():
    """D-11: mismatch raises ValueError; no mutation."""
    req = GenerationRequest(
        topico="Frações",
        quantidade=2,
        plano=PlanoDificuldade(facil=1, medio=1, dificil=0),
    )
    ok = ExerciseBatch(
        exercicios=[
            Exercise(
                enunciado="a",
                resposta="1",
                explicacao="x",
                dificuldade=DificuldadeEnum.FACIL,
            ),
            Exercise(
                enunciado="b",
                resposta="2",
                explicacao="y",
                dificuldade=DificuldadeEnum.MEDIO,
            ),
        ],
        dificuldades=req.dificuldades,
    )
    verify_plan_echo(ok, req)

    bad = ExerciseBatch(
        exercicios=[
            Exercise(
                enunciado="a",
                resposta="1",
                explicacao="x",
                dificuldade=DificuldadeEnum.MEDIO,  # wrong slot
            ),
            Exercise(
                enunciado="b",
                resposta="2",
                explicacao="y",
                dificuldade=DificuldadeEnum.MEDIO,
            ),
        ],
        dificuldades=req.dificuldades,
    )
    with pytest.raises(ValueError, match="echo mismatch"):
        verify_plan_echo(bad, req)
    assert bad.exercicios[0].dificuldade == DificuldadeEnum.MEDIO
