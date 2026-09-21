---
phase: 13-request-schema-plan-contract
plan: 01
subsystem: api
tags: [pydantic, GenerationRequest, ExerciseSpec, plano, itens, dificuldades, verify_plan_echo]

requires:
  - phase: 12-milestone-setup
    provides: v2.1 roadmap and BATCH/CAP requirements
provides:
  - ExerciseSpec + PlanoDificuldade request contract
  - GenerationRequest normalize (uniform / plano / itens / equal-split)
  - Required Exercise.dificuldade + ExerciseBatch.dificuldades echoes
  - Pure verify_plan_echo (D-11) for Phase 14 wiring
affects:
  - 14-prompt-validator-adherence
  - 15-cli-wizard-ux

actuals:
  tokens: 9500
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns:
    - "schema-boundary normalize via @model_validator(mode=after)"
    - "pure echo check separate from RELY loop"

key-files:
  created: []
  modified:
    - exercise-ai/models.py
    - exercise-ai/tests/test_models.py
    - exercise-ai/tests/conftest.py
    - exercise-ai/tests/test_*.py (echo field construction)

key-decisions:
  - "ExerciseSpec + PlanoDificuldade; itens_ordenados property after normalize"
  - "Uniform keeps itens=None; ordered slots via _ordered_specs / itens_ordenados"
  - "verify_plan_echo pure ValueError; not wired into validator/reliability"

patterns-established:
  - "BATCH-02 qty↔plan length fails at Pydantic before LLM"
  - "D-07/D-08 equal-split remainder to last band in fácil→médio→difícil"

requirements-completed: [BATCH-01, BATCH-02, BATCH-03, BATCH-04, CAP-01]

coverage:
  - id: D1
    description: Uniform legacy request normalizes dificuldades length 1
    requirement: BATCH-04
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_models.py#test_uniform_legacy_normalizes_dificuldades
        status: pass
    human_judgment: false
  - id: D2
    description: Mixed plano XOR itens; qty must match plan length
    requirement: BATCH-01
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_models.py#test_mixed_plano_expands_facil_medio
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_models.py#test_plano_and_itens_xor_rejected
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_models.py#test_quantidade_mismatch_plano_rejected
        status: pass
    human_judgment: false
  - id: D3
    description: Exercise/ExerciseBatch require difficulty echoes; verify_plan_echo fail-closed
    requirement: BATCH-03
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_models.py#test_exercise_and_batch_require_echo_fields
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_models.py#test_verify_plan_echo_passes_and_fails
        status: pass
    human_judgment: false
  - id: D4
    description: Equal-split dificuldades heuristic with remainder on last band
    requirement: BATCH-01
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_models.py#test_equal_split_dificuldades_remainder_to_last
        status: pass
    human_judgment: false
  - id: D5
    description: MAX_QUANTIDADE remains 40; suite green on uniform path
    requirement: CAP-01
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_models.py#test_max_quantidade_cap_unchanged
        status: pass
      - kind: unit
        ref: "pytest exercise-ai -q (172 passed)"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-09-21
status: complete
---

# Phase 13: Request schema & plan contract — Plan 01 Summary

**Typed uniform/mixed batch contract landed in `models.py`: `plano`/`itens` XOR, count invariants, required difficulty echoes, and pure `verify_plan_echo` — prompts/RELY/CLI untouched.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-09-21
- **Completed:** 2026-09-21
- **Tasks:** 2
- **Files modified:** 16 (models + test suite echo updates)

## Accomplishments

- Extended `GenerationRequest` with `ExerciseSpec`, `PlanoDificuldade`, optional `plano`/`itens`/`dificuldades`, and post-validate ordered specs via `itens_ordenados`
- Required `Exercise.dificuldade` and `ExerciseBatch.dificuldades`; pure `verify_plan_echo` raises on slot mismatch without mutation
- Offline coverage for uniform compat, mixed plano/itens, XOR, qty drift, equal-split (D-07/D-08), CAP-01; full suite 172 passed

## Task Commits

1. **Task 1: Tracer uniform + plano + echo** — `e6e61af` (feat)
2. **Task 2: XOR, equal-split, CAP-01, suite green** — `6018adc` (feat)
3. **Plan metadata** — (this docs commit)

## Files Created/Modified

- `exercise-ai/models.py` — schema + normalize + `verify_plan_echo`
- `exercise-ai/tests/test_models.py` — tracer + invariant tests (17)
- `exercise-ai/tests/conftest.py` — factories supply echo fields
- `exercise-ai/tests/test_*.py` — Exercise/ExerciseBatch constructions + Gemini mock JSON

## Decisions Made

- Materialize mixed plans onto `itens`; keep uniform `itens=None` and expose slots via `itens_ordenados`
- Equal-split remainder assigned to last band in fácil→médio→difícil among listed bands
- Do not call `verify_plan_echo` from validator/reliability (Phase 14)

## Deviations from Plan

### Auto-fixed Issues

**1. Suite breakage from required echo fields**
- **Found during:** Task 2
- **Issue:** Many tests constructed `Exercise`/`ExerciseBatch` without new required fields; Gemini mock JSON omitted echoes
- **Fix:** AST-updated constructions; updated `test_generators` fallback mock payload
- **Files modified:** `exercise-ai/tests/test_*.py`
- **Verification:** `pytest exercise-ai -q` → 172 passed
- **Committed in:** `6018adc`

**Total deviations:** 1 auto-fixed  
**Impact on plan:** Necessary for suite green; no scope creep into prompts/CLI/RELY

## Issues Encountered

- Initial regex-based test rewrite corrupted nested constructors; restored from git and re-applied via AST `unparse`

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 14 can consume `itens_ordenados` + wire `verify_plan_echo` into RELY
- Phase 15 can author `plano`/`itens` against the same models
- Residual risk: live LLM responses must now emit echo fields (schema enforces); prompts not yet instructing mixed bands

---
*Phase: 13-request-schema-plan-contract*
*Completed: 2026-09-21*
