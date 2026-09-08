---
phase: 02-validation-error-handling
reviewed: 2026-09-04T11:56:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - exercise-ai/validator.py
  - exercise-ai/main.py
  - exercise-ai/generator.py
  - exercise-ai/generator_gemini.py
findings:
  critical: 0
  warning: 4
  info: 2
  total: 6
status: issues
---

# Phase 2: Code Review Report

**Reviewed:** 2026-09-04T11:56:00Z
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues

## Summary

Advisory review of Phase 2 validation and API error-handling against `02-CONTEXT` D-01–D-15 and project security (API keys never in logs). Core contracts look solid: semantic validation on `ExerciseBatch`, exact quantity, strip-empty fields with path messages, `VALIDATION_REPORT_MODE`, two-layer stderr, stage labels, fail-fast exit 1, and stdout JSON-only on success. Issues are concentrated in API error logging/sanitization and a few unmapped edge failure paths.

## Warnings

### WR-01: `[API:*]` detail logs may embed API key material

**File:** `exercise-ai/generator.py:57`
**Also:** `exercise-ai/generator_gemini.py:72`
**Issue:** Both mappers log `f"{type(exc).__name__}: {exc}"` to stderr before mapping. OpenAI `AuthenticationError` (and some provider bodies) commonly include the submitted key or a redacted fragment (e.g. `Incorrect API key provided: sk-...`). That violates project security (“API keys never in logs”) even when the user-facing `RuntimeError` for auth is sanitized (D-09/D-10).
**Fix:** Log exception type + status/code only; never interpolate raw `str(exc)` unless sanitized. Example:

```python
code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
print(f"[API:openai] {type(exc).__name__} status={code}", file=sys.stderr)
```

### WR-02: OpenAI generic fallback puts technical `{exc}` in user message (D-09)

**File:** `exercise-ai/generator.py:71`
**Issue:** Mapped auth/timeout/rate/connection paths return plain PT messages, but the fallback is `RuntimeError(f"Erro na chamada à API da OpenAI: {exc}")`. D-09 requires a unified PT user message with technical detail only in the `[API:openai]` log layer. Gemini already uses a fixed `_MSG_GENERIC` without embedding `exc`.
**Fix:**

```python
return RuntimeError("Erro na chamada à API da OpenAI.")
```

### WR-03: Empty `completion.choices` bypasses ERR-03 / D-12 mapping

**File:** `exercise-ai/generator.py:92`
**Issue:** `message = completion.choices[0].message` raises `IndexError` when `choices` is empty. That is not an `OpenAIError`, so it skips `map_openai_error` and lands in `main`’s bare `except Exception`, yielding a cryptic English traceback-style message instead of a clear PT `RuntimeError` (D-12 / ERR-03).
**Fix:** Guard before indexing:

```python
if not completion.choices:
    print("[API:openai] empty choices", file=sys.stderr)
    raise RuntimeError(
        "Não foi possível obter a estrutura de exercícios da resposta do modelo."
    )
message = completion.choices[0].message
```

### WR-04: Gemini non-`APIError` transport failures skip typed mapping (D-11)

**File:** `exercise-ai/generator_gemini.py:97-107`
**Issue:** Only `genai_errors.APIError` is mapped. Client/transport timeouts or connection failures that surface as other exception types (e.g. underlying HTTP timeout) propagate unmapped to `main`’s generic handler, so users may not get the intended timeout/connection PT messages from D-11.
**Fix:** Broaden the `except` to map known transport failures (or catch `Exception` after `APIError`, classify via message/heuristics, and always raise `map_gemini_error` / equivalent PT `RuntimeError`), keeping technical detail in `[API:gemini]` only.

## Info

### IN-01: Invalid `VALIDATION_REPORT_MODE` silently behaves as `"all"`

**File:** `exercise-ai/validator.py:11,59`
**Issue:** Only `"first_exercise"` changes control flow; any other string (typo) falls through to collect-all behavior with no warning.
**Fix:** Validate at module load or start of `validate_exercise_batch` and raise / log if mode ∉ `{"all", "first_exercise"}`.

### IN-02: Post-Pydantic `isinstance` / `hasattr` branches are largely unreachable

**File:** `exercise-ai/validator.py:30-40`
**Issue:** Callers pass `ExerciseBatch` from Structured Outputs / `model_validate`. The non-instance and missing-`exercicios` paths are defensive but unused in the current pipeline (D-01 assumes already-parsed batch). Harmless; slightly noisy for readers.
**Fix:** Keep for belt-and-suspenders, or narrow the public type and drop dead branches once Phase 3 tests lock the contract.

## D-01–D-15 compliance snapshot

| Decision | Assessment |
|----------|------------|
| D-01 Semantic rules on parsed `ExerciseBatch` | Met |
| D-02 Exact `len(exercicios) == quantidade` | Met |
| D-03 `.strip()` empty fields | Met |
| D-04 Raw JSON on validation failure | Met |
| D-05 Plain PT user line vs prefixed detail | Met (CLI + validators) |
| D-06 Field paths `exercicios[i].field` | Met |
| D-07 Expected vs received quantity | Met |
| D-08 `VALIDATION_REPORT_MODE` constant | Met (see IN-01) |
| D-09 Unified PT user / provider detail logs | Mostly; WR-02 gaps OpenAI generic |
| D-10 Dual-key missing message | Met |
| D-11 Distinct timeout/rate/conn/auth | Met for mapped types; WR-04 Gemini edge |
| D-12 Empty/unparseable → clear `RuntimeError` | Met for handled paths; WR-03 empty choices |
| D-13 Fail-fast stderr + exit 1 | Met |
| D-14 Success stdout JSON only | Met |
| D-15 Stage labels on stderr | Met (`Gerando…` / `Validando…`) |

---

_Reviewed: 2026-09-04T11:56:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
_Advisory only — production code not modified_
