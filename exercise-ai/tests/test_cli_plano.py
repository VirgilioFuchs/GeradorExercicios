"""Offline CLI tests for --plano (Phase 15)."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from models import DificuldadeEnum

import main as main_mod


def test_cli_plano_mixed(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    captured: dict = {}

    def fake_run(request, out_path, max_retries=None):
        captured["request"] = request

    out = tmp_path / "o.json"
    with patch.object(main_mod, "run", side_effect=fake_run):
        main_mod.main(
            [
                "--topico",
                "eq",
                "--plano",
                "2,3,0",
                "--out",
                str(out),
            ]
        )
    req = captured["request"]
    assert req.plano is not None
    assert req.plano.facil == 2 and req.plano.medio == 3
    assert req.quantidade == 5
    assert req.dificuldade is None or req.plano is not None


def test_cli_plano_uniform(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    captured: dict = {}

    def fake_run(request, out_path, max_retries=None):
        captured["request"] = request

    with patch.object(main_mod, "run", side_effect=fake_run):
        main_mod.main(
            ["--topico", "eq", "--plano", "0,4,0", "--out", str(tmp_path / "u.json")]
        )
    req = captured["request"]
    assert req.plano is None
    assert req.dificuldade == DificuldadeEnum.MEDIO
    assert req.quantidade == 4


def test_cli_plano_invalid_exits(capsys, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    with pytest.raises(SystemExit) as se:
        main_mod.main(["--topico", "eq", "--plano", "1,2", "--out", "x.json"])
    assert se.value.code == 2
    assert "plano" in capsys.readouterr().err.lower()


def test_cli_legacy_without_plano(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    captured: dict = {}

    def fake_run(request, out_path, max_retries=None):
        captured["request"] = request

    with patch.object(main_mod, "run", side_effect=fake_run):
        main_mod.main(
            [
                "--topico",
                "eq",
                "--dificuldade",
                "facil",
                "--quantidade",
                "3",
                "--out",
                str(tmp_path / "l.json"),
            ]
        )
    req = captured["request"]
    assert req.plano is None
    assert req.dificuldade == DificuldadeEnum.FACIL
    assert req.quantidade == 3
