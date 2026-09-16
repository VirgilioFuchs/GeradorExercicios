---
phase: 11-service-layer-extraction
plan: 02
subsystem: api
tags: [service, embed, ConfigError, InvalidRequestError, scoped-env, pytest]

requires:
  - phase: 11-service-layer-extraction
    provides: service.generate_batch pure seam (11-01)
provides:
  - GenerationRequest quantidade Field(ge=1, le=40) + non-empty topico
  - ConfigError / InvalidRequestError / GenerationFailedError with rich attrs
  - Always-on _scoped_env restore for LLM_PROVIDER and LLM_REASONING_EFFORT
  - CLI-owned postmortem; OSError-guarded token flush
affects: [11-03, phase-12-demo]

actuals:
  tokens: 6500
  tasks: 3
  commits: 7

tech-stack:
  added: []
  patterns:
    - error subclasses defined on service boundary; leaf modules lazy-import to avoid cycles
    - _scoped_env always restores provider/reasoning presence-or-absence
    - postmortem write owned by CLI ValueError handler

key-files:
  created:
    - exercise-ai/tests/test_models.py
  modified:
    - exercise-ai/models.py
    - exercise-ai/main.py
    - exercise-ai/service.py
    - exercise-ai/generator.py
    - exercise-ai/generator_gemini.py
    - exercise-ai/failover.py
    - exercise-ai/reliability.py
    - exercise-ai/reasoning.py
    - exercise-ai/token_usage/collector.py
    - exercise-ai/tests/test_service.py

key-decisions:
  - "Error classes live in service.py; raise sites lazy-import to break cycles"
  - "Validation exhaustion → InvalidRequestError(kind=validation_exhausted)"
  - "Postmortem moved to main.run ValueError handler; service path writes none"
  - "Flush OSError swallowed in collector/service/main finally so primary errors survive"

patterns-established:
  - "Host branches on isinstance + .kind without PT message matching"
  - "generate_batch always brackets LLM_PROVIDER / LLM_REASONING_EFFORT"

requirements-completed: [EMBED-02, EMBED-03, EMBED-04]

coverage:
  - id: D1
    description: Domain bound quantidade 1–40 and non-empty topico; argparse _positive_quantidade retained
    requirement: EMBED-03
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_models.py
        status: pass
      - kind: unit
        ref: pytest exercise-ai/tests/test_main.py -q
        status: pass
    human_judgment: false
  - id: D2
    description: Host discriminates ConfigError / InvalidRequestError via isinstance + .kind; validation exhaustion pinned
    requirement: EMBED-02
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_service.py#test_config_error_kind_missing_key
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_service.py#test_validation_exhaustion_raises_invalid_request_error
        status: pass
    human_judgment: false
  - id: D3
    description: Env restore after failover mutation; service no postmortem; flush OSError cannot mask
    requirement: EMBED-04
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_service.py#test_generate_batch_restores_env_after_provider_mutation
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_service.py#test_service_path_exhaustion_writes_no_postmortem
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_service.py#test_flush_oserror_does_not_mask_generation_error
        status: pass
      - kind: unit
        ref: pytest exercise-ai -q (149 passed)
        status: pass
    human_judgment: false

duration: 14min
completed: 2026-09-16
status: complete
---

# Phase 11 Plan 02: Domain bounds, error subclasses, env/FS hygiene Summary

**Host-safe seam: 1–40 domain bounds, discriminable error kinds, always-on env restore, CLI-only postmortem, OSError-guarded flush.**

## Performance

- **Duration:** 14 min
- **Started:** 2026-09-16T14:52:50Z
- **Completed:** 2026-09-16T15:06:29Z
- **Tasks:** 3
- **Files modified:** 11

## Accomplishments

- Enforced `GenerationRequest.quantidade` `Field(ge=1, le=40)` and non-empty stripped `topico`; exported `MAX_QUANTIDADE`; kept argparse `_positive_quantidade`.
- Added `ConfigError` / `InvalidRequestError` / `GenerationFailedError` on the service boundary with `.kind` / `retriable` / `api_error_kind`; validation exhaustion raises `InvalidRequestError(kind=validation_exhausted)`.
- Wrapped `generate_batch` in `_scoped_env` for `LLM_PROVIDER` + `LLM_REASONING_EFFORT`; moved postmortem to CLI; guarded flush against `OSError`.
- Full offline suite: **149 passed**.

## Task Commits

1. **Task 1 RED:** `00bf2d6` — test(11-02): add failing tests for domain bounds
2. **Task 1 GREEN:** `4379686` — domain bounds in models/main (commit message polluted by concurrent 11-01 docs; code is Task 1)
3. **Task 2 RED:** `832881b` — test(11-02): add failing tests for error subclasses
4. **Task 2 GREEN:** `a1de061` — feat(11-02): add ConfigError InvalidRequestError GenerationFailedError
5. **Task 3 RED:** `c0b0c8b` — test(11-02): add failing tests for env restore and FS hygiene
6. **Task 3 GREEN:** `ae2d881` — feat(11-02): scoped env restore, CLI postmortem, guarded flush

## Files Created/Modified

- `exercise-ai/models.py` — MAX_QUANTIDADE, ge/le, topico validator
- `exercise-ai/service.py` — error classes, `_scoped_env`, guarded flush, logger
- `exercise-ai/main.py` — CLI postmortem on ValueError; MAX_QUANTIDADE import; ConfigError keys
- `exercise-ai/reliability.py` — ConfigError retries; InvalidRequestError exhaustion; no library postmortem
- `exercise-ai/generator.py` / `generator_gemini.py` / `failover.py` / `reasoning.py` — raise-site migration
- `exercise-ai/token_usage/collector.py` — OSError guard in flush
- `exercise-ai/tests/test_models.py` / `test_service.py` — new coverage

## Decisions Made

- Lazy-import error classes in leaf modules (keep definitions in `service.py` per plan, avoid circular imports).
- `main` reads `reliability.POSTMORTEM_PATH` dynamically so existing monkeypatched CLI tests keep working.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Circular import via module-level service imports**
- **Found during:** Task 2
- **Issue:** `generator → reasoning → service → failover → reliability → generator` broke collection for `test_reasoning` / `test_generators`.
- **Fix:** Keep classes in `service.py`; lazy-import at raise sites in leaf modules.
- **Files modified:** generator.py, generator_gemini.py, failover.py, reliability.py, reasoning.py
- **Commit:** `a1de061`

**2. [Rule 1 - Bug] CLI postmortem path not seeing monkeypatched POSTMORTEM_PATH**
- **Found during:** Task 3
- **Issue:** `from reliability import POSTMORTEM_PATH` bound the default path; two reliability tests failed.
- **Fix:** `import reliability` and use `reliability.POSTMORTEM_PATH` at write time.
- **Files modified:** main.py
- **Commit:** `ae2d881`

**3. [Note] Task 1 GREEN commit message mixed with concurrent 11-01 docs**
- **Found during:** Task 1 commit
- **Issue:** Parallel agent activity produced `4379686` with message `docs(11-01): record metadata...` while including models/main domain changes.
- **Fix:** Left commit as-is (no amend); documented here. Domain code is correct and covered by tests.

**Total deviations:** 2 auto-fixed + 1 note. **Impact:** none on behavior; import/postmortem path fixes required for green suite.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None beyond plan mitigations T-11-04 / T-11-05 / T-11-06.

## Issues Encountered

None.

## Next

Ready for 11-03 (encoding harden + Gemini timeout + README contract). Do not start until orchestrator dispatches.

## Self-Check: PASSED

- FOUND: exercise-ai/tests/test_models.py
- FOUND: exercise-ai/service.py (`ConfigError|_scoped_env`)
- FOUND: commits 00bf2d6, 4379686, 832881b, a1de061, c0b0c8b, ae2d881
- VERIFY: `pytest exercise-ai -q` → 149 passed
