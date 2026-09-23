"""Band counts → GenerationRequest kwargs (demo / CLI / wizard parity)."""

from __future__ import annotations

import sys
from typing import Any

from models import DificuldadeEnum, PlanoDificuldade

_BAND_KEYS: tuple[str, ...] = ("facil", "medio", "dificil")


def parse_plano_csv(raw: str) -> tuple[int, int, int]:
    """Parse ``F,M,D`` (fácil→médio→difícil) into three non-negative ints."""
    text = (raw or "").strip()
    parts = [p.strip() for p in text.split(",")]
    if len(parts) != 3:
        raise ValueError(
            f"--plano inválido '{raw}': use F,M,D (ex.: 2,3,1) — "
            "três inteiros ≥0 em ordem fácil,médio,difícil."
        )
    out: list[int] = []
    for i, part in enumerate(parts):
        try:
            n = int(part)
        except ValueError as exc:
            raise ValueError(
                f"--plano inválido '{raw}': '{part}' não é inteiro "
                f"(posição {_BAND_KEYS[i]})."
            ) from exc
        if n < 0:
            raise ValueError(
                f"--plano inválido '{raw}': {_BAND_KEYS[i]}={n} deve ser ≥0."
            )
        out.append(n)
    return out[0], out[1], out[2]


def soft_warn_bands(
    facil: int,
    medio: int,
    dificil: int,
    quantidade_field: int,
    *,
    file=None,
) -> None:
    """Print soft warnings (demo D-11 parity); does not raise."""
    dest = file if file is not None else sys.stderr
    total = facil + medio + dificil
    if total == 0:
        print(
            "[aviso] soma das faixas = 0; GenerationRequest vai falhar na validação.",
            file=dest,
        )
    if total > 40:
        print(
            f"[aviso] soma das faixas = {total} > 40 (cap).",
            file=dest,
        )
    if total > 0 and quantidade_field != total:
        print(
            f"[aviso] quantidade={quantidade_field} ≠ soma das faixas={total}; "
            "o payload usa as regras de plano (misto→soma / uniforme→contagem da faixa).",
            file=dest,
        )


def build_request_kwargs(
    facil: int,
    medio: int,
    dificil: int,
    quantidade_field: int = 0,
) -> dict[str, Any]:
    """Map band counts to kwargs for ``GenerationRequest`` (D-07).

    - 2+ positive bands → ``plano`` + ``quantidade=sum``
    - exactly 1 positive band → legacy ``dificuldade`` + ``quantidade=band count``
    - zero bands → ``ValueError``
    """
    bands: list[tuple[DificuldadeEnum, int]] = [
        (DificuldadeEnum.FACIL, int(facil)),
        (DificuldadeEnum.MEDIO, int(medio)),
        (DificuldadeEnum.DIFICIL, int(dificil)),
    ]
    for _, count in bands:
        if count < 0:
            raise ValueError("contagens de faixa devem ser ≥0")
    active = [(band, count) for band, count in bands if count > 0]
    if not active:
        raise ValueError(
            "plano vazio: informe pelo menos uma faixa >0 "
            "(facil, medio ou dificil)."
        )
    if len(active) >= 2:
        total = sum(count for _, count in bands)
        return {
            "plano": PlanoDificuldade(
                facil=facil,
                medio=medio,
                dificil=dificil,
            ),
            "quantidade": total,
        }
    band, count = active[0]
    _ = quantidade_field  # ignored for uniform payload qty (D-07 / demo D-14)
    return {
        "dificuldade": band,
        "quantidade": count,
    }
