"""Basic math consistency checks for exercise batches (Phase 6).

Stdlib-only heuristics for arithmetic and ax+b=c. Clear inconsistencies
raise ValueError; uninterpretable items are recorded without failing the batch.
"""

from __future__ import annotations

import re
import sys
from decimal import Decimal, InvalidOperation
from typing import Any

from models import Exercise, ExerciseBatch

_uninterpretable: list[dict[str, Any]] = []
_last_inconsistencies: list[dict[str, Any]] = []

_RAISE_MAX_LEN = 120

_ARITH_EXPR = re.compile(
    r"(?P<a>\d+(?:[.,]\d+)?)\s*"
    r"(?P<op>[+\-−*/÷×xX])\s*"
    r"(?P<b>\d+(?:[.,]\d+)?)"
    r"(?:\s*=\s*\??|\s*\?)?\s*$",
    re.IGNORECASE,
)

# ax + b = c  (integers; optional coeff defaults to 1; a ≠ 0)
_LINEAR_EQ = re.compile(
    r"^\s*(?P<a>-?\d*)\s*[xX]\s*"
    r"(?P<sign>[+\-−])\s*"
    r"(?P<b>\d+)\s*"
    r"=\s*(?P<c>-?\d+)\s*$",
)

_ANSWER_NUM = re.compile(r"^-?\d+(?:[.,]\d+)?$")

_OUT_OF_SCOPE = re.compile(
    r"(√|sqrt|sistema|inequa|≥|≤|≠|geometr|triâng|triang|área|area|ângulo|angulo"
    r"|frac[cç]|"
    r"\d+\s*/\s*\d+\s*[+\-−*/÷×]|"  # chained fraction ops
    r"[a-zA-Z]\s*/\s*[a-zA-Z])",
    re.IGNORECASE,
)


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


def _record_uninterpretable(index: int, ex: Exercise, reason: str = "uninterpretable") -> None:
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
    if op == "+":
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
    return abs(expected - obtained) <= Decimal("0.0001")


def _parse_answer(resposta: str) -> Decimal | None:
    ans_clean = resposta.strip().replace(" ", "")
    if not _ANSWER_NUM.match(ans_clean):
        return None
    return _parse_number(ans_clean)


def _is_out_of_scope(enunciado: str) -> bool:
    en = enunciado.strip()
    if _OUT_OF_SCOPE.search(en):
        return True
    # Radical symbol alone
    if "√" in en or "∛" in en:
        return True
    # Inequality operators
    if any(ch in en for ch in (">", "<", "≥", "≤", "≠")):
        return True
    return False


def _try_linear(enunciado: str, resposta: str) -> tuple[str, Decimal | None, Decimal | None]:
    """Return (status, expected_x, obtained) for ax+b=c."""
    m = _LINEAR_EQ.match(enunciado.strip())
    if m is None:
        return "skip", None, None

    a_raw = m.group("a")
    if a_raw in ("", "+"):
        a = 1
    elif a_raw == "-":
        a = -1
    else:
        a = int(a_raw)
    if a == 0:
        return "uninterpretable", None, None

    sign = m.group("sign")
    b = int(m.group("b"))
    if sign in ("-", "−"):
        b = -b
    c = int(m.group("c"))

    # ax + b = c  →  x = (c - b) / a
    if c - b != (c - b) // a * a:
        # Non-integer exact division still OK if answer matches Decimal
        pass
    expected = Decimal(c - b) / Decimal(a)
    obtained = _parse_answer(resposta)
    if obtained is None:
        return "uninterpretable", None, None
    if _numbers_equal(expected, obtained):
        return "ok", expected, obtained
    return "inconsistent", expected, obtained


def _try_arithmetic(enunciado: str, resposta: str) -> tuple[str, Decimal | None, Decimal | None]:
    """Return (status, expected, obtained) for binary arithmetic."""
    en = enunciado.strip()
    m = _ARITH_EXPR.search(en)
    if m is None:
        return "skip", None, None

    # Require the match to cover essentially the whole enunciado (known template).
    matched = m.group(0).strip()
    en_compact = re.sub(r"\s+", " ", en).strip()
    matched_compact = re.sub(r"\s+", " ", matched).strip()
    if en_compact != matched_compact and not en_compact.startswith(matched_compact):
        # Allow leading filler only if remaining is empty after match at end
        if not en_compact.endswith(matched_compact):
            return "skip", None, None
        # Reject if substantial non-math prefix (e.g. "Simplifique √16 / 2")
        prefix = en_compact[: -len(matched_compact)].strip()
        if prefix and not re.fullmatch(r"[=?]*", prefix):
            if re.search(r"[A-Za-zÀ-ÿ√]", prefix):
                return "skip", None, None

    a = _parse_number(m.group("a"))
    b = _parse_number(m.group("b"))
    op = _normalize_op(m.group("op"))
    if a is None or b is None or op is None:
        return "uninterpretable", None, None

    # Bare "x" as multiply only when not part of equation variable (handled by linear first)
    expected = _compute(a, op, b)
    if expected is None:
        return "uninterpretable", None, None

    obtained = _parse_answer(resposta)
    if obtained is None:
        return "uninterpretable", None, None

    if _numbers_equal(expected, obtained):
        return "ok", expected, obtained
    return "inconsistent", expected, obtained


def _classify(ex: Exercise) -> tuple[str, str, Decimal | None, Decimal | None]:
    """Return (status, tipo, expected, obtained)."""
    en = (ex.enunciado or "").strip()
    ans = (ex.resposta or "").strip()
    if not en or not ans:
        return "uninterpretable", "", None, None

    if _is_out_of_scope(en):
        return "uninterpretable", "", None, None

    status, expected, obtained = _try_linear(en, ans)
    if status != "skip":
        return status, "ax+b=c", expected, obtained

    status, expected, obtained = _try_arithmetic(en, ans)
    if status != "skip":
        return status, "aritmetica", expected, obtained

    return "uninterpretable", "", None, None


def check_math_batch(batch: ExerciseBatch) -> None:
    """Raise ValueError on clear arithmetic / ax+b=c inconsistencies.

    Uninterpretable items are recorded and do not fail the batch (D-02).
    """
    global _last_inconsistencies
    clear_math_buffers()
    inconsistencies: list[dict[str, Any]] = []

    for i, ex in enumerate(batch.exercicios):
        status, tipo, expected, obtained = _classify(ex)
        if status == "ok":
            continue
        if status == "uninterpretable":
            _record_uninterpretable(i, ex)
            continue
        detail = {
            "index": i,
            "enunciado": (ex.enunciado or "")[:80],
            "resposta": (ex.resposta or "")[:80],
            "reason": "inconsistent",
            "tipo": tipo,
            "esperado": str(expected),
            "obtido": str(obtained),
        }
        inconsistencies.append(detail)
        print(
            f"[MATH] índice={i} tipo={tipo} esperado={expected} obtido={obtained}",
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
