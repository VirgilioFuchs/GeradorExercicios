"""run() dual-output contract, argparse validation, and LOG-01 events."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from models import DificuldadeEnum, Exercise, ExerciseBatch, GenerationRequest

import main
import reliability


@pytest.fixture
def demo_batch():
    return ExerciseBatch(
        exercicios=[
            Exercise(enunciado="e1", resposta="r1", explicacao="x1"),
            Exercise(enunciado="e2", resposta="r2", explicacao="x2"),
            Exercise(enunciado="e3", resposta="r3", explicacao="x3"),
        ]
    )


def test_run_success_text_stdout_and_json_out(demo_batch, tmp_path):
    out_path = tmp_path / "batch.json"
    request = GenerationRequest(
        materia="Matemática",
        topico="Equação do primeiro grau",
        dificuldade=DificuldadeEnum.FACIL,
        quantidade=3,
    )
    out, err = io.StringIO(), io.StringIO()
    with patch.object(main, "generate_with_failover", return_value=demo_batch) as gen:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            main.run(request, out_path=out_path)
    assert gen.call_count == 1
    stdout = out.getvalue()
    stderr = err.getvalue()

    assert "### Exercício 1" in stdout
    assert "Enunciado: e1" in stdout
    assert "Resposta: r1" in stdout
    assert "Explicação: x1" in stdout
    assert "### Exercício 3" in stdout
    with pytest.raises(json.JSONDecodeError):
        json.loads(stdout)

    parsed = json.loads(out_path.read_text(encoding="utf-8"))
    assert "exercicios" in parsed and len(parsed["exercicios"]) == 3

    assert "Gerando" not in stdout and "Validando" not in stdout
    assert "Início da geração" in stderr
    assert "materia=" in stderr and "topico=" in stderr
    assert "quantidade=" in stderr
    assert "LLM_API_KEY=" not in stderr
    assert "GEMINI_API_KEY=" not in stderr
    assert "sucesso" in stderr.lower()


def test_run_value_error_exits_one_plain_stderr(tmp_path):
    out_path = tmp_path / "batch.json"
    request = GenerationRequest(
        materia="Matemática",
        topico="Equação do primeiro grau",
        dificuldade=DificuldadeEnum.FACIL,
        quantidade=3,
    )
    out2, err2 = io.StringIO(), io.StringIO()
    with patch.object(
        main,
        "generate_with_failover",
        side_effect=ValueError("exercicios[0].resposta está vazio"),
    ) as gen2:
        with contextlib.redirect_stdout(out2), contextlib.redirect_stderr(err2):
            with pytest.raises(SystemExit) as se:
                main.run(request, out_path=out_path, max_retries=0)
    assert se.value.code == 1
    assert gen2.call_count == 1
    assert out2.getvalue() == ""
    assert not out_path.exists()
    err_text = err2.getvalue()
    assert "exercicios[0].resposta está vazio" in err_text
    assert "Erro de configuração ou validação" not in err_text
    assert "Erro na execução da geração" not in err_text
    assert "Início da geração" in err_text
    assert "Parâmetros:" in err_text
    assert "Falha" in err_text or "falha" in err_text.lower()


def test_main_source_keeps_plain_stderr_contract():
    msrc = Path("exercise-ai/main.py").read_text(encoding="utf-8")
    assert "sys.exit(1)" in msrc and "ensure_ascii=False" in msrc
    assert "print(str(val_err), file=sys.stderr)" in msrc
    assert "print(str(run_err), file=sys.stderr)" in msrc
    assert "Erro de configuração ou validação" not in msrc
    assert "Erro na execução da geração" not in msrc
    assert "def run(" in msrc
    assert "run_demo" not in msrc
    assert "generate_with_failover" in msrc
    assert "--max-retries" in msrc


def test_cli_requires_out_before_llm(tmp_path):
    with patch.object(main, "generate_with_failover") as gen:
        with pytest.raises(SystemExit) as se:
            main.main([])
    assert se.value.code == 2
    assert gen.call_count == 0


def test_cli_demo_defaults_with_out(demo_batch, tmp_path):
    out_path = tmp_path / "out.json"
    out, err = io.StringIO(), io.StringIO()
    with patch.object(main, "generate_with_failover", return_value=demo_batch) as gen:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            main.main(["--out", str(out_path)])
    assert gen.call_count == 1
    req = gen.call_args.args[0]
    assert req.materia == "Matemática"
    assert req.topico == "Equação do primeiro grau"
    assert req.dificuldade == DificuldadeEnum.FACIL
    assert req.quantidade == 3
    assert "### Exercício 1" in out.getvalue()
    assert out_path.exists()


def test_cli_rejects_invalid_dificuldade():
    with patch.object(main, "generate_with_failover") as gen:
        with pytest.raises(SystemExit) as se:
            main.main(["--dificuldade", "hard", "--out", "x.json"])
    assert se.value.code == 2
    assert gen.call_count == 0


def test_cli_rejects_invalid_provider():
    with patch.object(main, "generate_with_failover") as gen:
        with pytest.raises(SystemExit) as se:
            main.main(["--provider", "claude", "--out", "x.json"])
    assert se.value.code == 2
    assert gen.call_count == 0


def test_cli_rejects_quantidade_zero_and_over_ceiling():
    with patch.object(main, "generate_with_failover") as gen:
        with pytest.raises(SystemExit):
            main.main(["--quantidade", "0", "--out", "x.json"])
        with pytest.raises(SystemExit):
            main.main(["--quantidade", "41", "--out", "x.json"])
    assert gen.call_count == 0

    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        with pytest.raises(SystemExit):
            main.main(["--quantidade", "41", "--out", "x.json"])
    assert "máximo 40" in err.getvalue()


def test_cli_help_portuguese_lists_defaults():
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        with pytest.raises(SystemExit) as se:
            main.main(["--help"])
    assert se.value.code == 0
    help_text = out.getvalue() + err.getvalue()
    assert "Matemática" in help_text
    assert "Equação do primeiro grau" in help_text
    assert "facil" in help_text
    assert "--out" in help_text
    assert "--provider" in help_text
    assert "--max-retries" in help_text


def test_cli_provider_override_sets_env(demo_batch, tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    monkeypatch.setenv("GEMINI_API_KEY", "AIza-test")
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    out_path = tmp_path / "out.json"
    with patch.object(main, "generate_with_failover", return_value=demo_batch) as gen:
        main.main(["--provider", "openai", "--out", str(out_path)])
    assert gen.call_count == 1
    import os

    assert os.environ.get("LLM_PROVIDER") == "openai"


def test_cli_missing_provider_key_specific_message(monkeypatch, tmp_path):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "AIza-present")
    err = io.StringIO()
    with patch.object(main, "generate_with_failover") as gen:
        with contextlib.redirect_stderr(err):
            with pytest.raises(SystemExit) as se:
                main.main(["--provider", "openai", "--out", str(tmp_path / "o.json")])
    assert se.value.code == 1
    assert gen.call_count == 0
    msg = err.getvalue()
    assert "LLM_API_KEY" in msg
    assert "openai" in msg.lower()


def test_cli_missing_grok_key_specific_message(monkeypatch, tmp_path):
    monkeypatch.delenv("GROK_API_KEY", raising=False)
    monkeypatch.setenv("LLM_API_KEY", "sk-present")
    err = io.StringIO()
    with patch.object(main, "generate_with_failover") as gen:
        with contextlib.redirect_stderr(err):
            with pytest.raises(SystemExit) as se:
                main.main(["--provider", "grok", "--out", str(tmp_path / "o.json")])
    assert se.value.code == 1
    assert gen.call_count == 0
    msg = err.getvalue()
    assert "GROK_API_KEY" in msg
    assert "grok" in msg.lower()


def test_cli_provider_grok_sets_env(demo_batch, tmp_path, monkeypatch):
    monkeypatch.setenv("GROK_API_KEY", "xai-test")
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    out_path = tmp_path / "out.json"
    with patch.object(main, "generate_with_failover", return_value=demo_batch) as gen:
        main.main(["--provider", "grok", "--out", str(out_path)])
    assert gen.call_count == 1
    import os

    assert os.environ.get("LLM_PROVIDER") == "grok"


def test_cli_rejects_max_retries_outside_range():
    with patch.object(main, "generate_with_failover") as gen:
        with pytest.raises(SystemExit) as se:
            main.main(["--max-retries", "4", "--out", "x.json"])
    assert se.value.code == 2
    assert gen.call_count == 0

    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        with pytest.raises(SystemExit):
            main.main(["--max-retries", "-1", "--out", "x.json"])
    assert "max-retries" in err.getvalue().lower()
    assert gen.call_count == 0


def test_cli_max_retries_passes_to_run(demo_batch, tmp_path, monkeypatch):
    monkeypatch.delenv("RELY_MAX_RETRIES", raising=False)
    out_path = tmp_path / "out.json"
    with patch.object(main, "generate_with_failover", return_value=demo_batch) as gen:
        with patch.object(main, "resolve_max_retries", wraps=main.resolve_max_retries) as resolv:
            main.main(["--out", str(out_path), "--max-retries", "0"])
    assert gen.call_count == 1
    assert resolv.call_args.args[0] == 0
    assert out_path.exists()


def test_multi_attempt_failure_no_out_empty_stdout(tmp_path):
    """Exhausted regenerations leave no --out and empty stdout (D-14)."""
    out_path = tmp_path / "batch.json"
    request = GenerationRequest(
        materia="Matemática",
        topico="Equação do primeiro grau",
        dificuldade=DificuldadeEnum.FACIL,
        quantidade=3,
    )
    bad = ExerciseBatch(
        exercicios=[Exercise(enunciado="e1", resposta="", explicacao="x1")]
    )
    out, err = io.StringIO(), io.StringIO()

    def failover_skip_provider(request, max_retries):
        # Point-of-use mock skips resolve_provider() (no API keys in CI).
        return reliability.generate_validated_batch(request, max_retries)

    with patch.object(main, "generate_with_failover", side_effect=failover_skip_provider):
        with patch.object(reliability, "generate_exercises", return_value=bad) as gen:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                with pytest.raises(SystemExit) as se:
                    main.run(request, out_path=out_path, max_retries=2)
    assert se.value.code == 1
    assert gen.call_count == 3
    assert out.getvalue() == ""
    assert not out_path.exists()
    assert "2ª Regeneração" in err.getvalue()
