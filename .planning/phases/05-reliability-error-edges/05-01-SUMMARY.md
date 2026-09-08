---
phase: 05-reliability-error-edges
plan: 01
subsystem: reliability
tags: [retry, reliability, RuntimeError, retriable, argparse, pytest, openai, gemini]

requires:
  - phase: 04-cli-argparse
    provides: dual-output CLI (text stdout + required --out), argparse surface, LOG-01
provides:
  - generate_validated_batch Phase 6 hook with bounded regenerations
  - resolve_max_retries CLI > RELY_MAX_RETRIES > default 1 (0–3)
  - ERR-05 typed empty OpenAI choices + Gemini non-APIError mapping
  - Aggregate duration log total_ms + chamadas without secrets
affects: [06-math-quality]

actuals:
  tokens: 12000
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "reliability.generate_validated_batch owns retry; main only orchestrates I/O"
    - "RuntimeError.retriable True/False marker for invalid-response vs permanent API"
    - "Same request/prompt every regeneration; no prompt repair"

key-files:
  created:
    - exercise-ai/reliability.py
    - exercise-ai/tests/test_reliability.py
  modified:
    - exercise-ai/main.py
    - exercise-ai/generator.py
    - exercise-ai/generator_gemini.py
    - exercise-ai/tests/test_main.py
    - exercise-ai/tests/test_generators.py
    - exercise-ai/tests/test_logging_security.py
    - README.md
    - exercise-ai/.env.example
    - .planning/ROADMAP.md

key-decisions:
  - "Refusal marked retriable=False (policy will not fix on regen)"
  - "Gemini except Exception routes through map_gemini_error with retriable=False"
  - "Aggregate stderr line: duração total_ms=… chamadas=N"

patterns-established:
  - "invalid_llm_response(msg) → RuntimeError with retriable=True"
  - "_permanent_api_error(msg) → RuntimeError with retriable=False from mappers"
  - "Phase 6 math must raise into generate_validated_batch (ValueError or retriable=True)"

requirements-completed: [RELY-01, RELY-02, ERR-05]

coverage:
  - id: D1
    description: Bounded regeneration after structural validation failure (CLI/env 0–3)
    requirement: RELY-01
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_reliability.py#test_validation_fail_once_then_success
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_reliability.py#test_exhaustion_default_one_retry
        status: pass
    human_judgment: false
  - id: D2
    description: Aggregate duration + chamadas logged without secrets
    requirement: RELY-02
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_logging_security.py#test_duration_aggregate_never_contains_keys
        status: pass
    human_judgment: false
  - id: D3
    description: Empty OpenAI choices and Gemini non-APIError typed PT RuntimeError
    requirement: ERR-05
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_generators.py#test_openai_empty_choices_typed_retriable
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_generators.py#test_gemini_non_apierror_mapped
        status: pass
    human_judgment: false
  - id: D4
    description: Permanent auth not retried; invalid-response retried
    requirement: RELY-01
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_reliability.py#test_permanent_auth_no_regen
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_reliability.py#test_retriable_invalid_response_then_success
        status: pass
    human_judgment: false
  - id: D5
    description: Dual-output only on final success; --max-retries / RELY_MAX_RETRIES documented
    requirement: RELY-01
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_main.py#test_multi_attempt_failure_no_out_empty_stdout
        status: pass
      - kind: other
        ref: README.md + exercise-ai/.env.example RELY_MAX_RETRIES
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-09-08
status: complete
---

# Phase 5: Reliability & Error Edges Summary

**Bounded regenerate loop in `reliability.py` with `retriable` API edges, aggregate `total_ms`/`chamadas`, and public `--max-retries` / `RELY_MAX_RETRIES`**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-09-08T10:43:00-03:00
- **Completed:** 2026-09-08T11:10:00-03:00
- **Tasks:** 3
- **Files modified:** 11

## Accomplishments

- `generate_validated_batch` regenerates on structural `ValueError` and `retriable=True` invalid LLM responses; permanent API errors abort immediately
- ERR-05: empty OpenAI `choices` + Gemini non-`APIError` use typed PT `RuntimeError` with sanitized `[API:*]`
- Stderr stages `Gerando…` / `Validando…` / `Nª Regeneração`; final duration aggregate; dual-output only on success
- README + `.env.example` document retry contract; Phase 6 hook noted in module docstring and README

## Task Commits

1. **Task 1: Tracer — reliability loop** - `e5c173c` (feat)
2. **Task 2: ERR-05 edges + markers** - `a6eab15` (feat)
3. **Task 3: Docs + ROADMAP polish** - `40bab62` (docs)

**Plan metadata:** (this SUMMARY commit)

## Files Created/Modified

- `exercise-ai/reliability.py` — `resolve_max_retries`, `generate_validated_batch`, classification helpers
- `exercise-ai/main.py` — `--max-retries`; delegates to reliability; dual-output unchanged
- `exercise-ai/generator.py` / `generator_gemini.py` — `invalid_llm_response` / permanent markers; WR-03/WR-04
- `exercise-ai/tests/test_reliability.py` (+ updates to main/generators/logging tests)
- `README.md`, `exercise-ai/.env.example`, `.planning/ROADMAP.md`

## Decisions Made

- Refusal → `retriable=False` (consistent non-retry)
- Unmarked `RuntimeError` fails through (safe default)
- Left `DEFAULT_GEMINI_MODEL` as already committed in repo (no model-string change in this plan)

## Deviations from Plan

None - plan executed exactly as written

## Issues Encountered

None

## User Setup Required

None - no external service configuration required. Optional: set `RELY_MAX_RETRIES` in `.env` (documented in `.env.example`).

## Next Phase Readiness

- Phase 6 can raise math `ValueError` (or `retriable=True`) into `generate_validated_batch` without a second retry path
- `prompts.py` unchanged; no failover / prompt repair

---
*Phase: 05-reliability-error-edges*
*Completed: 2026-09-08*
