"""Paths for generated exercise artifacts under ``exercicios-gerados/``."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
EXERCICIOS_GERADOS = PACKAGE_DIR / "exercicios-gerados"
SUCCESS_DIR = EXERCICIOS_GERADOS / "success"
FAIL_ERROS_DIR = EXERCICIOS_GERADOS / "fail" / "erros"
FAIL_POSTMORTEM_DIR = EXERCICIOS_GERADOS / "fail" / "postmortem"
DEFAULT_POSTMORTEM_PATH = FAIL_POSTMORTEM_DIR / "math_postmortem.jsonl"


def resolve_success_out_path(out_path: Path | str) -> Path:
    """Map relative ``--out`` into ``exercicios-gerados/success/``; keep absolute as-is."""
    path = Path(out_path)
    if path.is_absolute():
        return path
    # Relative: always under success/ (basename only — avoid escaping via ..)
    name = path.name
    if not name:
        name = "exercicios.json"
    return SUCCESS_DIR / name


def write_fail_error_log(message: str, *, base_dir: Path | None = None) -> Path:
    """Write a plain-text error log under fail/erros/; return the path written."""
    erros = (base_dir or FAIL_ERROS_DIR)
    erros.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = erros / f"erro-{stamp}.txt"
    dest.write_text(message.strip() + "\n", encoding="utf-8")
    return dest
