"""Domain bounds and plan-contract tracers for GenerationRequest (Phase 13)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from models import (
    DificuldadeEnum,
    Exercise,
    ExerciseBatch,
    ExerciseSpec,
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


def test_verify_plan_echo_batch_dificuldades_summary_mismatch():
    """D-07: per-slot OK but batch.dificuldades ≠ request.dificuldades fails."""
    req = GenerationRequest(
        topico="Frações",
        quantidade=2,
        plano=PlanoDificuldade(facil=1, medio=1, dificil=0),
    )
    drifted = ExerciseBatch(
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
        dificuldades=[DificuldadeEnum.FACIL],  # missing medio in summary
    )
    with pytest.raises(ValueError, match="resumo dificuldades"):
        verify_plan_echo(drifted, req)


def test_verify_plan_echo_duplicated_summary_padding_ok():
    """LLM padding ['medio','medio'] vs summary ['medio'] is accepted (canonical unique)."""
    req = GenerationRequest(
        topico="Equação do primeiro grau",
        dificuldade=DificuldadeEnum.MEDIO,
        quantidade=2,
    )
    assert req.dificuldades == [DificuldadeEnum.MEDIO]
    padded = ExerciseBatch(
        exercicios=[
            Exercise(
                enunciado="a",
                resposta="1",
                explicacao="x",
                dificuldade=DificuldadeEnum.MEDIO,
            ),
            Exercise(
                enunciado="b",
                resposta="2",
                explicacao="y",
                dificuldade=DificuldadeEnum.MEDIO,
            ),
        ],
        dificuldades=[DificuldadeEnum.MEDIO, DificuldadeEnum.MEDIO],
    )
    verify_plan_echo(padded, req)


def test_verify_plan_echo_length_mismatch():
    """Length mismatch between batch and slots raises ValueError."""
    req = GenerationRequest(
        topico="Frações",
        quantidade=2,
        plano=PlanoDificuldade(facil=1, medio=1, dificil=0),
    )
    short = ExerciseBatch(
        exercicios=[
            Exercise(
                enunciado="a",
                resposta="1",
                explicacao="x",
                dificuldade=DificuldadeEnum.FACIL,
            ),
        ],
        dificuldades=[DificuldadeEnum.FACIL],
    )
    with pytest.raises(ValueError, match="tamanho do batch"):
        verify_plan_echo(short, req)


def test_plano_and_itens_xor_rejected():
    """D-03: plano ∧ itens → ValidationError."""
    with pytest.raises(ValidationError, match="mutuamente exclusivos"):
        GenerationRequest(
            topico="Frações",
            quantidade=2,
            plano=PlanoDificuldade(facil=1, medio=1, dificil=0),
            itens=[
                ExerciseSpec(dificuldade=DificuldadeEnum.FACIL),
                ExerciseSpec(dificuldade=DificuldadeEnum.MEDIO),
            ],
        )


def test_quantidade_mismatch_plano_rejected():
    """BATCH-02: quantidade != sum(plano) → ValidationError."""
    with pytest.raises(ValidationError, match="quantidade"):
        GenerationRequest(
            topico="Frações",
            quantidade=3,
            plano=PlanoDificuldade(facil=1, medio=1, dificil=0),
        )


def test_quantidade_mismatch_itens_rejected():
    """BATCH-02: quantidade != len(itens) → ValidationError."""
    with pytest.raises(ValidationError, match="quantidade"):
        GenerationRequest(
            topico="Frações",
            quantidade=3,
            itens=[
                ExerciseSpec(dificuldade=DificuldadeEnum.FACIL),
                ExerciseSpec(dificuldade=DificuldadeEnum.MEDIO),
            ],
        )


def test_empty_plano_with_qty_rejected():
    """Empty plano (all zeros) with quantidade>0 fails BATCH-02."""
    with pytest.raises(ValidationError, match="quantidade"):
        GenerationRequest(
            topico="Frações",
            quantidade=2,
            plano=PlanoDificuldade(facil=0, medio=0, dificil=0),
        )


def test_itens_only_path_preserves_order():
    """BATCH-01: explicit itens accepted and ordered as given."""
    req = GenerationRequest(
        topico="Frações",
        quantidade=3,
        itens=[
            ExerciseSpec(dificuldade=DificuldadeEnum.DIFICIL),
            ExerciseSpec(dificuldade=DificuldadeEnum.FACIL),
            ExerciseSpec(dificuldade=DificuldadeEnum.MEDIO),
        ],
    )
    assert [s.dificuldade for s in req.itens_ordenados] == [
        DificuldadeEnum.DIFICIL,
        DificuldadeEnum.FACIL,
        DificuldadeEnum.MEDIO,
    ]
    assert req.dificuldades == [
        DificuldadeEnum.FACIL,
        DificuldadeEnum.MEDIO,
        DificuldadeEnum.DIFICIL,
    ]


def test_equal_split_dificuldades_remainder_to_last():
    """D-07/D-08: qty 5, facil+medio → 2 fáceis + 3 médios."""
    req = GenerationRequest(
        topico="Frações",
        quantidade=5,
        dificuldades=[DificuldadeEnum.FACIL, DificuldadeEnum.MEDIO],
    )
    bands = [s.dificuldade for s in req.itens_ordenados]
    assert bands == (
        [DificuldadeEnum.FACIL] * 2 + [DificuldadeEnum.MEDIO] * 3
    )
    assert req.dificuldades == [DificuldadeEnum.FACIL, DificuldadeEnum.MEDIO]
