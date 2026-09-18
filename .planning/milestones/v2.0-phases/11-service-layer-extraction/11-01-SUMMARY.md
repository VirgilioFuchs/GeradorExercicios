---
phase: 11-service-layer-extraction
plan: 01
subsystem: api
tags: [service-layer, embed, generate_batch, pytest, cli-adapter]

requires:
  - phase: 10-interactive-cli-wizard
    provides: wizard enters via main.run; CLI argparse surface
provides:
  - Host-callable service.generate_batch(request) -> ExerciseBatch
  - main.run as CLI adapter (print/--out/fail-log/exit)
  - Tracer coverage for return/raise-without-exit
affects:
  - 11-02 env restore and error subclasses
  - 11-03 encoding timeout README
  - 12-local-embed-demo

actuals:
  tokens: 12818
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "main → service → pipeline import direction (no service→main)"
    - "CLI max_retries bridged via RELY_MAX_RETRIES env (no kwargs on generate_batch)"
    - "Token begin/flush owned by service; run keeps idempotent flush safety net"

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
  - "Pure move only: generate_batch(request) with env bridge for CLI max_retries"
  - "begin_run/flush live in service; run retains finally flush as safety net"

patterns-established:
  - "Pattern: host patches service.generate_with_failover / resolve_max_retries, not main"
  - "Pattern: service never imports main (avoids load_dotenv at host import)"

requirements-completed: [EMBED-01, EMBED-03]

coverage:
  - id: D1
    description: "Host-callable generate_batch returns ExerciseBatch without stdout exercise dump"
    requirement: EMBED-01
    verification:
      - kind: unit
        ref: "exercise-ai/tests/test_service.py#test_generate_batch_returns_batch_without_stdout_dump"
        status: pass
    human_judgment: false
  - id: D2
    description: "Library path raises normal Exception subclasses without SystemExit"
    requirement: EMBED-01
    verification:
      - kind: unit
        ref: "exercise-ai/tests/test_service.py#test_generate_batch_raises_normal_exception"
        status: pass
    human_judgment: false
  - id: D3
    description: "CLI adapter still writes --out and exits on failure; full suite green after patch re-point"
    requirement: EMBED-03
    verification:
      - kind: unit
        ref: "exercise-ai/tests/test_service.py#test_run_still_writes_out_and_exits_on_failure"
        status: pass
      - kind: unit
        ref: "pytest exercise-ai -q (138 passed)"
        status: pass
    human_judgment: false
  - id: D4
    description: "service.py does not import main (D-15)"
    requirement: EMBED-01
    verification:
      - kind: unit
        ref: "exercise-ai/tests/test_service.py#test_service_source_does_not_import_main"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-09-16
status: complete
---

# Phase 11 Plan 01: Service Seam Extraction Summary

**Pure move of `service.generate_batch(request) -> ExerciseBatch` with `main.run` as CLI adapter; suite green after re-pointing monkeypatches**

## Performance

- **Duration:** 6 min
- **Started:** 2026-09-16T14:45:02Z
- **Completed:** 2026-09-16T14:50:35Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- Created embed seam `service.generate_batch` (begin_run → resolve_max_retries(None) → failover → flush)
- Refactored `main.run` into CLI adapter: presentation/`--out`/fail-log/`sys.exit` preserved; CLI `--max-retries` bridged via temporary `RELY_MAX_RETRIES`
- Tracer + re-pointed pins: full offline suite 138 passed; no `main` import in `service.py`

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end host path tracer** - `bf77c0f` (feat)
2. **Task 2: Re-point main-internal patches** - `c344920` (test)

**Plan metadata:** `4278900` (docs: complete plan); `421e0e8` (docs: STATE position)

## Files Created/Modified
- `exercise-ai/service.py` - Public `generate_batch` host seam
- `exercise-ai/main.py` - CLI adapter delegating to service
- `exercise-ai/tests/test_service.py` - Host-path tracer (return/raise/no-main-import/run adapter)
- `exercise-ai/tests/test_main.py` - Source contract + max-retries spy via service
- `exercise-ai/tests/test_failover.py` - Patch `service.generate_with_failover`
- `exercise-ai/tests/test_output_paths.py` - Patch service for success/fail path tests
- `exercise-ai/tests/test_token_usage.py` - Patch service for flush-in-finally coverage

## Decisions Made
- CLI `max_retries` bridged through `RELY_MAX_RETRIES` for the service call only (restore prior presence/absence) so `generate_batch` stays kwargs-free (D-01)
- Token lifecycle owned by service; `run()` keeps idempotent `flush_token_usage()` in `finally` as safety net

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
Ready for 11-02 (domain bounds, error subclasses, scoped env restore, FS hygiene). Do not mix encoding/timeout/README here.

## TDD Gate Compliance
Task 2 marked `tdd="true"`: RED was the natural suite breakage after Task 1 pure move (patches targeting removed `main` bindings); GREEN is commit `c344920` restoring green suite. No separate RED commit — existing tests served as the failing gate.

## Self-Check: PASSED

- FOUND: exercise-ai/service.py
- FOUND: exercise-ai/tests/test_service.py
- FOUND: .planning/phases/11-service-layer-extraction/11-01-SUMMARY.md
- FOUND: bf77c0f
- FOUND: c344920

---
*Phase: 11-service-layer-extraction*
*Completed: 2026-09-16*
