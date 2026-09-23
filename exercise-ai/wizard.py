"""Interactive Portuguese CLI wizard activated by first token ``gerar``."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable

from models import DificuldadeEnum, GenerationRequest

# Tip strings (D-10); reasoning tip must include both halves of D-09.
TIP_TOPICO = (
    'Ex.: Equação do primeiro grau. Enter = "Equação do primeiro grau".'
)
TIP_MATERIA = 'Ex.: Matemática. Enter = "Matemática".'
TIP_DIFICULDADE = "Digite facil, medio ou dificil. Enter = facil."
TIP_QUANTIDADE = "Inteiro 1–40. Enter = 3."
TIP_PROVIDER = (
    "openai, gemini ou grok (precisa da chave no .env). "
    "Enter = auto-detect pela chave."
)
TIP_REASONING = (
    'none / low / medium / high — quanto o modelo "pensa". Enter = medium. '
    "Grok/Gemini honram o nível; OpenAI gpt-4o-mini pode ignorar."
)
TIP_OUT = (
    "Arquivo de saída, ex.: exercicios.json ou pasta/saida.json. "
    "Obrigatório ter um caminho válido."
)

_NON_TTY_MSG = (
    "O wizard 'gerar' requer um terminal interativo (TTY). "
    "Use as flags argparse para CI/scripts."
)
_EXTRA_ARGS_MSG = (
    "O comando 'gerar' não aceita argumentos extras. "
    "Use apenas: python exercise-ai/main.py gerar"
)

_VALID_DIFICULDADE = frozenset({"facil", "medio", "dificil"})
_VALID_PROVIDER = frozenset({"openai", "gemini", "grok"})
_VALID_REASONING = frozenset({"none", "low", "medium", "high", "xhigh", "max"})


@dataclass(frozen=True)
class WizardAnswers:
    """Collected wizard fields ready for GenerationRequest + env + out path."""

    materia: str
    topico: str
    dificuldade: str
    quantidade: int
    provider: str | None
    reasoning: str
    out_path: str


def is_interactive_stdin(
    isatty_fn: Callable[[], bool] | None = None,
) -> bool:
    """Return True when stdin is a TTY (D-03)."""
    check = isatty_fn if isatty_fn is not None else sys.stdin.isatty
    return bool(check())


def _print_prompt(question: str, tip: str) -> None:
    """Print question then tip on stdout (D-10)."""
    print(question)
    print(tip)


def _ask_text(
    question: str,
    tip: str,
    *,
    default: str,
    input_fn: Callable[[], str],
) -> str:
    _print_prompt(question, tip)
    raw = input_fn().strip()
    return raw if raw else default


def _ask_dificuldade(
    *,
    default: str,
    input_fn: Callable[[], str],
) -> str:
    while True:
        _print_prompt("Dificuldade:", TIP_DIFICULDADE)
        raw = input_fn().strip().lower()
        if not raw:
            return default
        if raw in _VALID_DIFICULDADE:
            return raw
        print(
            f"Dificuldade inválida '{raw}': use facil, medio ou dificil.",
            file=sys.stderr,
        )


def _ask_quantidade(
    *,
    default: int,
    max_qty: int,
    input_fn: Callable[[], str],
) -> int:
    while True:
        _print_prompt("Quantidade:", TIP_QUANTIDADE)
        raw = input_fn().strip()
        if not raw:
            return default
        try:
            qty = int(raw)
        except ValueError:
            print(
                f"Quantidade inválida '{raw}': informe um inteiro entre 1 e {max_qty}.",
                file=sys.stderr,
            )
            continue
        if qty < 1 or qty > max_qty:
            print(
                f"Quantidade inválida '{qty}': use um inteiro entre 1 e {max_qty}.",
                file=sys.stderr,
            )
            continue
        return qty


def _ask_provider(*, input_fn: Callable[[], str]) -> str | None:
    while True:
        _print_prompt("Provedor:", TIP_PROVIDER)
        raw = input_fn().strip().lower()
        if not raw:
            return None
        if raw in _VALID_PROVIDER:
            return raw
        print(
            f"Provedor inválido '{raw}': use openai, gemini ou grok.",
            file=sys.stderr,
        )


def _ask_reasoning(*, input_fn: Callable[[], str]) -> str:
    while True:
        _print_prompt("Reasoning:", TIP_REASONING)
        raw = input_fn().strip().lower()
        if not raw:
            return "medium"
        if raw in _VALID_REASONING:
            return raw
        print(
            f"Reasoning inválido '{raw}': use none, low, medium ou high.",
            file=sys.stderr,
        )


def _ask_out_path(*, input_fn: Callable[[], str]) -> str:
    while True:
        _print_prompt("Nome do JSON (--out):", TIP_OUT)
        raw = input_fn().strip()
        if raw:
            return raw
        print(
            "Caminho do JSON obrigatório. Informe um arquivo de saída.",
            file=sys.stderr,
        )


def collect_wizard_answers(
    *,
    input_fn: Callable[[], str] | None = None,
    isatty_fn: Callable[[], bool] | None = None,
) -> WizardAnswers:
    """Run the locked 7-question flow (D-04); raise SystemExit on non-TTY (D-03)."""
    import main as main_mod

    if not is_interactive_stdin(isatty_fn):
        print(_NON_TTY_MSG, file=sys.stderr)
        raise SystemExit(1)

    read = input_fn if input_fn is not None else input

    materia = _ask_text(
        "Matéria:",
        TIP_MATERIA,
        default=main_mod._DEFAULT_MATERIA,
        input_fn=read,
    )
    topico = _ask_text(
        "Tipo de exercício (tópico):",
        TIP_TOPICO,
        default=main_mod._DEFAULT_TOPICO,
        input_fn=read,
    )
    dificuldade = _ask_dificuldade(
        default=main_mod._DEFAULT_DIFICULDADE,
        input_fn=read,
    )
    quantidade = _ask_quantidade(
        default=main_mod._DEFAULT_QUANTIDADE,
        max_qty=main_mod._MAX_QUANTIDADE,
        input_fn=read,
    )
    provider = _ask_provider(input_fn=read)
    reasoning = _ask_reasoning(input_fn=read)
    out_path = _ask_out_path(input_fn=read)

    return WizardAnswers(
        materia=materia,
        topico=topico,
        dificuldade=dificuldade,
        quantidade=quantidade,
        provider=provider,
        reasoning=reasoning,
        out_path=out_path,
    )


def run_wizard(
    *,
    input_fn: Callable[[], str] | None = None,
    isatty_fn: Callable[[], bool] | None = None,
) -> None:
    """Collect answers, set env, and call ``main.run`` (D-14; D-15)."""
    import os

    import main as main_mod

    answers = collect_wizard_answers(input_fn=input_fn, isatty_fn=isatty_fn)

    if answers.provider:
        os.environ["LLM_PROVIDER"] = answers.provider
        try:
            main_mod._ensure_provider_key(answers.provider)
        except ValueError as err:
            print(str(err), file=sys.stderr)
            raise SystemExit(1) from err

    os.environ["LLM_REASONING_EFFORT"] = answers.reasoning

    request = GenerationRequest(
        materia=answers.materia,
        topico=answers.topico,
        dificuldade=DificuldadeEnum(answers.dificuldade),
        quantidade=answers.quantidade,
    )
    main_mod.run(request, out_path=answers.out_path, max_retries=None)
