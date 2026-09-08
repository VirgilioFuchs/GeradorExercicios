#!/usr/bin/env python3
"""Captura saídas de erro/sucesso — argparse (local) + Gemini ao vivo.

Uso (raiz do repo):
    python capturar_saida_erros.py              # só mocks/CLI (rápido)
    python capturar_saida_erros.py --live-gemini  # + chamadas reais ao Gemini

Gera: saida_erros.txt (sobrescreve)
Nunca grava valores de API keys no arquivo.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import os
import re
import sys
import tempfile
import time
import traceback
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
OUT_FILE = ROOT / "saida_erros.txt"
AI = ROOT / "exercise-ai"
if str(AI) not in sys.path:
    sys.path.insert(0, str(AI))

# Carrega .env antes dos imports que leem env em runtime
from dotenv import load_dotenv

_env = AI / ".env"
if not _env.exists():
    _env = ROOT / ".env"
load_dotenv(dotenv_path=_env)

import main  # noqa: E402
from models import (  # noqa: E402
    DificuldadeEnum,
    Exercise,
    ExerciseBatch,
    GenerationRequest,
)


def _redact(text: str) -> str:
    """Remove valores de chaves do texto capturado."""
    for name in ("LLM_API_KEY", "GEMINI_API_KEY"):
        val = os.getenv(name, "")
        if val and val.strip() and val in text:
            text = text.replace(val, "[REDACTED]")
    # formatos comuns se vazaram parcialmente
    text = re.sub(r"AIza[0-9A-Za-z_\-]{10,}", "AIza[REDACTED]", text)
    text = re.sub(r"sk-[A-Za-z0-9_\-]{10,}", "sk-[REDACTED]", text)
    return text


def _batch(n: int = 3) -> ExerciseBatch:
    return ExerciseBatch(
        exercicios=[
            Exercise(enunciado=f"e{i}", resposta=f"r{i}", explicacao=f"x{i}")
            for i in range(1, n + 1)
        ]
    )


def _request(qty: int = 3) -> GenerationRequest:
    return GenerationRequest(
        materia="Matemática",
        topico="Equação do primeiro grau",
        dificuldade=DificuldadeEnum.FACIL,
        quantidade=qty,
    )


def _section(title: str, lines: list[str]) -> str:
    bar = "=" * 72
    return f"{bar}\n{title}\n{bar}\n" + "\n".join(lines) + "\n\n"


def _fmt(result: dict) -> list[str]:
    return [
        f"exit={result['exit']}",
        f"--out escrito={result.get('out_file_written', 'n/a')}",
        "--- stdout ---",
        _redact(result["stdout"]).strip() or "(vazio)",
        "--- stderr ---",
        _redact(result["stderr"]).strip() or "(vazio)",
    ]


def _capture_cli(argv: list[str]) -> dict:
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            main.main(argv)
        except SystemExit as se:
            code = int(se.code) if se.code is not None else 0
    return {"exit": code, "stdout": out.getvalue(), "stderr": err.getvalue()}


def _capture_run(*, generate_side_effect, max_retries: int | None = 1) -> dict:
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with tempfile.TemporaryDirectory() as td:
        out_path = Path(td) / "out.json"
        with patch("reliability.generate_exercises", side_effect=generate_side_effect):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                try:
                    main.run(_request(), out_path=out_path, max_retries=max_retries)
                except SystemExit as se:
                    code = int(se.code) if se.code is not None else 0
        wrote = out_path.exists()
    return {
        "exit": code,
        "stdout": out.getvalue(),
        "stderr": err.getvalue(),
        "out_file_written": wrote,
    }


def _capture_live_cli(argv: list[str], *, env_overrides: dict | None = None) -> dict:
    """Chamada real à CLI (Gemini se --provider gemini / env)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    old = os.environ.copy()
    out_path = None
    try:
        if env_overrides:
            for k, v in env_overrides.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        # garantir path --out absoluto sob temp
        argv = list(argv)
        if "--out" in argv:
            i = argv.index("--out")
            out_path = Path(tempfile.mkdtemp()) / "live.json"
            argv[i + 1] = str(out_path)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                main.main(argv)
            except SystemExit as se:
                code = int(se.code) if se.code is not None else 0
        wrote = bool(out_path and out_path.exists())
    finally:
        os.environ.clear()
        os.environ.update(old)
    return {
        "exit": code,
        "stdout": out.getvalue(),
        "stderr": err.getvalue(),
        "out_file_written": wrote,
    }


def _capture_live_cli_flaky(
    argv: list[str],
    *,
    env_overrides: dict | None = None,
    attempts: int = 4,
    sleep_s: float = 2.0,
) -> dict:
    """Retry live CLI on transient Gemini 503 (API overload)."""
    last: dict | None = None
    for _ in range(attempts):
        last = _capture_live_cli(argv, env_overrides=env_overrides)
        if last["exit"] == 0:
            return last
        if "status=503" not in last["stderr"]:
            return last
        time.sleep(sleep_s)
    assert last is not None
    return last


def scenarios_cli_local() -> list[tuple[str, callable]]:
    return [
        ("L1. CLI — --out ausente", lambda: _capture_cli([])),
        (
            "L2. CLI — quantidade > 40",
            lambda: _capture_cli(["--quantidade", "41", "--out", "x.json"]),
        ),
        (
            "L3. CLI — --max-retries inválido",
            lambda: _capture_cli(["--max-retries", "9", "--out", "x.json"]),
        ),
        (
            "L4. CLI — dificuldade inválida",
            lambda: _capture_cli(["--dificuldade", "hard", "--out", "x.json"]),
        ),
        (
            "L5. CLI — provider inválido",
            lambda: _capture_cli(["--provider", "claude", "--out", "x.json"]),
        ),
    ]


def scenarios_mock_pipeline() -> list[tuple[str, callable]]:
    def exhaust_validation():
        bad = ExerciseBatch(
            exercicios=[
                Exercise(enunciado="e", resposta="", explicacao="x") for _ in range(3)
            ]
        )
        return _capture_run(generate_side_effect=[bad, bad], max_retries=1)

    def auth_permanent():
        auth = RuntimeError(
            "Falha de autenticação na API da OpenAI. Verifique LLM_API_KEY."
        )
        auth.retriable = False
        return _capture_run(generate_side_effect=auth, max_retries=2)

    def empty_choices_exhaust():
        err = RuntimeError(
            "A API da OpenAI retornou uma resposta sem opções (choices vazio)."
        )
        err.retriable = True
        return _capture_run(generate_side_effect=[err, err], max_retries=1)

    return [
        ("M1. Mock — validação esgota regenerações", exhaust_validation),
        ("M2. Mock — auth permanente (sem regen)", auth_permanent),
        ("M3. Mock — empty choices retriável esgotado", empty_choices_exhaust),
    ]


def scenarios_live_gemini() -> list[tuple[str, callable]]:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        return [
            (
                "G0. Gemini — PULADO (GEMINI_API_KEY ausente no .env)",
                lambda: {
                    "exit": -1,
                    "stdout": "",
                    "stderr": "Defina GEMINI_API_KEY em exercise-ai/.env",
                    "out_file_written": False,
                },
            )
        ]

    def success_one():
        return _capture_live_cli_flaky(
            [
                "--provider",
                "gemini",
                "--quantidade",
                "1",
                "--dificuldade",
                "facil",
                "--materia",
                "Matemática",
                "--topico",
                "Equação do primeiro grau",
                "--max-retries",
                "1",
                "--out",
                "PLACEHOLDER",
            ],
            env_overrides={"LLM_PROVIDER": "gemini"},
        )

    def missing_gemini_key():
        return _capture_live_cli(
            [
                "--provider",
                "gemini",
                "--quantidade",
                "1",
                "--out",
                "PLACEHOLDER",
            ],
            env_overrides={"GEMINI_API_KEY": None, "LLM_PROVIDER": "gemini"},
        )

    def bad_gemini_key():
        return _capture_live_cli(
            [
                "--provider",
                "gemini",
                "--quantidade",
                "1",
                "--max-retries",
                "0",
                "--out",
                "PLACEHOLDER",
            ],
            env_overrides={
                "GEMINI_API_KEY": "AIzaSyInvalidKeyForAuthTest00000000000",
                "LLM_PROVIDER": "gemini",
            },
        )

    def success_with_retry_budget():
        # Exercício real; regeneração só ocorre se validação falhar (pode ou não).
        return _capture_live_cli_flaky(
            [
                "--provider",
                "gemini",
                "--quantidade",
                "2",
                "--max-retries",
                "2",
                "--out",
                "PLACEHOLDER",
            ],
            env_overrides={"LLM_PROVIDER": "gemini"},
        )

    return [
        ("G1. Gemini LIVE — sucesso (1 exercício)", success_one),
        ("G2. Gemini LIVE — chave ausente (mensagem D-11)", missing_gemini_key),
        ("G3. Gemini LIVE — chave inválida (auth permanente)", bad_gemini_key),
        ("G4. Gemini LIVE — sucesso qty=2 max-retries=2", success_with_retry_budget),
    ]


def run_all(live_gemini: bool) -> None:
    scenarios: list[tuple[str, callable]] = []
    scenarios.extend(scenarios_cli_local())
    scenarios.extend(scenarios_mock_pipeline())
    if live_gemini:
        scenarios.extend(scenarios_live_gemini())

    chunks: list[str] = [
        _section(
            "CAPTURA DE ERROS / SAÍDAS — GeradorExercicios",
            [
                f"Gerado por: {Path(__file__).name}",
                f"Modo: {'CLI+mocks+Gemini LIVE' if live_gemini else 'CLI+mocks (sem LLM)'}",
                f"Saída: {OUT_FILE.name}",
                "Segredos redigidos com [REDACTED].",
            ],
        )
    ]

    for title, fn in scenarios:
        print(f"-> {title} ...", flush=True)
        try:
            result = fn()
            chunks.append(_section(title, _fmt(result)))
        except Exception:
            chunks.append(
                _section(title + " — FALHA AO CAPTURAR", [_redact(traceback.format_exc())])
            )

    OUT_FILE.write_text("".join(chunks), encoding="utf-8")
    print(f"\nEscrito: {OUT_FILE} ({len(scenarios)} cenários)")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Captura saídas de erro da CLI")
    p.add_argument(
        "--live-gemini",
        action="store_true",
        help="Inclui chamadas reais à API Google Gemini (usa GEMINI_API_KEY do .env)",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_all(live_gemini=args.live_gemini)
