"""Prompt slot enumeration from itens_ordenados (Phase 14 / PROMPT-01)."""

from __future__ import annotations

from models import DificuldadeEnum, GenerationRequest, PlanoDificuldade
from prompts import build_prompts


def test_mixed_prompt_enumerates_hybrid_slots():
    """Mixed plano → numbered hybrid labels per slot (D-01, D-04)."""
    req = GenerationRequest(
        materia="Matemática",
        topico="Frações",
        quantidade=3,
        plano=PlanoDificuldade(facil=1, medio=1, dificil=1),
    )
    _, user = build_prompts(req)
    assert "1. fácil (facil)" in user
    assert "2. médio (medio)" in user
    assert "3. difícil (dificil)" in user
    assert "enunciado:" not in user
    assert "resposta:" not in user
    assert "explicacao:" not in user


def test_uniform_prompt_enumerates_n_slots_same_band():
    """Uniform scalar dificuldade still enumerates N hybrid lines (D-02)."""
    req = GenerationRequest(
        materia="Matemática",
        topico="Equação do primeiro grau",
        dificuldade=DificuldadeEnum.MEDIO,
        quantidade=3,
    )
    _, user = build_prompts(req)
    assert "1. médio (medio)" in user
    assert "2. médio (medio)" in user
    assert "3. médio (medio)" in user
    assert user.count("médio (medio)") == 3
    assert "Matemática" in user
    assert "Equação do primeiro grau" in user
    assert "enunciado:" not in user
    assert "resposta:" not in user
    assert "explicacao:" not in user


def test_uniform_facil_prompt_uses_hybrid_facil_label():
    """Uniform fácil path uses accented hybrid label (D-02, D-04)."""
    req = GenerationRequest(
        materia="Matemática",
        topico="Soma",
        dificuldade=DificuldadeEnum.FACIL,
        quantidade=2,
    )
    _, user = build_prompts(req)
    assert "1. fácil (facil)" in user
    assert "2. fácil (facil)" in user
    assert user.count("fácil (facil)") == 2


def test_prompt_includes_dificuldades_summary_shape_cue():
    """G-14-4 / SEED-008: one-line unique-band resumo cue; no field-schema dump."""
    req = GenerationRequest(
        materia="Matemática",
        topico="Frações",
        dificuldade=DificuldadeEnum.MEDIO,
        quantidade=2,
    )
    _, user = build_prompts(req)
    assert "resumo das faixas distintas" in user
    assert "enunciado:" not in user
    assert "resposta:" not in user
    assert "explicacao:" not in user
