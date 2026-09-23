"""Interactive Portuguese CLI wizard activated by first token ``gerar``."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable

from models import GenerationRequest

# Tip strings (D-10); reasoning tip must include both halves of D-09.
TIP_TOPICO = (
    'Ex.: Equação do primeiro grau. Enter = "Equação do primeiro grau".'
)
TIP_MATERIA = 'Ex.: Matemática. Enter = "Matemática".'
TIP_FACIL = "Quantos fáceis? Inteiro ≥0. Enter = 0."
TIP_MEDIO = "Quantos médios? Inteiro ≥0. Enter = 0."
TIP_DIFICIL = "Quantos difíceis? Inteiro ≥0. Enter = 0."
TIP_QUANTIDADE = (
    "Inteiro 1–40 (aviso se ≠ soma das faixas). Enter = 3 ou a soma se faixas >0."
)
TIP_PROVIDER = (
    "openai, gemini ou grok (precisa da chave no .env). "
    "Enter = auto-detect pela chave."
)
TIP_REASONING = (
    'none / low / medium / high / xhigh / max — quanto o modelo "pensa". '
    "Enter = medium. Grok/Gemini honram o nível; OpenAI gpt-4o-mini pode ignorar."
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

_VALID_PROVIDER = frozenset({"openai", "gemini", "grok"})
_VALID_REASONING = frozenset({"none", "low", "medium", "high", "xhigh", "max"})


@dataclass(frozen=True)
class WizardAnswers:
    """Collected wizard fields ready for GenerationRequest + env + out path."""

    materia: str
    topico: str
    facil: int
    medio: int
    dificil: int
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


def _ask_band_count(
    question: str,
    tip: str,
    *,
    default: int,
    input_fn: Callable[[], str],
) -> int:
    while True:
        _print_prompt(question, tip)
        raw = input_fn().strip()
        if not raw:
            return default
        try:
            n = int(raw)
        except ValueError:
            print(
                f"Contagem inválida '{raw}': informe um inteiro ≥0.",
                file=sys.stderr,
            )
            continue
        if n < 0:
            print(
                f"Contagem inválida '{n}': use um inteiro ≥0.",
                file=sys.stderr,
            )
            continue
        return n


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
            f"Reasoning inválido '{raw}': use none, low, medium, high, xhigh ou max.",
            file=sys.stderr,
        )


def _ask_out_path(*, input_fn: Callable[[], str]) -> str:
    while True:
        _print_prompt("Arquivo de saída (--out):", TIP_OUT)
        raw = input_fn().strip()
        if raw:
            return raw
        print("Informe um caminho de arquivo JSON.", file=sys.stderr)


def collect_wizard_answers(
    *,
    input_fn: Callable[[], str] | None = None,
    isatty_fn: Callable[[], bool] | None = None,
) -> WizardAnswers:
    """Prompt operator for generation parameters (Phase 15 band UX)."""
    import main as main_mod

    if not is_interactive_stdin(isatty_fn=isatty_fn):
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
    facil = _ask_band_count("Fáceis:", TIP_FACIL, default=0, input_fn=read)
    medio = _ask_band_count("Médios:", TIP_MEDIO, default=0, input_fn=read)
    dificil = _ask_band_count("Difíceis:", TIP_DIFICIL, default=0, input_fn=read)
    band_sum = facil + medio + dificil
    qty_default = band_sum if band_sum > 0 else main_mod._DEFAULT_QUANTIDADE
    quantidade = _ask_quantidade(
        default=qty_default,
        max_qty=main_mod._MAX_QUANTIDADE,
        input_fn=read,
    )
    provider = _ask_provider(input_fn=read)
    reasoning = _ask_reasoning(input_fn=read)
    out_path = _ask_out_path(input_fn=read)

    return WizardAnswers(
        materia=materia,
        topico=topico,
        facil=facil,
        medio=medio,
        dificil=dificil,
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
    import plan_ux

    answers = collect_wizard_answers(input_fn=input_fn, isatty_fn=isatty_fn)

    if answers.provider:
        os.environ["LLM_PROVIDER"] = answers.provider
        try:
            main_mod._ensure_provider_key(answers.provider)
        except ValueError as err:
            print(str(err), file=sys.stderr)
            raise SystemExit(1) from err

    os.environ["LLM_REASONING_EFFORT"] = answers.reasoning

    plan_ux.soft_warn_bands(
        answers.facil,
        answers.medio,
        answers.dificil,
        answers.quantidade,
    )
    try:
        plan_kw = plan_ux.build_request_kwargs(
            answers.facil,
            answers.medio,
            answers.dificil,
            quantidade_field=answers.quantidade,
        )
    except ValueError as err:
        print(str(err), file=sys.stderr)
        raise SystemExit(1) from err

    request = GenerationRequest(
        materia=answers.materia,
        topico=answers.topico,
        **plan_kw,
    )
    main_mod.run(request, out_path=answers.out_path, max_retries=None)
