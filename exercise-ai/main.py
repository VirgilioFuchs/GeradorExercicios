"""CLI entry point and pipeline orchestrator for exercise generation."""

import json
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


def run_demo() -> None:
    """Executa o pipeline linear completo de demonstração."""
    # Parâmetros de demonstração canônicos especificados no AGENT.md
    request = GenerationRequest(
        materia="Matemática",
        topico="Equação do primeiro grau",
        dificuldade=DificuldadeEnum.FACIL,
        quantidade=3,
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

    except ValueError as val_err:
        print(str(val_err), file=sys.stderr)
        sys.exit(1)
    except RuntimeError as run_err:
        print(str(run_err), file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_demo()
