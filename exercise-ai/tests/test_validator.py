"""Durable TEST-02 validator coverage (no live LLM)."""
from __future__ import annotations
import contextlib
import io
import pytest
import validator
from models import Exercise, ExerciseBatch, DificuldadeEnum
from validator import validate_exercise_batch

def test_valid_batch_returns_same_instance(make_request, make_batch):
    req = make_request(quantidade=2)
    good = make_batch(2)
    assert validate_exercise_batch(good, req) is good

def test_non_exercise_batch_raises_without_prefix_and_logs_stderr(make_request):
    req = make_request(quantidade=2)
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(ValueError) as exc_info:
            validate_exercise_batch({'exercicios': []}, req)
    msg = str(exc_info.value)
    assert 'ExerciseBatch' in msg
    assert '[VALIDAÇÃO]' not in msg
    assert '[VALIDAÇÃO]' in buf.getvalue()

def test_chave_exercicios_ausente_via_missing_attr(make_request, make_exercise):
    """TEST-02 chave ausente: ExerciseBatch subclass where hasattr(exercicios) is False."""
    req = make_request(quantidade=1)

    class _MissingExercicios(ExerciseBatch):

        def __getattribute__(self, item: str):
            if item == 'exercicios':
                raise AttributeError(item)
            return object.__getattribute__(self, item)
    batch = _MissingExercicios.model_construct(exercicios=[make_exercise()])
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(ValueError) as exc_info:
            validate_exercise_batch(batch, req)
    msg = str(exc_info.value)
    assert "Chave 'exercicios' ausente" in msg
    assert '[VALIDAÇÃO]' not in msg
    assert '[VALIDAÇÃO]' in buf.getvalue()

def test_chave_exercicios_invalida_nao_lista(make_request, make_batch):
    """TEST-02 chave ausente/inválida: exercicios set to non-list."""
    req = make_request(quantidade=2)
    malformed = make_batch(2)
    object.__setattr__(malformed, 'exercicios', 'nao-lista')
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(ValueError) as exc_info:
            validate_exercise_batch(malformed, req)
    msg = str(exc_info.value)
    assert "Chave 'exercicios' ausente" in msg
    assert '[VALIDAÇÃO]' not in msg
    assert '[VALIDAÇÃO]' in buf.getvalue()

def test_empty_exercicios_list(make_request):
    req = make_request(quantidade=2)
    empty = ExerciseBatch(exercicios=[], dificuldades=[DificuldadeEnum.FACIL])
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(ValueError) as exc_info:
            validate_exercise_batch(empty, req)
    msg = str(exc_info.value).lower()
    assert 'vazia' in msg or 'lista' in msg
    assert '[VALIDAÇÃO]' not in str(exc_info.value)

def test_wrong_quantity_esperado_recebido(make_request, make_exercise):
    req = make_request(quantidade=2)
    bad_qty = ExerciseBatch(exercicios=[make_exercise()], dificuldades=[DificuldadeEnum.FACIL])
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(ValueError) as exc_info:
            validate_exercise_batch(bad_qty, req)
    msg = str(exc_info.value)
    assert 'esperado 2' in msg and 'recebido 1' in msg
    assert '[VALIDAÇÃO]' not in msg
    stderr = buf.getvalue()
    assert '[VALIDAÇÃO]' in stderr
    assert '"enunciado"' in stderr

def test_whitespace_field_path_message(make_request, make_exercise):
    req = make_request(quantidade=2)
    bad_ws = ExerciseBatch(exercicios=[make_exercise(enunciado='ok', resposta='  ', explicacao='ok'), make_exercise(enunciado='ok', resposta='ok', explicacao='ok')], dificuldades=[DificuldadeEnum.FACIL])
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(ValueError) as exc_info:
            validate_exercise_batch(bad_ws, req)
    msg = str(exc_info.value)
    assert 'exercicios[0].resposta' in msg
    assert not msg.startswith('[VALIDAÇÃO]')

def test_report_mode_all_vs_first_exercise(make_request, make_exercise):
    req = make_request(quantidade=2)
    multi = ExerciseBatch(exercicios=[make_exercise(enunciado=' ', resposta='b', explicacao='c'), make_exercise(enunciado=' ', resposta='e', explicacao='f')], dificuldades=[DificuldadeEnum.FACIL])
    original = validator.VALIDATION_REPORT_MODE
    try:
        validator.VALIDATION_REPORT_MODE = 'all'
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            with pytest.raises(ValueError) as exc_all:
                validate_exercise_batch(multi, req)
        err_all = str(exc_all.value)
        assert 'exercicios[0].enunciado' in err_all
        assert 'exercicios[1].enunciado' in err_all
        validator.VALIDATION_REPORT_MODE = 'first_exercise'
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            with pytest.raises(ValueError) as exc_first:
                validate_exercise_batch(multi, req)
        err_first = str(exc_first.value)
        assert 'exercicios[0].enunciado' in err_first
        assert 'exercicios[1].enunciado' not in err_first
    finally:
        validator.VALIDATION_REPORT_MODE = original

def test_structurally_ok_math_wrong_raises_via_validator(make_request, make_exercise):
    """Integration: structural OK + math-wrong → raise; [MATH] stderr; minimal PT."""
    req = make_request(quantidade=1)
    batch = ExerciseBatch(exercicios=[make_exercise(enunciado='2 + 2 = ?', resposta='5', explicacao='errado')], dificuldades=[DificuldadeEnum.FACIL])
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(ValueError) as exc_info:
            validate_exercise_batch(batch, req)
    msg = str(exc_info.value)
    assert '[MATH]' not in msg
    assert '[VALIDAÇÃO]' not in msg
    assert 'matemática' in msg.lower() or 'inconsist' in msg.lower()
    assert '[MATH]' in buf.getvalue()

def test_structurally_ok_math_multi_via_validator(make_request, make_exercise):
    """Integration: two math fails listed in one truncated raise (D-03, D-12)."""
    req = make_request(quantidade=2)
    batch = ExerciseBatch(exercicios=[make_exercise(enunciado='2 + 2', resposta='5', explicacao='e'), make_exercise(enunciado='3 + 3', resposta='9', explicacao='e')], dificuldades=[DificuldadeEnum.FACIL])
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        with pytest.raises(ValueError) as exc_info:
            validate_exercise_batch(batch, req)
    msg = str(exc_info.value)
    assert '0' in msg and '1' in msg
    assert '[MATH]' not in msg
    assert buf.getvalue().count('[MATH]') >= 2
