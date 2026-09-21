"""Tests for exercicios-gerados success/fail path routing."""
from __future__ import annotations
from pathlib import Path
from unittest.mock import patch
import pytest
from models import DificuldadeEnum, Exercise, ExerciseBatch, GenerationRequest
import main as main_mod
import output_paths
import reliability
import service

def test_resolve_success_out_relative_under_success():
    out = output_paths.resolve_success_out_path('lote.json')
    assert out == output_paths.SUCCESS_DIR / 'lote.json'

def test_resolve_success_out_absolute_unchanged(tmp_path):
    abs_path = tmp_path / 'batch.json'
    assert output_paths.resolve_success_out_path(abs_path) == abs_path

def test_resolve_success_strips_relative_parent(tmp_path):
    out = output_paths.resolve_success_out_path('../escape.json')
    assert out == output_paths.SUCCESS_DIR / 'escape.json'

def test_write_fail_error_log(tmp_path):
    dest = output_paths.write_fail_error_log('falhou X', base_dir=tmp_path)
    assert dest.parent == tmp_path
    assert 'falhou X' in dest.read_text(encoding='utf-8')

def test_default_postmortem_under_fail_postmortem():
    assert reliability.POSTMORTEM_PATH == output_paths.DEFAULT_POSTMORTEM_PATH
    assert 'fail' in str(reliability.POSTMORTEM_PATH).replace('\\', '/')
    assert 'postmortem' in str(reliability.POSTMORTEM_PATH).replace('\\', '/')

def test_run_success_relative_out_writes_success_dir(monkeypatch, tmp_path):
    """Relative --out lands under SUCCESS_DIR (monkeypatched for isolation)."""
    success = tmp_path / 'success'
    monkeypatch.setattr(output_paths, 'SUCCESS_DIR', success)
    batch = ExerciseBatch(exercicios=[Exercise(enunciado='1+1', resposta='2', explicacao='soma', dificuldade=DificuldadeEnum.FACIL)], dificuldades=[DificuldadeEnum.FACIL])
    req = GenerationRequest(topico='x', dificuldade=DificuldadeEnum.FACIL, quantidade=1)
    monkeypatch.setattr(service, 'generate_with_failover', lambda *a, **k: batch)
    main_mod.run(req, out_path='meu.json', max_retries=0)
    dest = success / 'meu.json'
    assert dest.is_file()
    assert 'enunciado' in dest.read_text(encoding='utf-8')

def test_run_failure_writes_error_log(monkeypatch, tmp_path):
    erros = tmp_path / 'erros'
    monkeypatch.setattr(output_paths, 'FAIL_ERROS_DIR', erros)
    monkeypatch.setattr(main_mod, 'write_fail_error_log', lambda msg: output_paths.write_fail_error_log(msg, base_dir=erros))
    req = GenerationRequest(topico='x', dificuldade=DificuldadeEnum.FACIL, quantidade=1)

    def boom(*a, **k):
        raise RuntimeError('geração falhou teste')
    monkeypatch.setattr(service, 'generate_with_failover', boom)
    with pytest.raises(SystemExit) as ei:
        main_mod.run(req, out_path=tmp_path / 'x.json', max_retries=0)
    assert ei.value.code == 1
    files = list(erros.glob('erro-*.txt'))
    assert len(files) == 1
    assert 'geração falhou teste' in files[0].read_text(encoding='utf-8')
