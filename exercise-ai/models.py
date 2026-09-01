"""Data schemas and models for exercise generation."""

from enum import Enum
from pydantic import BaseModel, Field


class DificuldadeEnum(str, Enum):
    """Níveis de dificuldade permitidos para geração de exercícios."""
    FACIL = "facil"
    MEDIO = "medio"
    DIFICIL = "dificil"


class GenerationRequest(BaseModel):
    """Parâmetros de entrada para solicitação de geração de exercícios."""
    materia: str = Field(default="Matemática", description="Matéria dos exercícios")
    topico: str = Field(..., description="Tópico específico da matéria")
    dificuldade: DificuldadeEnum = Field(..., description="Nível de dificuldade")
    quantidade: int = Field(..., gt=0, description="Quantidade exata de exercícios a gerar")


class Exercise(BaseModel):
    """Estrutura de um exercício individual."""
    enunciado: str = Field(..., description="Texto do enunciado do exercício")
    resposta: str = Field(..., description="Resposta correta ou solução direta")
    explicacao: str = Field(..., description="Explicação passo a passo da resolução")


class ExerciseBatch(BaseModel):
    """Lote contendo a lista de exercícios gerados."""
    exercicios: list[Exercise] = Field(..., description="Lista de exercícios gerados")
