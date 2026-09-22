---
phase: 14-mixed-prompt-plan-adherence-demo-enablement
plan: 01
subsystem: api
tags: [prompts, verify_plan_echo, RELY, itens_ordenados, hybrid-labels, structured-outputs]

requires:
  - phase: 13-request-schema-plan-contract
    provides: itens_ordenados, pure verify_plan_echo, GenerationRequest plano contract
provides:
  - Numbered hybrid slot list in user prompt from itens_ordenados (uniform + mixed)
  - verify_plan_echo batch.dificuldades summary check (D-07)
  - Post-validate verify_plan_echo inside generate_validated_batch (RELY path)
affects:
  - 14-02-demo-band-ux
  - 15-cli-wizard-ux

actuals:
  tokens: 4200
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns:
    - "always-enumerate slots via itens_ordenados; hybrid PT+enum labels"
    - "plan echo after validate inside RELY; ValueError → existing retry/exhaustion"

key-files:
  created:
    - exercise-ai/tests/test_prompts.py
  modified:
    - exercise-ai/prompts.py
    - exercise-ai/models.py
    - exercise-ai/reliability.py
    - exercise-ai/tests/test_models.py
    - exercise-ai/tests/test_reliability.py

key-decisions:
  - "Hybrid labels in prompts: fácil (facil) / médio (medio) / difícil (dificil)"
  - "Batch summary check lives in verify_plan_echo (same entrypoint), not validator"
  - "verify_plan_echo called only after validate_exercise_batch succeeds"

patterns-established:
  - "PROMPT: no enunciado/resposta/explicacao field-list prose — schema is format authority"
  - "VAL: plan adherence is RELY-owned; validator stays length/emptiness + math_check"

requirements-completed: [PROMPT-01, VAL-01, VAL-02]

coverage:
  - id: D1
    description: User prompt always enumerates numbered hybrid slots from itens_ordenados (mixed and uniform)
    requirement: PROMPT-01
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_prompts.py#test_mixed_prompt_enumerates_hybrid_slots
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_prompts.py#test_uniform_prompt_enumerates_n_slots_same_band
        status: pass
    human_judgment: false
  - id: D2
    description: verify_plan_echo fails on per-slot mismatch and batch dificuldades summary drift
    requirement: VAL-01
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_models.py#test_verify_plan_echo_passes_and_fails
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_models.py#test_verify_plan_echo_batch_dificuldades_summary_mismatch
        status: pass
    human_judgment: false
  - id: D3
    description: Echo mismatch enters bounded RELY retry / validation_exhausted; single loop; not in validator
    requirement: VAL-02
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_reliability.py#test_plan_echo_mismatch_retries_then_succeeds
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_reliability.py#test_plan_echo_mismatch_exhausts_validation
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_reliability.py#test_single_retry_loop_only
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-09-22
status: complete
---

# Phase 14 Plan 01: Mixed prompt + plan adherence Summary

**Numbered hybrid slot prompts from `itens_ordenados`, `verify_plan_echo` (slots + batch summary) after validate inside RELY, offline mismatch→retry proven**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-09-22T09:40:00-03:00
- **Completed:** 2026-09-22T10:05:00-03:00
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- User prompts always enumerate 1-based hybrid difficulty slots (uniform and mixed); field-contract bullets removed
- `verify_plan_echo` extended for order-sensitive `batch.dificuldades` vs `request.dificuldades`
- Plan echo wired after `validate_exercise_batch` in `generate_validated_batch`; mismatches reuse existing RELY `ValueError` path
- Full offline suite green (`pytest exercise-ai -q` → 178 passed)

## Task Commits

1. **Task 1: Tracer — prompt slots + verify_plan_echo after validate + RELY on mismatch** - `4e8d8fd` (feat)
2. **Task 2: Hardening — prompt/VAL coverage + suite green** - `f2649a2` (test)

**Plan metadata:** (this SUMMARY commit)

## Files Created/Modified
- `exercise-ai/prompts.py` — slot list from `itens_ordenados`; hybrid labels; no field-list prose
- `exercise-ai/models.py` — `verify_plan_echo` batch summary check
- `exercise-ai/reliability.py` — call `verify_plan_echo` after validate
- `exercise-ai/tests/test_prompts.py` — mixed + uniform prompt tests
- `exercise-ai/tests/test_models.py` — summary + length echo tests
- `exercise-ai/tests/test_reliability.py` — echo mismatch → RELY / exhaustion; layer separation assert

## Decisions Made
- Followed CONTEXT D-01..D-08 as specified; batch summary check extended in-place on `verify_plan_echo`
- Did not touch `demo/`, CLI/wizard, or `validator.py` plan logic

## Deviations from Plan

None - plan executed exactly as written

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Library path for PROMPT-01 + VAL-01 + VAL-02 complete
- Ready for Plan 14-02 (demo band UX / `plano` POST wiring)
- CLI/wizard compact plan UX remains Phase 15

---
*Phase: 14-mixed-prompt-plan-adherence-demo-enablement*
*Completed: 2026-09-22*
