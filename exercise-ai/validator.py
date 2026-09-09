"""Validator module for semantic post-parse exercise batch checks."""

from __future__ import annotations

import json
import sys

from math_check import check_math_batch
from models import ExerciseBatch, GenerationRequest

# Change this constant to switch report behavior: "all" | "first_exercise"
VALIDATION_REPORT_MODE: str = "all"

_FIELD_NAMES = ("enunciado", "resposta", "explicacao")


def _log_validation_failure(summary: str, batch: object) -> None:
    """Write detailed [VALIDAÇÃO] log + raw batch JSON to stderr (never API keys)."""
    print(f"[VALIDAÇÃO] {summary}", file=sys.stderr)
    if isinstance(batch, ExerciseBatch):
        raw = json.dumps(batch.model_dump(), ensure_ascii=False, indent=2)
    else:
        raw = json.dumps(batch, ensure_ascii=False, indent=2, default=str)
    print(raw, file=sys.stderr)


def validate_exercise_batch(batch: ExerciseBatch, request: GenerationRequest) -> ExerciseBatch:
    """Validate semantic structure of an already-parsed ExerciseBatch (D-01–D-08)."""
    errors: list[str] = []

    if not isinstance(batch, ExerciseBatch):
        msg = "O lote retornado não é uma instância válida de ExerciseBatch."
        _log_validation_failure(msg, batch)
        raise ValueError(msg)

    if not hasattr(batch, "exercicios"):
        errors.append("Chave 'exercicios' ausente ou inválida.")
    else:
        exercicios = batch.exercicios
        if not isinstance(exercicios, list):
            errors.append("Chave 'exercicios' ausente ou inválida.")
        elif len(exercicios) == 0:
            errors.append("A lista de exercícios retornada está vazia.")
        else:
            n = len(exercicios)
            if n != request.quantidade:
                errors.append(
                    f"quantidade incorreta: esperado {request.quantidade} exercícios, "
                    f"recebido {n}"
                )

            for i, ex in enumerate(exercicios):
                exercise_errors: list[str] = []
                for field in _FIELD_NAMES:
                    value = getattr(ex, field, "")
                    if not str(value).strip():
                        exercise_errors.append(f"exercicios[{i}].{field} está vazio")
                if exercise_errors:
                    errors.extend(exercise_errors)
                    if VALIDATION_REPORT_MODE == "first_exercise":
                        break

    if errors:
        user_message = "; ".join(errors)
        _log_validation_failure(user_message, batch)
        raise ValueError(user_message)

    check_math_batch(batch)
    return batch
