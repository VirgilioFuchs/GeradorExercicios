"""Validator module for exercises.

Phase 1 provides a baseline validation stub / pass-through.
Comprehensive validation rules, count checks, and unit tests are implemented in Phase 2.
"""

from models import ExerciseBatch, GenerationRequest


def validate_exercise_batch(batch: ExerciseBatch, request: GenerationRequest) -> ExerciseBatch:
    """Valida a estrutura básica do lote de exercícios retornado.
    
    Verifica se o objeto é uma instância de ExerciseBatch e se contém exercícios não vazios.
    Na Fase 2, esta validação será estendida com regras semânticas e contagens estritas.
    """
    if not isinstance(batch, ExerciseBatch):
        raise ValueError("O lote retornado não é uma instância válida de ExerciseBatch.")

    if not batch.exercicios:
        raise ValueError("A lista de exercícios retornada está vazia.")

    return batch
