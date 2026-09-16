# Plan 11-01 Summary: Pure service seam extraction

**Phase:** 11-service-layer-extraction  
**Plan:** 01  
**Completed:** 2026-09-16

---
phase: 11-service-layer-extraction
plan: 01
subsystem: api
tags: [service, embed, generate_batch, pytest]

requires:
  - phase: 10-interactive-cli-wizard
    provides: wizard enters via main.run; CLI argparse path
provides:
  - service.generate_batch(request) -> ExerciseBatch embed seam
  - main.run as CLI adapter (print / --out / fail-log / sys.exit)
  - test_service.py host-path tracer
affects: [11-02, 11-03, phase-12-demo]

actuals:
  tokens: 8000
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns: [library-core + thin CLI adapter, RELY_MAX_RETRIES bridge for CLI max_retries]

key-files:
  created:
    - exercise-ai/service.py
    - exercise-ai/tests/test_service.py
  modified:
    - exercise-ai/main.py
    - exercise-ai/tests/test_main.py
    - exercise-ai/tests/test_failover.py
    - exercise-ai/tests/test_output_paths.py
    - exercise-ai/tests/test_token_usage.py

key-decisions:
  - "D-01/D-02: generate_batch(request) -> ExerciseBatch only"
  - "CLI max_retries bridged via temporary RELY_MAX_RETRIES (no kwargs)"
  - "Pure move only — hygiene deferred to 11-02/11-03"

patterns-established:
  - "main → service → pipeline import direction; service never imports main"
  - "run() owns presentation and process exit; service returns or raises"

requirements-completed: [EMBED-01, EMBED-03]

coverage:
  - id: D1
    description: Host calls generate_batch and receives ExerciseBatch or Exception without process exit
    requirement: EMBED-01
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_service.py
        status: pass
  - id: D2
    description: CLI adapter preserves print/--out/sys.exit; patches re-pointed to service
    requirement: EMBED-03
    verification:
      - kind: unit
        ref: pytest exercise-ai -q (138 passed)
        status: pass
---

## Accomplishments

- Created `exercise-ai/service.py` with `generate_batch(request) -> ExerciseBatch` (begin_run → resolve_max_retries(None) → generate_with_failover → flush in finally).
- Refactored `main.run` into CLI adapter calling `generate_batch`; bridged `--max-retries` via temporary `RELY_MAX_RETRIES`.
- Added `test_service.py` tracer; re-pointed failover/main/output_paths/token_usage patches onto `service`.
- Full offline suite: **138 passed**.

## Commits

- `bf77c0f` — feat(11-01): extract generate_batch service seam
- `c344920` — test(11-01): re-point patches onto service module

## Deviations

None — stayed within pure-move scope.

## Next

Plan 11-02: domain 1–40, error subclasses, scoped env restore, guarded flush.
