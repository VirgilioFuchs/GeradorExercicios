"""CLI entry point and pipeline orchestrator for exercise generation."""

import json
import logging
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

from models import DificuldadeEnum, GenerationRequest
from generator import generate_exercises
from validator import validate_exercise_batch

logger = logging.getLogger("exercise_ai")


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


def run_demo() -> None:
    """Executa o pipeline linear completo de demonstração."""
    _configure_logging()

    # Parâmetros de demonstração canônicos especificados no AGENT.md
    request = GenerationRequest(
        materia="Matemática",
        topico="Equação do primeiro grau",
        dificuldade=DificuldadeEnum.FACIL,
        quantidade=3,
    )

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

        output_json = json.dumps(
            validated_batch.model_dump(),
            indent=2,
            ensure_ascii=False,
        )
        print(output_json)
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


if __name__ == "__main__":
    run_demo()
