"""Basic math consistency checks for exercise batches (Phase 6).

Stdlib-only heuristics for arithmetic and (later) ax+b=c. Clear inconsistencies
raise ValueError; uninterpretable items are recorded without failing the batch.
"""

from __future__ import annotations

import re
import sys
from decimal import Decimal, InvalidOperation
from typing import Any

from models import Exercise, ExerciseBatch

# Module-level buffer for uninterpretable cases (drain for postmortem).
_uninterpretable: list[dict[str, Any]] = []

# Optional: clear inconsistencies collected on last check (for postmortem).
_last_inconsistencies: list[dict[str, Any]] = []

_RAISE_MAX_LEN = 120

# Digits, optional decimal, operators, whitespace, ?, =, x/× for multiply wording.
_ARITH_ALLOWED = re.compile(
    r"^[\d\s+\-−*/÷×xX.,=?]+$"
)

# Capture: number OP number, optional =? / ?
_ARITH_EXPR = re.compile(
    r"(?P<a>\d+(?:[.,]\d+)?)\s*"
    r"(?P<op>[+\-−*/÷×xX])\s*"
    r"(?P<b>\d+(?:[.,]\d+)?)"
    r"(?:\s*=\s*\??|\s*\?)?\s*$"
)

_ANSWER_NUM = re.compile(r"^-?\d+(?:[.,]\d+)?$")


def drain_uninterpretable_records() -> list[dict[str, Any]]:
    """Return and clear accumulated uninterpretable records (D-02, D-08)."""
    records = list(_uninterpretable)
    _uninterpretable.clear()
    return records


def drain_inconsistency_records() -> list[dict[str, Any]]:
    """Return and clear last clear-inconsistency records (for postmortem)."""
    records = list(_last_inconsistencies)
    _last_inconsistencies.clear()
    return records


def clear_math_buffers() -> None:
    """Clear uninterpretable + inconsistency buffers (success path)."""
    _uninterpretable.clear()
    _last_inconsistencies.clear()


def _record_uninterpretable(index: int, ex: Exercise, reason: str) -> None:
    _uninterpretable.append(
        {
            "index": index,
            "enunciado": (ex.enunciado or "")[:80],
            "resposta": (ex.resposta or "")[:80],
            "reason": reason,
        }
    )


def _parse_number(raw: str) -> Decimal | None:
    text = raw.strip().replace(",", ".")
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return None


def _normalize_op(op: str) -> str | None:
    if op in ("+",):
        return "+"
    if op in ("-", "−"):
        return "-"
    if op in ("*", "×", "x", "X"):
        return "*"
    if op in ("/", "÷"):
        return "/"
    return None


def _compute(a: Decimal, op: str, b: Decimal) -> Decimal | None:
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        if b == 0:
            return None
        return a / b
    return None


def _numbers_equal(expected: Decimal, obtained: Decimal) -> bool:
    """Compare with tolerance for simple decimal division."""
    return abs(expected - obtained) <= Decimal("0.0001")


def _try_arithmetic(enunciado: str, resposta: str) -> tuple[str, Decimal | None, Decimal | None]:
    """Return (status, expected, obtained).

    status: 'ok' | 'inconsistent' | 'uninterpretable'
    """
    en = enunciado.strip()
    ans_raw = resposta.strip()
    if not en or not ans_raw:
        return "uninterpretable", None, None

    # Out-of-scope signals → uninterpretable (Task 2 expands; keep conservative here).
    lower = en.lower()
    if any(
        token in lower
        for token in ("√", "sqrt", "sistema", "≥", "≤", ">", "<", "frac", "/")
    ) and "/" not in en.replace(" ", ""):
        # "/" alone in fraction context handled below; skip for now on radicals etc.
        pass

    # Reject fraction-like "a/b" as standalone answer patterns later; for enunciado
    # with only one slash as division operator we still allow via _ARITH_EXPR.

    if not _ARITH_ALLOWED.match(en.replace("?", "").replace("=", "")):
        # Allow if we can still match a simple binary expression somewhere.
        m = _ARITH_EXPR.search(en)
        if m is None:
            return "uninterpretable", None, None
    else:
        m = _ARITH_EXPR.search(en)
        if m is None:
            return "uninterpretable", None, None

    a = _parse_number(m.group("a"))
    b = _parse_number(m.group("b"))
    op = _normalize_op(m.group("op"))
    if a is None or b is None or op is None:
        return "uninterpretable", None, None

    expected = _compute(a, op, b)
    if expected is None:
        return "uninterpretable", None, None

    # Answer must be a plain number for clear check.
    ans_clean = ans_raw.replace(" ", "")
    if not _ANSWER_NUM.match(ans_clean):
        return "uninterpretable", None, None
    obtained = _parse_number(ans_clean)
    if obtained is None:
        return "uninterpretable", None, None

    if _numbers_equal(expected, obtained):
        return "ok", expected, obtained
    return "inconsistent", expected, obtained


def check_math_batch(batch: ExerciseBatch) -> None:
    """Raise ValueError on clear arithmetic inconsistencies (D-01, D-14).

    Uninterpretable items are recorded and do not fail the batch (D-02).
    """
    global _last_inconsistencies
    clear_math_buffers()  # start fresh per batch check
    # clear_math_buffers cleared uninterpretable too — re-init tracking
    inconsistencies: list[dict[str, Any]] = []

    for i, ex in enumerate(batch.exercicios):
        status, expected, obtained = _try_arithmetic(ex.enunciado, ex.resposta)
        if status == "ok":
            continue
        if status == "uninterpretable":
            _record_uninterpretable(i, ex, "uninterpretable")
            continue
        # inconsistent
        detail = {
            "index": i,
            "enunciado": (ex.enunciado or "")[:80],
            "resposta": (ex.resposta or "")[:80],
            "reason": "inconsistent",
            "tipo": "aritmetica",
            "esperado": str(expected),
            "obtido": str(obtained),
        }
        inconsistencies.append(detail)
        print(
            f"[MATH] índice={i} tipo=aritmetica esperado={expected} obtido={obtained}",
            file=sys.stderr,
        )

    _last_inconsistencies = list(inconsistencies)

    if not inconsistencies:
        return

    indices = ", ".join(str(d["index"]) for d in inconsistencies)
    user_message = f"inconsistência matemática nos exercícios: {indices}"
    if len(user_message) > _RAISE_MAX_LEN:
        user_message = user_message[: _RAISE_MAX_LEN - 1] + "…"
    raise ValueError(user_message)
