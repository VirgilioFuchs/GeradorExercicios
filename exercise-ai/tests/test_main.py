"""run_demo stdout purity, fail-fast exit, and LOG-01 events."""

from __future__ import annotations

import contextlib
import io
import json
from unittest.mock import patch

import pytest
from models import Exercise, ExerciseBatch

import main


@pytest.fixture
def demo_batch():
    return ExerciseBatch(
        exercicios=[
            Exercise(enunciado="e1", resposta="r1", explicacao="x1"),
            Exercise(enunciado="e2", resposta="r2", explicacao="x2"),
            Exercise(enunciado="e3", resposta="r3", explicacao="x3"),
        ]
    )


def test_run_demo_success_stdout_json_only(demo_batch):
    out, err = io.StringIO(), io.StringIO()
    with patch.object(main, "generate_exercises", return_value=demo_batch) as gen:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            main.run_demo()
    assert gen.call_count == 1
    stdout = out.getvalue()
    stderr = err.getvalue()
    assert "Gerando" not in stdout and "Validando" not in stdout
    parsed = json.loads(stdout)
    assert "exercicios" in parsed and len(parsed["exercicios"]) == 3
    assert "Gerando" in stderr and "Validando" in stderr

    # LOG-01: start, params (no secrets), success — suite fails if wiring missing
    assert "Início da geração" in stderr
    assert "materia=" in stderr and "topico=" in stderr
    assert "quantidade=" in stderr
    assert "LLM_API_KEY=" not in stderr
    assert "GEMINI_API_KEY=" not in stderr
    assert "sucesso" in stderr.lower()


def test_run_demo_value_error_exits_one_plain_stderr():
    out2, err2 = io.StringIO(), io.StringIO()
    with patch.object(
        main,
        "generate_exercises",
        side_effect=ValueError("exercicios[0].resposta está vazio"),
    ) as gen2:
        with contextlib.redirect_stdout(out2), contextlib.redirect_stderr(err2):
            with pytest.raises(SystemExit) as se:
                main.run_demo()
    assert se.value.code == 1
    assert gen2.call_count == 1
    assert out2.getvalue() == ""
    err_text = err2.getvalue()
    assert "exercicios[0].resposta está vazio" in err_text
    assert "Erro de configuração ou validação" not in err_text
    assert "Erro na execução da geração" not in err_text

    # LOG-01 failure / validation reason
    assert "Início da geração" in err_text
    assert "Parâmetros:" in err_text
    assert "Falha" in err_text or "falha" in err_text.lower()


def test_main_source_keeps_plain_stderr_contract():
    msrc = open("exercise-ai/main.py", encoding="utf-8").read()
    assert "sys.exit(1)" in msrc and "ensure_ascii=False" in msrc
    assert "print(str(val_err), file=sys.stderr)" in msrc
    assert "print(str(run_err), file=sys.stderr)" in msrc
    assert "Erro de configuração ou validação" not in msrc
    assert "Erro na execução da geração" not in msrc
