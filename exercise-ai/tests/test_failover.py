"""Offline mocked D-12 matrix for OpenAI ↔ Gemini failover (Phase 8)."""
from __future__ import annotations
import contextlib
import io
import json
from unittest.mock import MagicMock, patch
import pytest
from models import DificuldadeEnum, Exercise, ExerciseBatch, GenerationRequest
from openai import APITimeoutError, AuthenticationError
import failover
import generator
import generator_gemini
import main
DUMMY_LLM_KEY = 'sk-TEST-LEAK-LLM-KEY-9f3a2b1c'
DUMMY_GEMINI_KEY = 'AIzaSy-TEST-LEAK-GEMINI-KEY-7d4e'

@pytest.fixture
def demo_batch():
    return ExerciseBatch(exercicios=[Exercise(enunciado='e1', resposta='r1', explicacao='x1', dificuldade=DificuldadeEnum.FACIL), Exercise(enunciado='e2', resposta='r2', explicacao='x2', dificuldade=DificuldadeEnum.FACIL), Exercise(enunciado='e3', resposta='r3', explicacao='x3', dificuldade=DificuldadeEnum.FACIL)], dificuldades=[DificuldadeEnum.FACIL])

@pytest.fixture
def request_demo():
    return GenerationRequest(materia='Matemática', topico='Equação do primeiro grau', dificuldade=DificuldadeEnum.FACIL, quantidade=3)

def _permanent(kind: str, msg: str='falha api') -> RuntimeError:
    err = RuntimeError(msg)
    err.retriable = False
    err.api_error_kind = kind
    return err

def test_openai_timeout_eligible_auth_not():
    timeout_err = generator.map_openai_compatible_error(APITimeoutError(request=MagicMock()), api_tag='openai', of_label='da OpenAI', auth_key_name='LLM_API_KEY')
    assert timeout_err.api_error_kind == 'timeout'
    assert timeout_err.retriable is False
    assert failover.is_failover_eligible(timeout_err) is True
    auth_err = generator.map_openai_compatible_error(AuthenticationError(message='bad key', response=MagicMock(status_code=401), body=None), api_tag='openai', of_label='da OpenAI', auth_key_name='LLM_API_KEY')
    assert auth_err.api_error_kind == 'auth'
    assert failover.is_failover_eligible(auth_err) is False

def test_gemini_mapper_kinds():

    class _St:

        def __init__(self, code):
            self.status_code = code

        def __str__(self):
            return f'status {self.status_code}'
    with contextlib.redirect_stderr(io.StringIO()):
        assert generator_gemini.map_gemini_error(_St(401)).api_error_kind == 'auth'
        assert generator_gemini.map_gemini_error(_St(429)).api_error_kind == 'rate_limit'
        assert generator_gemini.map_gemini_error(_St(408)).api_error_kind == 'timeout'
        assert generator_gemini.map_gemini_error(_St(500)).api_error_kind == 'generic'

def test_openai_to_gemini_failover_success(demo_batch, request_demo, monkeypatch):
    """Tracer: eligible timeout → one peer retry + [FAILOVER] without secrets."""
    monkeypatch.setenv('LLM_API_KEY', DUMMY_LLM_KEY)
    monkeypatch.setenv('GEMINI_API_KEY', DUMMY_GEMINI_KEY)
    monkeypatch.setenv('LLM_PROVIDER', 'openai')
    calls: list[tuple] = []
    switched: list[str] = []

    def fake_gen(req, max_retries):
        calls.append((req, max_retries))
        if len(calls) == 1:
            raise _permanent('timeout', 'Tempo esgotado')
        return demo_batch
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        out = failover.generate_with_failover(request_demo, 1, generate_fn=fake_gen, resolve_provider=lambda: 'openai', switch_provider=switched.append)
    assert out is demo_batch
    assert len(calls) == 2
    assert calls[0][0] is request_demo and calls[1][0] is request_demo
    assert calls[0][1] == 1 and calls[1][1] == 1
    assert switched == ['gemini']
    stderr = err.getvalue()
    assert '[FAILOVER] openai -> gemini (timeout)' in stderr
    assert '[FAILOVER] usado: gemini' in stderr
    assert DUMMY_LLM_KEY not in stderr
    assert DUMMY_GEMINI_KEY not in stderr

@pytest.mark.parametrize('kind', ['rate_limit', 'connection', 'generic'])
def test_gemini_to_openai_eligible_kinds(kind, demo_batch, request_demo, monkeypatch):
    monkeypatch.setenv('LLM_API_KEY', DUMMY_LLM_KEY)
    monkeypatch.setenv('GEMINI_API_KEY', DUMMY_GEMINI_KEY)
    switched: list[str] = []
    calls = {'n': 0}

    def fake_gen(req, max_retries):
        calls['n'] += 1
        if calls['n'] == 1:
            raise _permanent(kind)
        return demo_batch
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        failover.generate_with_failover(request_demo, 0, generate_fn=fake_gen, resolve_provider=lambda: 'gemini', switch_provider=switched.append)
    assert calls['n'] == 2
    assert switched == ['openai']
    assert f'[FAILOVER] gemini -> openai ({kind})' in err.getvalue()
    assert switched.count('openai') == 1

@pytest.mark.parametrize('kind', ['auth', 'refusal'])
def test_no_failover_on_auth_or_refusal(kind, request_demo):
    calls = {'n': 0}
    switched: list[str] = []

    def fake_gen(req, max_retries):
        calls['n'] += 1
        raise _permanent(kind)
    err = io.StringIO()
    with pytest.raises(RuntimeError), contextlib.redirect_stderr(err):
        failover.generate_with_failover(request_demo, 1, generate_fn=fake_gen, resolve_provider=lambda: 'openai', switch_provider=switched.append)
    assert calls['n'] == 1
    assert switched == []
    assert '[FAILOVER]' not in err.getvalue()

def test_no_failover_on_retriable_invalid(request_demo):
    calls = {'n': 0}
    switched: list[str] = []
    retriable = RuntimeError('estrutura ausente')
    retriable.retriable = True

    def fake_gen(req, max_retries):
        calls['n'] += 1
        raise retriable
    err = io.StringIO()
    with pytest.raises(RuntimeError), contextlib.redirect_stderr(err):
        failover.generate_with_failover(request_demo, 1, generate_fn=fake_gen, resolve_provider=lambda: 'openai', switch_provider=switched.append)
    assert calls['n'] == 1
    assert switched == []
    assert '[FAILOVER]' not in err.getvalue()

def test_no_failover_on_validation_value_error(request_demo):
    calls = {'n': 0}
    switched: list[str] = []

    def fake_gen(req, max_retries):
        calls['n'] += 1
        raise ValueError('exercicios[0].resposta está vazio')
    err = io.StringIO()
    with pytest.raises(ValueError), contextlib.redirect_stderr(err):
        failover.generate_with_failover(request_demo, 1, generate_fn=fake_gen, resolve_provider=lambda: 'openai', switch_provider=switched.append)
    assert calls['n'] == 1
    assert switched == []
    assert '[FAILOVER]' not in err.getvalue()

def test_grok_skips_failover_even_on_timeout(request_demo, demo_batch):
    calls = {'n': 0}
    switched: list[str] = []

    def fake_gen(req, max_retries):
        calls['n'] += 1
        raise _permanent('timeout')
    err = io.StringIO()
    with pytest.raises(RuntimeError), contextlib.redirect_stderr(err):
        failover.generate_with_failover(request_demo, 1, generate_fn=fake_gen, resolve_provider=lambda: 'grok', switch_provider=switched.append)
    assert calls['n'] == 1
    assert switched == []
    assert '[FAILOVER]' not in err.getvalue()
    assert failover.failover_peer('grok') is None

def test_missing_secondary_key_no_second_generate(request_demo, monkeypatch):
    monkeypatch.setenv('LLM_API_KEY', DUMMY_LLM_KEY)
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    calls = {'n': 0}
    switched: list[str] = []

    def fake_gen(req, max_retries):
        calls['n'] += 1
        raise _permanent('timeout')
    err = io.StringIO()
    with pytest.raises(ValueError, match='GEMINI_API_KEY') as ei:
        with contextlib.redirect_stderr(err):
            failover.generate_with_failover(request_demo, 1, generate_fn=fake_gen, resolve_provider=lambda: 'openai', switch_provider=switched.append)
    assert '.env' in str(ei.value)
    assert calls['n'] == 1
    assert switched == []
    assert '[FAILOVER] openai -> gemini (timeout)' in err.getvalue()
    assert DUMMY_LLM_KEY not in str(ei.value)

def test_secondary_failure_propagates_no_third(request_demo, monkeypatch):
    monkeypatch.setenv('LLM_API_KEY', DUMMY_LLM_KEY)
    monkeypatch.setenv('GEMINI_API_KEY', DUMMY_GEMINI_KEY)
    calls = {'n': 0}
    switched: list[str] = []

    def fake_gen(req, max_retries):
        calls['n'] += 1
        if calls['n'] == 1:
            raise _permanent('connection')
        raise _permanent('rate_limit', 'secundário falhou')
    err = io.StringIO()
    with pytest.raises(RuntimeError, match='secundário falhou'), contextlib.redirect_stderr(err):
        failover.generate_with_failover(request_demo, 1, generate_fn=fake_gen, resolve_provider=lambda: 'openai', switch_provider=switched.append)
    assert calls['n'] == 2
    assert switched == ['gemini']
    assert '[FAILOVER] usado:' not in err.getvalue()

def test_explicit_provider_openai_still_failovers(demo_batch, request_demo, monkeypatch):
    """D-10: --provider openai (via env) does not disable failover."""
    monkeypatch.setenv('LLM_PROVIDER', 'openai')
    monkeypatch.setenv('LLM_API_KEY', DUMMY_LLM_KEY)
    monkeypatch.setenv('GEMINI_API_KEY', DUMMY_GEMINI_KEY)
    switched: list[str] = []
    calls = {'n': 0}

    def fake_gen(req, max_retries):
        calls['n'] += 1
        if calls['n'] == 1:
            raise _permanent('timeout')
        return demo_batch
    with contextlib.redirect_stderr(io.StringIO()):
        failover.generate_with_failover(request_demo, 1, generate_fn=fake_gen, resolve_provider=generator._resolve_provider, switch_provider=switched.append)
    assert calls['n'] == 2
    assert switched == ['gemini']

def test_run_failover_writes_out_and_redacts(demo_batch, request_demo, tmp_path, monkeypatch):
    monkeypatch.setenv('LLM_API_KEY', DUMMY_LLM_KEY)
    monkeypatch.setenv('GEMINI_API_KEY', DUMMY_GEMINI_KEY)
    monkeypatch.setenv('LLM_PROVIDER', 'openai')
    out_path = tmp_path / 'batch.json'
    calls = {'n': 0}

    def fake_gen(req, max_retries):
        calls['n'] += 1
        if calls['n'] == 1:
            raise _permanent('timeout', f'leak? {DUMMY_LLM_KEY}')
        return demo_batch
    import service
    out, err = (io.StringIO(), io.StringIO())
    with patch.object(service, 'generate_with_failover', side_effect=lambda req, max_retries: failover.generate_with_failover(req, max_retries, generate_fn=fake_gen, resolve_provider=lambda: 'openai', switch_provider=lambda name: None)):
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            main.run(request_demo, out_path=out_path, max_retries=0)
    assert out_path.exists()
    parsed = json.loads(out_path.read_text(encoding='utf-8'))
    assert len(parsed['exercicios']) == 3
    assert '### Exercício 1' in out.getvalue()
    stderr = err.getvalue()
    assert '[FAILOVER] openai -> gemini (timeout)' in stderr
    assert DUMMY_LLM_KEY not in stderr
    assert DUMMY_GEMINI_KEY not in stderr
    assert calls['n'] == 2

def test_failover_peer_helpers():
    assert failover.failover_peer('openai') == 'gemini'
    assert failover.failover_peer('gemini') == 'openai'
    assert failover.failover_peer('grok') is None
    assert failover.failover_peer('other') is None
