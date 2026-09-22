---
phase: 14-mixed-prompt-plan-adherence-demo-enablement
plan: 03
subsystem: ai
tags: [dificuldades, verify_plan_echo, Structured Outputs, SEED-008, G-14-4, VAL-01]

requires:
  - phase: 14-mixed-prompt-plan-adherence-demo-enablement
    provides: verify_plan_echo exact compare in RELY (Plan 14-01)
provides:
  - Stronger ExerciseBatch.dificuldades Field description (unique-band summary 1–3)
  - One-line prompt cue for distinct-band dificuldades resumo
  - Offline regression for padded summary fail-closed + RELY exhaustion
affects:
  - DEMO-01 live uniform re-UAT
  - 15-cli-wizard-ux

actuals:
  tokens: 1200
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Teach summary shape via Field description + one prompt cue; keep exact echo compare"
    - "No silent canonicalize of batch.dificuldades before verify_plan_echo"

key-files:
  created: []
  modified:
    - exercise-ai/models.py
    - exercise-ai/prompts.py
    - exercise-ai/tests/test_models.py
    - exercise-ai/tests/test_prompts.py
    - exercise-ai/tests/test_reliability.py

key-decisions:
  - "Keep batch.dificuldades != request.dificuldades exact equality (D-07 fail-closed)"
  - "One short SEED-008 cue under Requisitos; no enunciado/resposta/explicacao field dump"
  - "Canonicalize-before-verify remains out of scope"

patterns-established:
  - "G-14-4 closure: schema+prompt teach unique bands; padded ['medio','medio'] still exhausts RELY"

requirements-completed: [VAL-01, DEMO-01]

coverage:
  - id: D1
    description: ExerciseBatch.dificuldades Field describes unique-band summary (1–3, ordered), not per-exercise
    requirement: VAL-01
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_models.py#test_verify_plan_echo_duplicated_summary_padding_fails
        status: pass
    human_judgment: false
  - id: D2
    description: User prompt includes distinct-band dificuldades resumo cue without field-schema dump
    requirement: VAL-01
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_prompts.py#test_prompt_includes_dificuldades_summary_shape_cue
        status: pass
    human_judgment: false
  - id: D3
    description: Padded summary exhausts RELY as validation_exhausted (fail-closed, no rewrite)
    requirement: DEMO-01
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_reliability.py#test_duplicated_dificuldades_summary_exhausts_validation
        status: pass
    human_judgment: false
  - id: D4
    description: Live DEMO-01 Test 4 uniform path no longer exhausts when model follows cue
    requirement: DEMO-01
    verification: []
    human_judgment: true
    rationale: Live LLM adherence after prompt/schema cue needs re-UAT; offline only locks fail-closed regression

duration: 8min
completed: 2026-09-22
status: complete
---

# Phase 14: Plan 03 Summary

**Schema Field + one prompt cue teach unique-band `dificuldades` summary; padded echo still fail-closes into RELY (G-14-4)**

## Performance

- **Duration:** 8 min
- **Started:** 2026-09-22T14:19:34Z
- **Completed:** 2026-09-22T14:22:25Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Strengthened `ExerciseBatch.dificuldades` Structured Outputs description (unique bands, order fácil→médio→difícil, length 1–3, not per-exercise)
- Added one Requisitos cue: batch `dificuldades` is distinct-band resumo matching plan summary
- Offline locks: padded `['medio','medio']` fails `verify_plan_echo` and exhausts RELY; cue present; SEED-008 hygiene held
- Confirmed no production rewrite of `batch.dificuldades` before verify

## Task Commits

Each task was committed atomically:

1. **Task 1: Schema + prompt unique-band dificuldades summary** - `a35f538` (fix)
2. **Task 2: Optional RELY fixture + suite green** - `38ed51b` (test)

**Plan metadata:** `80b2dac` (docs: complete plan)

## Files Created/Modified
- `exercise-ai/models.py` - Stronger `dificuldades` Field description
- `exercise-ai/prompts.py` - One-line distinct-band resumo cue
- `exercise-ai/tests/test_models.py` - G-14-4 padded-summary fail-closed test
- `exercise-ai/tests/test_prompts.py` - Cue assertion + no field dump
- `exercise-ai/tests/test_reliability.py` - RELY exhaustion on padded summary

## Decisions Made
- Prefer prompt/schema teaching over silent canonicalize before `verify_plan_echo` (plan discretion locked)
- Exact equality compare unchanged for real summary/slot mismatches

## Deviations from Plan

None - plan executed exactly as written

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Offline G-14-4 regression locked; full `pytest exercise-ai` green (182 passed)
- Manual re-UAT (DEMO-01 Test 4 uniform live) still needed to confirm model follows cue

---
*Phase: 14-mixed-prompt-plan-adherence-demo-enablement*
*Completed: 2026-09-22*
