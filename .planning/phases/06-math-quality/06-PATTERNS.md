# Phase 6: Math Quality - Pattern Map

**Mapped:** 2026-09-09
**Files analyzed:** 6
**Analogs found:** 6 / 6
**Source:** CONTEXT.md + codebase only (RESEARCH.md skipped)

## File Classification

Implied from CONTEXT decisions (D-01–D-17) and canonical code refs. Module vs in-validator placement is discretion (D-07); recommendation below follows Phase 5’s dedicated-module pattern (`reliability.py`).

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `exercise-ai/math_check.py` (new) | utility | transform | `exercise-ai/validator.py` | role-match |
| `exercise-ai/validator.py` (modify) | service | transform / request-response | itself — extend `validate_exercise_batch` | exact |
| `exercise-ai/reliability.py` (modify) | service / hook | request-response | itself — `generate_validated_batch` | exact |
| `exercise-ai/tests/test_math_check.py` (new) | test | batch (fixtures) | `exercise-ai/tests/test_validator.py` + `conftest.py` | exact |
| `exercise-ai/tests/test_validator.py` (modify) | test | batch | itself — structural → math integration | exact |
| `exercise-ai/tests/test_reliability.py` (modify) | test | request-response | itself — validation `ValueError` regen | exact |

**Not in scope as new files:** `models.py` (reuse `Exercise` / `ExerciseBatch`); second retry loop; CAS lib (prefer stdlib D-09).

---

## Pattern Assignments

### `exercise-ai/math_check.py` (utility, transform) — NEW

**Analog:** `exercise-ai/validator.py` (aggregate errors → stderr detail → short PT `ValueError`)

**Secondary analogs:** `generator.py` dual-channel (`[API:…]` stderr vs plain raise); `models.py` `Exercise` fields.

**Imports pattern** (from `validator.py` 1–8):
```python
from __future__ import annotations

import json
import sys

from models import ExerciseBatch, GenerationRequest
```

Prefer stdlib only (`re`, `ast`, `decimal`/`fractions` only if needed). Do **not** add sympy/CAS unless D-06 vendor path is chosen later.

**Core pattern — collect then raise** (`validator.py` 26–67):
```python
def validate_exercise_batch(batch: ExerciseBatch, request: GenerationRequest) -> ExerciseBatch:
    errors: list[str] = []
    # ... per-item checks append to errors ...
    if errors:
        user_message = "; ".join(errors)
        _log_validation_failure(user_message, batch)
        raise ValueError(user_message)
    return batch
```

Math checker should mirror this: scan all exercises (D-03 / `VALIDATION_REPORT_MODE = "all"`), append clear inconsistencies, skip/uninterpretable → record for postmortem **without** failing (D-02).

**Suggested public surface (planner may rename):**
```python
def check_math_batch(batch: ExerciseBatch) -> None:
    """Raise ValueError on clear arithmetic / ax+b=c inconsistencies.
    Uninterpretable items: record side-effect only; do not fail.
    """

def drain_uninterpretable_records() -> list[dict]:
    """Return + clear cases skipped for postmortem (D-02, D-08)."""
```

**Error / log dual-channel** — copy validator + API mapper split:

From `validator.py` 16–24 (`[VALIDAÇÃO]` detail on stderr, raise without prefix):
```python
def _log_validation_failure(summary: str, batch: object) -> None:
    print(f"[VALIDAÇÃO] {summary}", file=sys.stderr)
    # ... dump batch JSON, never API keys ...
```

From `generator.py` 89–91 (prefix tag + sanitized detail):
```python
print(f"[API:openai] {_openai_error_detail(exc)}", file=sys.stderr)
# raise plain-PT RuntimeError without the [API:…] prefix
```

**Apply for MATH (D-10–D-12):**
- stderr: `[MATH] índice=… tipo=… esperado=… obtido=…` (full detail)
- raise: minimal PT string, **no** `[MATH]` prefix (same contract as `[VALIDAÇÃO]` not in `str(exc)`)
- truncate raise; full content only in stderr / postmortem (LOG-02)

**Scope gates (D-01, D-14–D-16):** only arithmetic `+ − × ÷` (ints/simple decimals) and `ax + b = c` with integer `a,b,c`, `a ≠ 0`. Fractions/radicals/systems/inequalities/geometry → treat as uninterpretable (pass + record), not fail.

**Models to read** (`models.py` 22–31):
```python
class Exercise(BaseModel):
    enunciado: str
    resposta: str
    explicacao: str

class ExerciseBatch(BaseModel):
    exercicios: list[Exercise]
```

---

### `exercise-ai/validator.py` (service, transform) — MODIFY

**Analog:** itself — single validation entrypoint already hooked by reliability.

**Integration pattern:** after structural checks succeed (or after collecting structural errors — prefer **after** structural pass so math only runs on well-formed batches), call math checker. One `ValueError` contract so RELY regenerates (D-07, Phase 5 D-05/D-07).

**Current entry** (lines 26–67): keep signature
`validate_exercise_batch(batch, request) -> ExerciseBatch`.

**Recommended extension sketch:**
```python
from math_check import check_math_batch  # or inline helpers if planner keeps all in validator

def validate_exercise_batch(batch: ExerciseBatch, request: GenerationRequest) -> ExerciseBatch:
    # ... existing structural errors ...
    if errors:
        user_message = "; ".join(errors)
        _log_validation_failure(user_message, batch)
        raise ValueError(user_message)

    check_math_batch(batch)  # raises ValueError on clear math fails
    return batch
```

**Do not** invent a second exception type for math if reliability only catches `ValueError` today (`reliability.py` 89–95). Distinct UX comes from message text / `[MATH]` stderr, not a new exception class.

**Report-all constant** (line 11) — keep `"all"` for math multi-index listing (D-03):
```python
VALIDATION_REPORT_MODE: str = "all"
```

---

### `exercise-ai/reliability.py` (service / hook, request-response) — MODIFY

**Analog:** itself — Phase 6 hook already documented in module docstring.

**Core loop** (lines 54–95) — **do not add a second retry loop**:
```python
def generate_validated_batch(request: GenerationRequest, max_retries: int) -> ExerciseBatch:
    for attempt in range(0, max_retries + 1):
        # generate_exercises(request)  # same prompt every attempt
        try:
            return validate_exercise_batch(batch, request)
        except ValueError as exc:
            last_err = exc
            if attempt < max_retries:
                continue
            raise
```

Math failures must be plain `ValueError` from validation so this path regenerates (CONTEXT + MATH-02).

**D-13 exhaustion prefix** — only when regenerations exhausted, wrap/re-raise user-facing reason:
```python
# On final ValueError (attempt == max_retries), before raise:
# if max_retries > 0: message like "após N regenerações: {minimal_math_or_struct_reason}"
# Details stay on stderr / postmortem, not in a longer raise (D-11)
```

Align with Phase 5 D-13: error reason only at exhaustion (loop already only re-raises on last attempt; main prints `str(val_err)` once).

**Postmortem only on final failure** (D-08):
- On success path: do **not** write postmortem.
- On final `ValueError` (and optionally only when math/uninterpretable records exist): write diagnostic artifact (jsonl/txt — discretion), no secrets.

**File I/O analog** for postmortem write — `main.py` 198–206:
```python
out.write_text(
    json.dumps(validated_batch.model_dump(), indent=2, ensure_ascii=False),
    encoding="utf-8",
)
```

Use `pathlib.Path`, UTF-8, no env keys in payload. Prefer dumping structured records (index, enunciado/resposta snippets, reason: `inconsistent` vs `uninterpretable`) — not full API payloads.

**Duration finally block** (99–104) — leave as-is (RELY-02).

---

### `exercise-ai/tests/test_math_check.py` (test, batch) — NEW

**Analog:** `exercise-ai/tests/test_validator.py` + `tests/conftest.py`

**Imports / fixtures** (`conftest.py` 23–79):
```python
# make_request, make_exercise, make_batch factories — reuse
from models import Exercise, ExerciseBatch
```

**Dual-channel assert pattern** (`test_validator.py` 20–29):
```python
buf = io.StringIO()
with contextlib.redirect_stderr(buf):
    with pytest.raises(ValueError) as exc_info:
        validate_exercise_batch(...)  # or check_math_batch(...)
msg = str(exc_info.value)
assert "[VALIDAÇÃO]" not in msg          # for math: assert "[MATH]" not in msg
assert "[VALIDAÇÃO]" in buf.getvalue()   # for math: assert "[MATH]" in buf.getvalue()
```

**Table-driven / hybrid fixtures (D-05, D-17):** named minimal cases — correct arithmetic, wrong arithmetic, correct `ax+b=c`, wrong solution, uninterpretable (should **not** raise), multi-index list all failures.

Optional: `@pytest.mark.parametrize` as in `test_generators.py` for rows of `(enunciado, resposta, expect_fail)`.

**No live LLM** — never call `generate_exercises`; construct `Exercise` / `ExerciseBatch` only.

---

### `exercise-ai/tests/test_validator.py` (test, batch) — MODIFY

**Analog:** itself.

Add 1–2 integration tests: structurally valid batch with math-inconsistent `resposta` → `validate_exercise_batch` raises; stderr has `[MATH]`; raise message minimal PT and lists indices when multiple (D-03).

Preserve existing structural tests unchanged (regression).

---

### `exercise-ai/tests/test_reliability.py` (test, request-response) — MODIFY

**Analog:** itself — `test_validation_fail_once_then_success` (69–94).

**Regen-on-validation pattern:**
```python
with patch.object(reliability, "generate_exercises", side_effect=fake_gen) as gen:
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        main.run(request_demo, out_path=out_path, max_retries=1)
assert gen.call_count == 2
assert "1ª Regeneração" in err.getvalue()
```

**MATH-02 coverage:** first batch structurally OK but math-wrong → same regen; exhaustion → `SystemExit(1)`, message may include `após N regenerações:` (D-13), no `--out` file (`test_exhaustion_default_one_retry` 117–136).

Do **not** mock a separate math retry API — only `generate_exercises` + real `validate_exercise_batch` (or thin stub that raises math `ValueError`).

---

## Shared Patterns

### Dual-channel errors (stderr detail vs plain raise)
**Source:** `validator.py` 16–24, 62–65; `generator.py` 89–107; tests assert prefix only on stderr  
**Apply to:** math_check, validator integration, reliability exhaustion messaging

```python
# stderr: tagged detail  →  print(f"[MATH] …", file=sys.stderr)
# raise:  plain PT       →  raise ValueError("inconsistência matemática …")
# main.py 209–211 reprints str(val_err) once on failure
```

### Retriable validation via `ValueError` (no second loop)
**Source:** `reliability.py` 1–6, 88–95  
**Apply to:** all math failures (MATH-02)

```python
# Phase 6 hook: future math failures must reuse generate_validated_batch
# (raise a retriable ValueError from validation …) — do not invent a second retry path.
```

### Report all failures in one message
**Source:** `validator.py` 11, 51–60; `test_validator.py` 114–141  
**Apply to:** math multi-exercise listing (D-03)

### Stdlib-first, no agent frameworks
**Source:** AGENTS.md / PROJECT constraints; Phase 5 `reliability.py` as dedicated module  
**Apply to:** math_check implementation (D-09)

### LOG-02 / no secrets
**Source:** `tests/test_logging_security.py`; validator dumps batch JSON only  
**Apply to:** `[MATH]` stderr and postmortem files — never API keys or raw provider payloads

### Test factories without LLM
**Source:** `conftest.py` `make_exercise` / `make_batch`  
**Apply to:** all Phase 6 unit tests (D-17)

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| Postmortem artifact format (jsonl vs txt) | file-I/O | file-I/O | No existing postmortem writer; closest is `main.py` `--out` JSON write — invent minimal format under D-08 |
| Arithmetic / `ax+b=c` parsers | utility | transform | No math parsers in repo; implement with stdlib `re`/`ast` (discretion) |

---

## Locked CONTEXT → pattern checklist

| Decision | Pattern implication |
|----------|---------------------|
| D-01, D-14–D-16 | Fixtures + heuristics only for arithmetic and `ax+b=c` |
| D-02 | Uninterpretable → no raise; accumulate for postmortem |
| D-03 | List all inconsistent indices in one failure |
| D-05 | Hybrid: table fixtures + open heuristics |
| D-07 | Hook through `validate_exercise_batch` → existing RELY loop |
| D-08 | Postmortem write only on final failure |
| D-09 | Prefer stdlib |
| D-10–D-12 | `[MATH]` stderr + minimal truncated PT raise |
| D-13 | Prefix `após N regenerações:` only after exhaustion |

---

## Metadata

**Analog search scope:** `exercise-ai/`, `exercise-ai/tests/`  
**Files scanned:** 9 tracked analogs (`validator`, `reliability`, `models`, `main`, `generator`, `test_validator`, `test_reliability`, `conftest`, `test_logging_security`)  
**Tracked-source gate:** all named analogs verified via `git ls-files`  
**Pattern extraction date:** 2026-09-09
