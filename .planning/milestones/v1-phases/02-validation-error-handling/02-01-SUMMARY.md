---
phase: 02-validation-error-handling
plan: 01
subsystem: validation
tags: [python, pydantic, openai, gemini, validation, error-handling]

requires:
  - phase: 01-project-setup-llm-pipeline
    provides: ExerciseBatch models, linear generate→validate→stdout pipeline, OpenAI/Gemini generators
provides:
  - Semantic post-parse validation with field paths and quantity checks
  - Two-layer validation errors ([VALIDAÇÃO] log + plain PT ValueError)
  - VALIDATION_REPORT_MODE all | first_exercise
  - OpenAI and Gemini typed API error mappers with [API:*] detail logs
  - Dual-key missing message (GEMINI_API_KEY + LLM_API_KEY)
  - CLI stage labels and fail-fast plain stderr (D-05)
affects: [03-tests-logging-docs]

actuals:
  tokens: 3068
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - Two-layer stderr (user plain PT vs [VALIDAÇÃO]/[API:*] detail)
    - Status-code Gemini error table with GEMINI_ERROR_CLASSIFICATION docs
    - map_openai_error / map_gemini_error testable helpers

key-files:
  created: []
  modified:
    - exercise-ai/validator.py
    - exercise-ai/main.py
    - exercise-ai/generator.py
    - exercise-ai/generator_gemini.py

key-decisions:
  - "Gemini priority-1 named subclasses N/A on installed google-genai — documented and used status_code table only"
  - "Shared Portuguese missing-key sentence naming both GEMINI_API_KEY and LLM_API_KEY"

patterns-established:
  - "Validation failures: stderr [VALIDAÇÃO]+JSON then raise ValueError(plain PT)"
  - "API failures: stderr [API:provider] then raise RuntimeError(plain PT)"
  - "main user line is always print(str(err)) with no wrapper prefixes"

requirements-completed:
  - VALD-01
  - VALD-02
  - VALD-03
  - VALD-04
  - VALD-05
  - ERR-01
  - ERR-02
  - ERR-03
  - ERR-04

coverage:
  - id: D1
    description: "Semantic validator rejects bad type, empty/malformed exercicios, wrong quantity, whitespace fields with path messages"
    requirement: "VALD-01"
    verification:
      - kind: unit
        ref: "python .planning/_verify_02_01_t1.py (Task 1 automated)"
        status: pass
    human_judgment: false
  - id: D2
    description: "VALIDATION_REPORT_MODE all vs first_exercise; [VALIDAÇÃO]+raw JSON on failure without prefixing ValueError"
    requirement: "VALD-05"
    verification:
      - kind: unit
        ref: "Task 1 automated report-mode + stderr assertions"
        status: pass
    human_judgment: false
  - id: D3
    description: "OpenAI/Gemini map_*_error helpers + dual-key missing message + ERR-03 empty/refusal/unparseable"
    requirement: "ERR-02"
    verification:
      - kind: unit
        ref: "Task 2 automated map_openai_error / map_gemini_error / mock generate paths"
        status: pass
    human_judgment: false
  - id: D4
    description: "run_demo stdout JSON-only with Gerando/Validando on stderr; ValueError → SystemExit(1) plain stderr"
    requirement: "ERR-04"
    verification:
      - kind: unit
        ref: "Task 2 automated main.run_demo mocks"
        status: pass
    human_judgment: false

duration: 25 min
completed: 2026-09-04
status: complete
---

# Phase 2 Plan 01: Validation & Error Handling Summary

**Semantic validation and typed OpenAI/Gemini API errors with two-layer Portuguese diagnostics and fail-fast CLI.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-09-04T11:46:00Z
- **Completed:** 2026-09-04T12:15:00Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Expanded `validate_exercise_batch` for isinstance, list/empty checks, exact quantity, strip-empty fields, and `VALIDATION_REPORT_MODE`
- Wired two-layer validation stderr (`[VALIDAÇÃO]` + raw JSON) with plain PT `ValueError` text
- Added `map_openai_error` / `map_gemini_error` with `[API:openai|gemini]` detail logs and dual-key missing messages
- CLI: `Gerando…` / `Validando…` on stderr; `print(str(err))` only; exit 1; stdout JSON UTF-8 on success

## Task Commits

1. **Task 1: Tracer — semantic validator + stage labels** - `e8664b8` (feat)
2. **Task 2: Expand — API/config error mapping** - `eeac3d7` (feat)

## Files Created/Modified

- `exercise-ai/validator.py` — Semantic validation + report mode + `[VALIDAÇÃO]` dump
- `exercise-ai/main.py` — Stage labels; plain `print(str(...))` errors; fail-fast
- `exercise-ai/generator.py` — Dual-key message; `map_openai_error`; refusal/parsed-None logs
- `exercise-ai/generator_gemini.py` — `GEMINI_ERROR_CLASSIFICATION:`; `map_gemini_error`; empty/unparseable

## Decisions Made

- Installed `google-genai` has no timeout/rate/auth/connection named subclasses → documented `priority-1 N/A on this SDK` and implemented status_code table (401/403, 429, 408/504, network heuristics, generic)
- Unified missing-key Portuguese sentence naming both env vars across `_resolve_provider` and both `get_client` helpers

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] OpenAI exception harness AttributeError on `response=None`**
- **Found during:** Task 2 verify
- **Issue:** Plan `_make()` only caught `TypeError`; current `openai` SDK raises `AttributeError` when constructing status errors with `response=None`, aborting before the subclass fallback
- **Fix:** Local verify harness catches broader `Exception` so category mapping still exercises `map_openai_error` (implementation unchanged)
- **Files modified:** none (production); verify harness only
- **Verification:** Task 2 automated verify passed after harness broaden
- **Commit hash:** eeac3d7 (feat commit; harness not committed)

**Total deviations:** 1 auto-fixed (verify harness only). **Impact:** none on production behavior; plan script as pasted may still trip on this SDK until `_make` catches `Exception`.

## Issues Encountered

None

## Self-Check: PASSED

- Re-ran Task 1 and Task 2 automated verifies from repo root — both passed
- must_haves covered: validator paths, dual-key, mappers, CLI contract
- No retry loops, pytest suites, or agent frameworks added

## Next Phase Readiness

Phase 2 plan work complete — ready for phase verification gate, then Phase 3 (tests/logging/docs).

## Self-Check: PASSED
