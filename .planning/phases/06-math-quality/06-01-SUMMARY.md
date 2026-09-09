---
phase: 06-math-quality
plan: 01
subsystem: validation
tags: [math-check, arithmetic, linear-equation, ValueError, postmortem, reliability, pytest]

requires:
  - phase: 05-reliability-error-edges
    provides: generate_validated_batch ValueError regen loop
provides:
  - "stdlib math_check for arithmetic and ax+b=c clear inconsistencies"
  - "validator hook after structural pass (single ValueError contract)"
  - "exhaustion prefix após N regenerações + final-only postmortem"
affects: [verify-work, UAT math quality]

actuals:
  tokens: 9878
  tasks: 3
  commits: 6

tech-stack:
  added: []
  patterns:
    - "Dual-channel [MATH] stderr + minimal PT ValueError (mirrors [VALIDAÇÃO])"
    - "Uninterpretable pass+record; clear inconsistency fail-all indices"
    - "Postmortem jsonl only on final generate_validated_batch failure"

key-files:
  created:
    - exercise-ai/math_check.py
    - exercise-ai/tests/test_math_check.py
  modified:
    - exercise-ai/validator.py
    - exercise-ai/reliability.py
    - exercise-ai/tests/test_validator.py
    - exercise-ai/tests/test_reliability.py

key-decisions:
  - "Stdlib-only heuristics; no sympy/CAS (D-09)"
  - "Math failures reuse existing generate_validated_batch only (D-07)"
  - "POSTMORTEM_PATH injectable module attr for tests (D-08)"

patterns-established:
  - "check_math_batch after structural pass in validate_exercise_batch"
  - "drain_uninterpretable_records / drain_inconsistency_records for postmortem"
  - "após N regenerações: prefix only when max_retries > 0 on final ValueError"

requirements-completed: [MATH-01, MATH-02]

coverage:
  - id: D1
    description: "Clear arithmetic inconsistencies rejected without live LLM"
    requirement: MATH-01
    verification:
      - kind: unit
        ref: "exercise-ai/tests/test_math_check.py#test_wrong_arithmetic_raises_math_dual_channel"
        status: pass
    human_judgment: false
  - id: D2
    description: "Clear ax+b=c inconsistencies rejected; correct solutions pass"
    requirement: MATH-01
    verification:
      - kind: unit
        ref: "exercise-ai/tests/test_math_check.py#test_wrong_axb_equals_c_raises"
        status: pass
    human_judgment: false
  - id: D3
    description: "Uninterpretable items do not fail batch; records drainable"
    requirement: MATH-01
    verification:
      - kind: unit
        ref: "exercise-ai/tests/test_math_check.py#test_uninterpretable_does_not_raise_but_records"
        status: pass
    human_judgment: false
  - id: D4
    description: "Multi-index math failures listed in one ValueError"
    requirement: MATH-01
    verification:
      - kind: unit
        ref: "exercise-ai/tests/test_math_check.py#test_multi_index_lists_all_inconsistencies"
        status: pass
    human_judgment: false
  - id: D5
    description: "Math ValueError regenerates via generate_validated_batch; exhaustion prefix + postmortem"
    requirement: MATH-02
    verification:
      - kind: unit
        ref: "exercise-ai/tests/test_reliability.py#test_math_fail_once_then_success"
        status: pass
      - kind: unit
        ref: "exercise-ai/tests/test_reliability.py#test_math_exhaustion_prefix_and_postmortem"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-09-09
status: complete
---

# Phase 6 Plan 01: Math Quality Vertical Slice Summary

**Stdlib arithmetic + ax+b=c math checks wired through validator into the existing RELY regen loop, with `[MATH]` dual-channel UX, exhaustion prefix, and final-only postmortem.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-09-09T12:12:45Z
- **Completed:** 2026-09-09T12:37:00Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments
- `check_math_batch` rejects clear arithmetic and `ax+b=c` inconsistencies; uninterpretable cases pass and record for postmortem
- Validator calls math check after structural pass; math `ValueError` reuses `generate_validated_batch` (no second loop)
- Exhaustion surfaces `após N regenerações:` + minimal reason; postmortem jsonl only on final failure (no secrets)

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — arithmetic through validator → RELY** - `66cffa3` (feat)
2. **Task 2 RED: ax+b=c / uninterpretable fixtures** - `8162b36` (test)
3. **Task 2 GREEN: expand math_check surface** - `1293818` (feat)
4. **Task 3 RED: exhaustion + postmortem tests** - `1414c2e` (test)
5. **Task 3 GREEN: reliability prefix + postmortem** - `22145b2` (feat)

**Plan metadata:** (docs commit follows)

## Self-Check

Verifying created files and commits before state finalization:

- FOUND: `exercise-ai/math_check.py`
- FOUND: `exercise-ai/tests/test_math_check.py`
- FOUND: `66cffa3` Task 1
- FOUND: `8162b36` Task 2 RED
- FOUND: `1293818` Task 2 GREEN
- FOUND: `1414c2e` Task 3 RED
- FOUND: `22145b2` Task 3 GREEN
- FOUND: `pytest exercise-ai -q` → 73 passed

## Self-Check: PASSED

## Files Created/Modified
- `exercise-ai/math_check.py` - Hybrid arithmetic / ax+b=c checks; uninterpretable buffer; `[MATH]` stderr
- `exercise-ai/validator.py` - Calls `check_math_batch` after structural pass
- `exercise-ai/reliability.py` - Exhaustion prefix + final postmortem write
- `exercise-ai/tests/test_math_check.py` - Named minimal hybrid fixtures
- `exercise-ai/tests/test_validator.py` - Math integration via `validate_exercise_batch`
- `exercise-ai/tests/test_reliability.py` - MATH-02 regen, exhaustion, postmortem assertions

## Decisions Made
- Stdlib only (D-09); D-06 vendor path not taken
- Postmortem path via injectable `reliability.POSTMORTEM_PATH` for tests
- Out-of-scope patterns (radicals, inequalities, etc.) treated as uninterpretable before arithmetic substring match

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- MATH-01 and MATH-02 delivered; ready for phase verification / UAT
- Deferred: fractions/radicals/CAS, property gens, prompt repair, fine-tune from postmortem

---
*Phase: 06-math-quality*
*Completed: 2026-09-09*
