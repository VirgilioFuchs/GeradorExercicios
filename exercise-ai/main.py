"""CLI entry point and pipeline orchestrator for exercise generation."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Ensure local package path resolution
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Multi-path .env resolution (exercise-ai/.env or root/.env)
env_path = current_dir / ".env"
if not env_path.exists():
    env_path = current_dir.parent / ".env"
load_dotenv(dotenv_path=env_path)

from models import DificuldadeEnum, ExerciseBatch, GenerationRequest
from generator import generate_exercises
from validator import validate_exercise_batch

logger = logging.getLogger("exercise_ai")

_DEFAULT_MATERIA = "Matemática"
_DEFAULT_TOPICO = "Equação do primeiro grau"
_DEFAULT_DIFICULDADE = "facil"
_DEFAULT_QUANTIDADE = 3
_MAX_QUANTIDADE = 40


class _StderrStream:
    """Always write to the current sys.stderr (works under redirect_stderr)."""

    def write(self, msg: str) -> int:
        return sys.stderr.write(msg)

    def flush(self) -> None:
        sys.stderr.flush()


def _configure_logging() -> None:
    """Send development LOG-01 events to stderr (no log files)."""
    if logger.handlers:
        return
    handler = logging.StreamHandler(_StderrStream())
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def format_batch_text(batch: ExerciseBatch) -> str:
    """Render D-15 human-readable stdout layout for a validated batch."""
    blocks: list[str] = []
    for i, ex in enumerate(batch.exercicios, start=1):
        blocks.append(
            "\n".join(
                [
                    f"### Exercício {i}",
                    f"Enunciado: {ex.enunciado}",
                    f"Resposta: {ex.resposta}",
                    f"Explicação: {ex.explicacao}",
                ]
            )
        )
    return "\n\n".join(blocks)


def _ensure_provider_key(provider: str) -> None:
    """Fail with a provider-specific PT message when the chosen key is missing (D-11)."""
    if provider == "openai":
        if not os.getenv("LLM_API_KEY", "").strip():
            raise ValueError(
                "Chave ausente para o provedor openai. Defina LLM_API_KEY no arquivo .env."
            )
    elif provider == "gemini":
        if not os.getenv("GEMINI_API_KEY", "").strip():
            raise ValueError(
                "Chave ausente para o provedor gemini. Defina GEMINI_API_KEY no arquivo .env."
            )


def _positive_quantidade(value: str) -> int:
    """Parse --quantidade; reject non-int, <=0, and >40 before any LLM call."""
    try:
        qty = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"quantidade inválida '{value}': informe um inteiro entre 1 e {_MAX_QUANTIDADE}."
        ) from exc
    if qty <= 0 or qty > _MAX_QUANTIDADE:
        raise argparse.ArgumentTypeError(
            f"quantidade inválida '{qty}': o máximo 40 exercícios é permitido (1–{_MAX_QUANTIDADE})."
        )
    return qty


def build_parser() -> argparse.ArgumentParser:
    """Portuguese argparse surface for CLI-04 (D-01..D-20)."""
    parser = argparse.ArgumentParser(
        prog="main.py",
        description=(
            "Gera exercícios de matemática via LLM. "
            f"Defaults da demo quando omitidos: matéria={_DEFAULT_MATERIA}; "
            f"tópico={_DEFAULT_TOPICO}; dificuldade={_DEFAULT_DIFICULDADE}; "
            f"quantidade={_DEFAULT_QUANTIDADE}."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--materia",
        default=_DEFAULT_MATERIA,
        help=f"Matéria dos exercícios (padrão: {_DEFAULT_MATERIA})",
    )
    parser.add_argument(
        "--topico",
        default=_DEFAULT_TOPICO,
        help=f"Tópico específico (padrão: {_DEFAULT_TOPICO})",
    )
    parser.add_argument(
        "--dificuldade",
        choices=["facil", "medio", "dificil"],
        default=_DEFAULT_DIFICULDADE,
        help=f"Nível de dificuldade: facil|medio|dificil (padrão: {_DEFAULT_DIFICULDADE})",
    )
    parser.add_argument(
        "--quantidade",
        type=_positive_quantidade,
        default=_DEFAULT_QUANTIDADE,
        help=f"Quantidade de exercícios (1–{_MAX_QUANTIDADE}; padrão: {_DEFAULT_QUANTIDADE})",
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "gemini"],
        default=None,
        help="Provedor LLM para esta execução: openai|gemini (opcional)",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Caminho obrigatório do arquivo JSON de saída",
    )
    return parser


def run(request: GenerationRequest, out_path: Path | str) -> None:
    """Executa o pipeline: gerar → validar → texto no stdout + JSON em out_path."""
    _configure_logging()

    logger.info("Início da geração de exercícios")
    logger.info(
        "Parâmetros: materia=%s topico=%s dificuldade=%s quantidade=%s",
        request.materia,
        request.topico,
        request.dificuldade.value,
        request.quantidade,
    )

    try:
        print("Gerando…", file=sys.stderr)
        batch = generate_exercises(request)

        print("Validando…", file=sys.stderr)
        validated_batch = validate_exercise_batch(batch, request)

        print(format_batch_text(validated_batch))
        out = Path(out_path)
        out.write_text(
            json.dumps(
                validated_batch.model_dump(),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        logger.info("Geração concluída com sucesso")

    except ValueError as val_err:
        logger.error("Falha de validação ou configuração: %s", val_err)
        print(str(val_err), file=sys.stderr)
        sys.exit(1)
    except RuntimeError as run_err:
        logger.error("Falha na geração: %s", run_err)
        print(str(run_err), file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        logger.error("Falha inesperada: %s", exc)
        print(str(exc), file=sys.stderr)
        sys.exit(1)


def main(argv: list[str] | None = None) -> None:
    """Parse CLI args and run the generation pipeline."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.provider:
        os.environ["LLM_PROVIDER"] = args.provider
        try:
            _ensure_provider_key(args.provider)
        except ValueError as err:
            print(str(err), file=sys.stderr)
            sys.exit(1)

    request = GenerationRequest(
        materia=args.materia,
        topico=args.topico,
        dificuldade=DificuldadeEnum(args.dificuldade),
        quantidade=args.quantidade,
    )
    run(request, out_path=args.out)


if __name__ == "__main__":
    main()
