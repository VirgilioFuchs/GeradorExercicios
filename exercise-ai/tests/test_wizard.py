"""Offline tests for interactive ``gerar`` wizard (mock input / isatty)."""

from __future__ import annotations

import io
import os
from unittest.mock import MagicMock, patch

import pytest
from models import DificuldadeEnum

import main as main_mod
import wizard


def _scripted_input(answers: list[str]):
    """Return a callable that yields scripted answers then fails if over-consumed."""
    it = iter(answers)

    def _read() -> str:
        try:
            return next(it)
        except StopIteration as exc:
            raise AssertionError("input() called more times than scripted") from exc

    return _read


def test_collect_defaults_and_all_tips(capsys):
    """Enter accepts demo defaults; JSON re-prompts; all 7 tips on stdout (D-07..D-11)."""
    answers = wizard.collect_wizard_answers(
        input_fn=_scripted_input(["", "", "", "", "", "", "", "saida.json"]),
        isatty_fn=lambda: True,
    )
    assert answers.topico == main_mod._DEFAULT_TOPICO
    assert answers.materia == main_mod._DEFAULT_MATERIA
    assert answers.dificuldade == main_mod._DEFAULT_DIFICULDADE
    assert answers.quantidade == main_mod._DEFAULT_QUANTIDADE
    assert answers.provider is None
    assert answers.reasoning == "medium"
    assert answers.out_path == "saida.json"

    out = capsys.readouterr().out
    assert "Equação do primeiro grau" in out
    assert "Matemática" in out
    assert "facil" in out
    assert "1–40" in out or "1-40" in out
    assert "Enter = 3" in out
    assert "openai" in out and "gemini" in out and "grok" in out
    assert "Grok/Gemini" in out
    assert "gpt-4o-mini" in out
    assert "Obrigatório" in out
    assert "max-retries" not in out.lower()
    assert "profile" not in out.lower()


def test_non_tty_fails_without_input(capsys):
    input_mock = MagicMock(side_effect=AssertionError("input must not be called"))
    with pytest.raises(SystemExit) as se:
        wizard.collect_wizard_answers(input_fn=input_mock, isatty_fn=lambda: False)
    assert se.value.code == 1
    input_mock.assert_not_called()
    err = capsys.readouterr().err
    assert "TTY" in err
    assert "argparse" in err.lower() or "flags" in err.lower()


def test_gerar_main_calls_run_with_mapped_request(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("LLM_REASONING_EFFORT", raising=False)

    captured: dict = {}

    def fake_run(request, out_path, max_retries=None):
        captured["request"] = request
        captured["out_path"] = str(out_path)
        captured["max_retries"] = max_retries
        captured["provider"] = os.environ.get("LLM_PROVIDER")
        captured["reasoning"] = os.environ.get("LLM_REASONING_EFFORT")

    script = [
        "Frações",
        "Álgebra",
        "medio",
        "5",
        "openai",
        "high",
        "wizard-out.json",
    ]
    with (
        patch.object(main_mod, "run", side_effect=fake_run),
        patch.object(wizard, "is_interactive_stdin", return_value=True),
        patch("builtins.input", side_effect=script),
    ):
        main_mod.main(["gerar"])

    req = captured["request"]
    assert req.materia == "Álgebra"
    assert req.topico == "Frações"
    assert req.dificuldade == DificuldadeEnum.MEDIO
    assert req.quantidade == 5
    assert captured["out_path"] == "wizard-out.json"
    assert captured["max_retries"] is None
    assert captured["provider"] == "openai"
    assert captured["reasoning"] == "high"

    out = capsys.readouterr().out
    assert "Grok/Gemini" in out
    assert "gpt-4o-mini" in out


def test_gerar_rejects_extra_tokens(capsys):
    with pytest.raises(SystemExit) as se:
        main_mod.main(["gerar", "--out", "x.json"])
    assert se.value.code == 2
    err = capsys.readouterr().err
    assert "não aceita argumentos extras" in err


def test_argparse_path_does_not_invoke_wizard(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    out = tmp_path / "cli.json"
    called = {"wizard": False, "run": False}

    def fake_run(request, out_path, max_retries=None):
        called["run"] = True
        assert request.quantidade == 3

    def boom_wizard(**kwargs):
        called["wizard"] = True
        raise AssertionError("wizard must not run on argparse path")

    with (
        patch.object(main_mod, "run", side_effect=fake_run),
        patch("wizard.run_wizard", side_effect=boom_wizard),
    ):
        main_mod.main(["--out", str(out), "--provider", "openai"])

    assert called["run"] is True
    assert called["wizard"] is False


def test_provider_enter_leaves_unset(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    captured: dict = {}

    def fake_run(request, out_path, max_retries=None):
        captured["provider"] = os.environ.get("LLM_PROVIDER")
        captured["reasoning"] = os.environ.get("LLM_REASONING_EFFORT")

    with (
        patch.object(main_mod, "run", side_effect=fake_run),
        patch.object(wizard, "is_interactive_stdin", return_value=True),
        patch(
            "builtins.input",
            side_effect=["", "", "", "", "", "", "out.json"],
        ),
    ):
        main_mod.main(["gerar"])

    assert captured["provider"] is None
    assert captured["reasoning"] == "medium"


def test_invalid_dificuldade_quantidade_reasoning_reprompt(capsys):
    answers = wizard.collect_wizard_answers(
        input_fn=_scripted_input(
            [
                "",  # topico default
                "",  # materia default
                "hard",  # invalid dificuldade
                "medio",
                "99",  # invalid quantidade
                "2",
                "",  # provider auto
                "turbo",  # invalid reasoning
                "low",
                "ok.json",
            ]
        ),
        isatty_fn=lambda: True,
    )
    assert answers.dificuldade == "medio"
    assert answers.quantidade == 2
    assert answers.reasoning == "low"
    assert answers.out_path == "ok.json"
    err = capsys.readouterr().err
    assert "Dificuldade inválida" in err
    assert "Quantidade inválida" in err
    assert "Reasoning inválido" in err


def test_no_profile_or_max_retries_prompts(capsys):
    wizard.collect_wizard_answers(
        input_fn=_scripted_input(["", "", "", "", "", "", "x.json"]),
        isatty_fn=lambda: True,
    )
    out = capsys.readouterr().out.lower()
    assert "max-retries" not in out
    assert "max_retries" not in out
    assert "profile" not in out
