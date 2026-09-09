"""Unit tests for math_check (no live LLM)."""

from __future__ import annotations

import contextlib
import io

import pytest
from models import Exercise, ExerciseBatch
from math_check import check_math_batch, clear_math_buffers


def test_wrong_arithmetic_raises_math_dual_channel():
    """Clear wrong arithmetic → ValueError; [MATH] on stderr only."""
    clear_math_buffers()
    batch = ExerciseBatch(
        exercicios=[
            Exercise(enunciado="2 + 2", resposta="5", explicacao="errado"),
        ]
    )
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(ValueError) as exc_info:
            check_math_batch(batch)
    msg = str(exc_info.value)
    assert "[MATH]" not in msg
    assert "matemática" in msg.lower() or "inconsist" in msg.lower()
    assert "[MATH]" in buf.getvalue()
    assert "índice=0" in buf.getvalue() or "indice=0" in buf.getvalue().lower()


def test_correct_arithmetic_passes():
    """Correct arithmetic returns without raise."""
    clear_math_buffers()
    batch = ExerciseBatch(
        exercicios=[
            Exercise(enunciado="2 + 2 = ?", resposta="4", explicacao="dois mais dois"),
        ]
    )
    check_math_batch(batch)  # no raise
