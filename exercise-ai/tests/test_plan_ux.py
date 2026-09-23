"""Unit tests for plan_ux band → GenerationRequest kwargs."""

from __future__ import annotations

import pytest
from models import DificuldadeEnum, GenerationRequest, PlanoDificuldade

import plan_ux


def test_parse_plano_csv_ok():
    assert plan_ux.parse_plano_csv("2,3,1") == (2, 3, 1)
    assert plan_ux.parse_plano_csv(" 0 , 5 , 0 ") == (0, 5, 0)


def test_parse_plano_csv_errors():
    with pytest.raises(ValueError, match="F,M,D"):
        plan_ux.parse_plano_csv("2,3")
    with pytest.raises(ValueError, match="inteiro"):
        plan_ux.parse_plano_csv("a,1,0")
    with pytest.raises(ValueError, match="≥0"):
        plan_ux.parse_plano_csv("1,-1,0")


def test_build_mixed_plano():
    kw = plan_ux.build_request_kwargs(2, 3, 0, quantidade_field=99)
    assert "plano" in kw
    assert kw["plano"] == PlanoDificuldade(facil=2, medio=3, dificil=0)
    assert kw["quantidade"] == 5
    assert "dificuldade" not in kw
    req = GenerationRequest(materia="Matemática", topico="eq", **kw)
    assert req.plano is not None
    assert req.quantidade == 5


def test_build_uniform_legacy():
    kw = plan_ux.build_request_kwargs(0, 3, 0, quantidade_field=99)
    assert kw["dificuldade"] == DificuldadeEnum.MEDIO
    assert kw["quantidade"] == 3
    assert "plano" not in kw
    req = GenerationRequest(materia="Matemática", topico="eq", **kw)
    assert req.plano is None
    assert req.dificuldade == DificuldadeEnum.MEDIO


def test_build_zero_bands_raises():
    with pytest.raises(ValueError, match="plano vazio"):
        plan_ux.build_request_kwargs(0, 0, 0, quantidade_field=3)


def test_soft_warn_qty_mismatch(capsys):
    plan_ux.soft_warn_bands(1, 1, 0, quantidade_field=5, file=None)
    err = capsys.readouterr().err
    assert "quantidade=5" in err
    assert "soma" in err
