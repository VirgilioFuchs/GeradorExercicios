"""Unit tests for math_check (no live LLM). Named hybrid fixtures (D-05, D-17)."""
from __future__ import annotations
import contextlib
import io
import pytest
from models import Exercise, ExerciseBatch, DificuldadeEnum
from math_check import check_math_batch, clear_math_buffers, drain_uninterpretable_records

def test_wrong_arithmetic_raises_math_dual_channel():
    """Clear wrong arithmetic → ValueError; [MATH] on stderr only."""
    clear_math_buffers()
    batch = ExerciseBatch(exercicios=[Exercise(enunciado='2 + 2', resposta='5', explicacao='errado', dificuldade=DificuldadeEnum.FACIL)], dificuldades=[DificuldadeEnum.FACIL])
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(ValueError) as exc_info:
            check_math_batch(batch)
    msg = str(exc_info.value)
    assert '[MATH]' not in msg
    assert 'matemática' in msg.lower() or 'inconsist' in msg.lower()
    assert '[MATH]' in buf.getvalue()
    assert 'índice=0' in buf.getvalue() or 'indice=0' in buf.getvalue().lower()

def test_correct_arithmetic_passes():
    """Correct arithmetic returns without raise."""
    clear_math_buffers()
    batch = ExerciseBatch(exercicios=[Exercise(enunciado='2 + 2 = ?', resposta='4', explicacao='dois mais dois', dificuldade=DificuldadeEnum.FACIL)], dificuldades=[DificuldadeEnum.FACIL])
    check_math_batch(batch)

def test_correct_axb_equals_c_passes():
    """Correct ax+b=c solution passes and is interpreted (D-15)."""
    clear_math_buffers()
    batch = ExerciseBatch(exercicios=[Exercise(enunciado='2x + 3 = 7', resposta='2', explicacao='x = (7-3)/2', dificuldade=DificuldadeEnum.FACIL)], dificuldades=[DificuldadeEnum.FACIL])
    check_math_batch(batch)
    assert drain_uninterpretable_records() == []

def test_wrong_axb_equals_c_raises():
    """Wrong ax+b=c solution raises with [MATH] stderr (D-15)."""
    clear_math_buffers()
    batch = ExerciseBatch(exercicios=[Exercise(enunciado='2x + 3 = 7', resposta='5', explicacao='errado', dificuldade=DificuldadeEnum.FACIL)], dificuldades=[DificuldadeEnum.FACIL])
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(ValueError) as exc_info:
            check_math_batch(batch)
    msg = str(exc_info.value)
    assert '[MATH]' not in msg
    assert '0' in msg
    assert '[MATH]' in buf.getvalue()

def test_uninterpretable_does_not_raise_but_records():
    """Fraction-like / radical text → no raise; record drainable (D-02; D-16)."""
    clear_math_buffers()
    batch = ExerciseBatch(exercicios=[Exercise(enunciado='Simplifique √16 / 2', resposta='2', explicacao='radical', dificuldade=DificuldadeEnum.FACIL)], dificuldades=[DificuldadeEnum.FACIL])
    check_math_batch(batch)
    records = drain_uninterpretable_records()
    assert len(records) >= 1
    assert records[0]['reason'] == 'uninterpretable'
    assert records[0]['index'] == 0

def test_multi_index_lists_all_inconsistencies():
    """Two clear inconsistencies → one ValueError listing both indices (D-03)."""
    clear_math_buffers()
    batch = ExerciseBatch(exercicios=[Exercise(enunciado='2 + 2', resposta='5', explicacao='errado', dificuldade=DificuldadeEnum.FACIL), Exercise(enunciado='3 × 3', resposta='10', explicacao='errado', dificuldade=DificuldadeEnum.FACIL), Exercise(enunciado='1 + 1', resposta='2', explicacao='ok', dificuldade=DificuldadeEnum.FACIL)], dificuldades=[DificuldadeEnum.FACIL])
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(ValueError) as exc_info:
            check_math_batch(batch)
    msg = str(exc_info.value)
    assert '0' in msg and '1' in msg
    assert '[MATH]' not in msg
    stderr = buf.getvalue()
    assert stderr.count('[MATH]') >= 2

def test_simple_percent_arithmetic_checked():
    """Percent that reduces to arithmetic may be checked (D-16)."""
    clear_math_buffers()
    batch_wrong = ExerciseBatch(exercicios=[Exercise(enunciado='10 + 10', resposta='30', explicacao='errado', dificuldade=DificuldadeEnum.FACIL)], dificuldades=[DificuldadeEnum.FACIL])
    with contextlib.redirect_stderr(io.StringIO()):
        with pytest.raises(ValueError):
            check_math_batch(batch_wrong)
