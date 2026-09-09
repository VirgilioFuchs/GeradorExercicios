---
phase: 06-math-quality
verified: 2026-09-09T12:25:24Z
status: passed
score: 11/11 must-haves verified
behavior_unverified: 0
overrides_applied: 0
gaps: []
---

# Phase 6: Math Quality Verification Report

**Phase Goal:** As a CLI user, I want clearly inconsistent arithmetic and ax+b=c answers rejected with a distinct math error that reuses bounded regeneration, so that bad LLM answers are filtered without a second retry path.

**Verified:** 2026-09-09T12:25:24Z  
**Status:** passed  
**Re-verification:** No — initial verification  
**Suite:** `pytest exercise-ai -q` → **73 passed** (2 warnings unrelated to math)

## Goal Achievement

### User Flow Coverage (MVP mode)

| Step | Expected | Evidence | Status |
|------|----------|----------|--------|
| Inconsistent arithmetic / ax+b=c answers | Rejected by validation without live LLM | `check_math_batch` + `test_wrong_arithmetic_*`, `test_wrong_axb_equals_c_raises`, validator integration | ✓ |
| Distinct math error | Dual-channel `[MATH]` stderr + minimal PT `ValueError` (no `[MATH]` in raise) | `math_check.py` L260–274; tests assert dual channel | ✓ |
| Bounded regeneration | Math `ValueError` enters existing `generate_validated_batch` only | `validator` → `ValueError`; `test_math_fail_once_then_success`; single `for attempt` loop | ✓ |
| Exhaustion | Fail predictably with `após N regenerações:` + postmortem only on final fail | `reliability.py` L115–121; `test_math_exhaustion_prefix_and_postmortem` | ✓ |

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| R1 | Validador rejeita respostas matematicamente inconsistentes nos casos básicos definidos na discuss/plan (testável sem LLM real) | **VERIFIED** | Arithmetic + ax+b=c fixtures in `test_math_check.py`; integration via `validate_exercise_batch` in `test_validator.py` |
| R2 | Falha matemática produz mensagem clara identificando o problema (distinta de falha estrutural genérica) | **VERIFIED** | Raise text `inconsistência matemática nos exercícios: …`; stderr `[MATH] índice=… tipo=… esperado=… obtido=…`; distinct from `[VALIDAÇÃO]` / empty-field wording |
| R3 | Quando aplicável, falha matemática dispara regeneração limitada (RELY-01); esgotadas as tentativas, fluxo falha de forma previsível | **VERIFIED** | `test_math_fail_once_then_success` (call_count==2); `test_math_exhaustion_prefix_and_postmortem` (`após 1 regenerações:`, SystemExit 1, no `--out`) |
| P1 | Clear arithmetic inconsistencies (+ − × ÷ ints/simple decimals) rejected without live LLM | **VERIFIED** | `test_wrong_arithmetic_raises_math_dual_channel`; `test_correct_arithmetic_passes`; `_try_arithmetic` / `_compute` in `math_check.py` |
| P2 | Clear ax+b=c inconsistencies (integer a,b,c a≠0) rejected the same way | **VERIFIED** | `test_wrong_axb_equals_c_raises`; `test_correct_axb_equals_c_passes`; `_try_linear` |
| P3 | Uninterpretable enunciado/resposta do not fail the batch; recorded for postmortem | **VERIFIED** | `test_uninterpretable_does_not_raise_but_records`; `_record_uninterpretable` + `drain_uninterpretable_records` |
| P4 | Multiple math inconsistencies → one ValueError lists all; batch fails | **VERIFIED** | `test_multi_index_lists_all_inconsistencies`; `test_structurally_ok_math_multi_via_validator` |
| P5 | Dual channel: stderr `[MATH]` with index+detail; raise minimal truncated PT without `[MATH]` | **VERIFIED** | Dual-channel tests in `test_math_check.py` / `test_validator.py`; `_RAISE_MAX_LEN = 120` |
| P6 | Math ValueError enters existing `generate_validated_batch` only — regenerates up to N then stops | **VERIFIED** | Single `for attempt in range` in `reliability.py`; `test_single_retry_loop_only`; no math retry API |
| P7 | After regenerations exhausted, user-facing reason prefixed with `após N regenerações:` + minimal reason | **VERIFIED** | `reliability.py` L118–121; `test_math_exhaustion_prefix_and_postmortem`; `test_max_retries_zero_no_apos_prefix` |
| P8 | Postmortem diagnostic file only on final batch failure (never on success), no API keys/payloads | **VERIFIED** | `_write_postmortem` on final ValueError only; `test_math_success_writes_no_postmortem`; exhaustion test asserts no `LLM_API_KEY` / `sk-` |

**Score:** 11/11 truths verified (0 behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `exercise-ai/math_check.py` | `check_math_batch`; hybrid arith / ax+b=c; uninterpretable records; `[MATH]` dual channel | ✓ VERIFIED | Substantive (~275 LOC); stdlib `re`/`decimal` only; wired from validator |
| `exercise-ai/validator.py` | Calls math check after structural pass | ✓ VERIFIED | L68 `check_math_batch(batch)` only when `errors` empty |
| `exercise-ai/reliability.py` | Exhaustion prefix + final postmortem; one retry loop | ✓ VERIFIED | Contains `após`; `_write_postmortem`; single attempt loop |
| `exercise-ai/tests/test_math_check.py` | Named fixtures correct/wrong arith, ax+b=c, uninterpretable, multi-index | ✓ VERIFIED | 7 tests covering required cases |
| `exercise-ai/tests/test_validator.py` | Structural OK + math-wrong via `validate_exercise_batch` | ✓ VERIFIED | Contains `MATH`; integration tests present |
| `exercise-ai/tests/test_reliability.py` | Math regen; exhaustion prefix + postmortem | ✓ VERIFIED | Contains `após`; MATH-02 path covered |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `validate_exercise_batch` | `math_check.check_math_batch` | after structural errors empty; same ValueError | ✓ WIRED | `validator.py` L63–68 |
| math `ValueError` | `reliability.generate_validated_batch` | existing `except ValueError` regen — no second loop | ✓ WIRED | `reliability.py` L107–122; single loop asserted by test |
| final exhausted `ValueError` | postmortem + `após N regenerações:` | D-08 + D-13 on last attempt only | ✓ WIRED | `_write_postmortem` then prefixed raise when `max_retries > 0` |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `check_math_batch` | `enunciado` / `resposta` | `ExerciseBatch.exercicios` from caller | Compared via Decimal expected vs obtained | ✓ FLOWING |
| `[MATH]` stderr | `expected` / `obtained` | Computed from parsed templates | Printed on clear inconsistency | ✓ FLOWING |
| postmortem jsonl | inconsistency + uninterpretable records | `drain_*_records()` buffers filled during check | Written only on final fail | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full suite (math + validator + reliability + rest) | `pytest exercise-ai -q` | 73 passed | ✓ PASS |
| Arithmetic reject dual-channel | exercised by suite (`test_wrong_arithmetic_raises_math_dual_channel`) | pass | ✓ PASS |
| Math → RELY regen | exercised by suite (`test_math_fail_once_then_success`) | pass | ✓ PASS |
| Exhaustion + postmortem | exercised by suite (`test_math_exhaustion_prefix_and_postmortem`) | pass | ✓ PASS |

### Probe Execution

| Probe | Command | Result | Status |
|-------|---------|--------|--------|
| — | — | No phase-declared probes | SKIP |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| MATH-01 | 06-01 | Reject mathematically inconsistent basic cases | ✓ SATISFIED | Arithmetic + ax+b=c rejection; uninterpretable pass+record |
| MATH-02 | 06-01 | Clear math message; may trigger RELY regen | ✓ SATISFIED | `[MATH]` + minimal PT raise; regen + exhaustion UX |

No orphaned Phase 6 requirements.

### Prohibitions

| Prohibition | Status | Evidence |
|-------------|--------|----------|
| No second retry loop for math outside `generate_validated_batch` | ✓ HELD | One `for attempt in range` in `reliability.py`; `test_single_retry_loop_only`; `math_check` has no retry API |
| No full CAS / sympy / vendor math library (stdlib only) | ✓ HELD | `math_check.py` uses `re`/`decimal` only; `requirements.txt` has no sympy/CAS |
| No fail-on-uninterpretable batch failure | ✓ HELD | Uninterpretable path records and continues; `test_uninterpretable_does_not_raise_but_records` |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | No TBD/FIXME/XXX/TODO/stub markers in phase files | — | None |

### Human Verification Required

None — all must-haves are covered by automated fixture/mocked tests without live LLM.

### Gaps Summary

None. Phase goal achieved in codebase: basic math inconsistencies rejected, distinct math messaging, RELY-bounded regeneration with exhaustion prefix and final-only postmortem, prohibitions held.

---

_Verified: 2026-09-09T12:25:24Z_  
_Verifier: Claude (gsd-verifier)_

## VERIFICATION PASSED
