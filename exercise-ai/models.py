"""Data schemas and models for exercise generation."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class DificuldadeEnum(str, Enum):
    """Níveis de dificuldade permitidos para geração de exercícios."""

    FACIL = "facil"
    MEDIO = "medio"
    DIFICIL = "dificil"


MAX_QUANTIDADE = 40

_BAND_ORDER: tuple[DificuldadeEnum, ...] = (
    DificuldadeEnum.FACIL,
    DificuldadeEnum.MEDIO,
    DificuldadeEnum.DIFICIL,
)


class ExerciseSpec(BaseModel):
    """Especificação por exercício (faixa de dificuldade)."""

    dificuldade: DificuldadeEnum


class PlanoDificuldade(BaseModel):
    """Contagens por faixa: fácil → médio → difícil."""

    facil: int = Field(0, ge=0)
    medio: int = Field(0, ge=0)
    dificil: int = Field(0, ge=0)

    def expand(self) -> list[ExerciseSpec]:
        """Ordena specs: todos fáceis, depois médios, depois difíceis (D-02)."""
        specs: list[ExerciseSpec] = []
        for band, count in (
            (DificuldadeEnum.FACIL, self.facil),
            (DificuldadeEnum.MEDIO, self.medio),
            (DificuldadeEnum.DIFICIL, self.dificil),
        ):
            specs.extend(ExerciseSpec(dificuldade=band) for _ in range(count))
        return specs


def _band_summary(specs: list[ExerciseSpec]) -> list[DificuldadeEnum]:
    """Faixas presentes, ordenadas fácil→médio→difícil (D-04)."""
    present = {spec.dificuldade for spec in specs}
    return [b for b in _BAND_ORDER if b in present]


class GenerationRequest(BaseModel):
    """Parâmetros de entrada para solicitação de geração de exercícios."""

    materia: str = Field(default="Matemática", description="Matéria dos exercícios")
    topico: str = Field(..., min_length=1, description="Tópico específico da matéria")
    dificuldade: DificuldadeEnum | None = Field(
        default=None, description="Nível de dificuldade (uniforme / compat)"
    )
    quantidade: int = Field(
        ...,
        ge=1,
        le=MAX_QUANTIDADE,
        description="Quantidade exata de exercícios a gerar",
    )
    dificuldades: list[DificuldadeEnum] | None = Field(
        default=None, description="Resumo das faixas usadas (1–3)"
    )
    plano: PlanoDificuldade | None = Field(
        default=None, description="Contagens por faixa (misto)"
    )
    itens: list[ExerciseSpec] | None = Field(
        default=None, description="Specs ordenados explícitos (misto)"
    )

    @field_validator("topico", mode="before")
    @classmethod
    def _strip_nonempty_topico(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("topico não pode ser vazio")
            return stripped
        return value

    @model_validator(mode="after")
    def _normalize_plan(self) -> GenerationRequest:
        has_plano = self.plano is not None
        has_itens = self.itens is not None

        # D-03: XOR of plan sources
        if has_plano and has_itens:
            raise ValueError("plano e itens são mutuamente exclusivos (XOR)")

        if has_plano:
            assert self.plano is not None
            specs = self.plano.expand()
            if len(specs) != self.quantidade:
                raise ValueError(
                    f"quantidade ({self.quantidade}) deve ser igual ao tamanho do "
                    f"plano ({len(specs)})"
                )
            self.itens = specs
        elif has_itens:
            assert self.itens is not None
            specs = list(self.itens)
            if len(specs) != self.quantidade:
                raise ValueError(
                    f"quantidade ({self.quantidade}) deve ser igual ao tamanho de "
                    f"itens ({len(specs)})"
                )
        elif self.dificuldade is not None:
            # D-05 / D-06: uniform via scalar — one band, qty slots for Phase 14
            specs = [
                ExerciseSpec(dificuldade=self.dificuldade)
                for _ in range(self.quantidade)
            ]
            # Keep itens None so uniform stays distinguishable from mixed
        elif self.dificuldades is not None and len(self.dificuldades) == 1:
            band = self.dificuldades[0]
            specs = [ExerciseSpec(dificuldade=band) for _ in range(self.quantidade)]
            if self.dificuldade is None:
                self.dificuldade = band
        else:
            raise ValueError(
                "informe dificuldade (uniforme), dificuldades (1 faixa), plano ou itens"
            )

        object.__setattr__(self, "_ordered_specs", specs)

        # D-04: band summary fácil→médio→difícil among present
        summary = _band_summary(specs)
        self.dificuldades = summary

        # Prompt compat: scalar dificuldade = first band when missing
        if self.dificuldade is None:
            self.dificuldade = summary[0]

        return self

    @property
    def itens_ordenados(self) -> list[ExerciseSpec]:
        """Specs ordenados pós-normalização (sempre len == quantidade)."""
        cached: list[ExerciseSpec] | None = getattr(self, "_ordered_specs", None)
        if cached is not None:
            return cached
        if self.itens is not None:
            return list(self.itens)
        if self.dificuldade is not None:
            return [
                ExerciseSpec(dificuldade=self.dificuldade)
                for _ in range(self.quantidade)
            ]
        return []


class Exercise(BaseModel):
    """Estrutura de um exercício individual."""

    enunciado: str = Field(..., description="Texto do enunciado do exercício")
    resposta: str = Field(..., description="Resposta correta ou solução direta")
    explicacao: str = Field(..., description="Explicação passo a passo da resolução")
    dificuldade: DificuldadeEnum = Field(
        ..., description="Faixa de dificuldade ecoada (D-09)"
    )


class ExerciseBatch(BaseModel):
    """Lote contendo a lista de exercícios gerados."""

    exercicios: list[Exercise] = Field(..., description="Lista de exercícios gerados")
    dificuldades: list[DificuldadeEnum] = Field(
        ..., description="Resumo das faixas ecoadas (D-10)"
    )


def verify_plan_echo(batch: ExerciseBatch, request: GenerationRequest) -> None:
    """Compara dificuldade de cada exercício ao slot ordenado; falha sem corrigir (D-11)."""
    expected = [s.dificuldade for s in request.itens_ordenados]
    if len(batch.exercicios) != len(expected):
        raise ValueError(
            f"tamanho do batch ({len(batch.exercicios)}) != slots do plano ({len(expected)})"
        )
    for i, (ex, band) in enumerate(zip(batch.exercicios, expected)):
        if ex.dificuldade != band:
            raise ValueError(
                f"echo mismatch no slot {i}: esperado {band.value}, "
                f"obtido {ex.dificuldade.value}"
            )
