"""Domain bounds for GenerationRequest (D-09 / EMBED-03)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from models import DificuldadeEnum, GenerationRequest


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
