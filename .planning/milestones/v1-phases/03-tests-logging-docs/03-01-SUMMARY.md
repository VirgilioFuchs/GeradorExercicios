---
phase: 03-tests-logging-docs
plan: 01
subsystem: testing
tags: [pytest, logging, validation, openai, gemini, readme, secret-redaction]

requires:
  - phase: 02-validation-error-handling
    provides: validate_exercise_batch, map_openai_error, map_gemini_error, run_demo fail-fast
provides:
  - Durable pytest suite under exercise-ai/tests/ (no live LLM)
  - LOG-01 stderr events (start/params/success/failure)
  - LOG-02 sanitized [API:*] detail logs + anti-leakage tests
  - Root README.md in Portuguese (setup/env/run/pytest)
affects: [ship, verify-work, onboarding]

actuals:
  tokens: 8718
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "pytest factories in conftest + sys.path to exercise-ai/"
    - "[API:*] logs type+status only; never raw str(exc)"
    - "LOG-01 via stdlib logging StreamHandler bound to current sys.stderr"

key-files:
  created:
    - exercise-ai/tests/conftest.py
    - exercise-ai/tests/test_validator.py
    - exercise-ai/tests/test_generators.py
    - exercise-ai/tests/test_main.py
    - exercise-ai/tests/test_logging_security.py
    - README.md
  modified:
    - exercise-ai/main.py
    - exercise-ai/generator.py
    - exercise-ai/generator_gemini.py

key-decisions:
  - "TEST-02 chave ausente = missing/invalid exercicios on validator (not API env keys)"
  - "LOG-01 events asserted via redirected stderr (dynamic stderr stream handler)"
  - "OpenAI generic fallback is fixed PT without embedding raw exc (WR-02)"

patterns-established:
  - "Pattern: durable suite promotes Phase 2 ephemeral verifies into pytest modules"
  - "Pattern: security tests inject distinctive dummy keys and assert absence in stderr"

requirements-completed: [TEST-01, TEST-02, LOG-01, LOG-02, SCAF-04]

coverage:
  - id: D1
    description: "Validator TEST-02 suite including chave ausente on exercicios"
    requirement: TEST-02
    verification:
      - kind: unit
        ref: "pytest exercise-ai/tests/test_validator.py -q"
        status: pass
    human_judgment: false
  - id: D2
    description: "Mocked OpenAI/Gemini mappers + ERR-01 missing API keys"
    requirement: TEST-01
    verification:
      - kind: unit
        ref: "pytest exercise-ai/tests/test_generators.py -q"
        status: pass
    human_judgment: false
  - id: D3
    description: "run_demo stdout purity + LOG-01 start/params/success/failure"
    requirement: LOG-01
    verification:
      - kind: unit
        ref: "pytest exercise-ai/tests/test_main.py -q"
        status: pass
    human_judgment: false
  - id: D4
    description: "LOG-02 anti-leakage of dummy API key values on mapper/failure paths"
    requirement: LOG-02
    verification:
      - kind: unit
        ref: "pytest exercise-ai/tests/test_logging_security.py -q"
        status: pass
    human_judgment: false
  - id: D5
    description: "Root README documents setup, env, run, pytest, stdout/stderr"
    requirement: SCAF-04
    verification:
      - kind: other
        ref: "python keyword check on README.md + pytest exercise-ai -q"
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-09-04
status: complete
---

# Phase 3 Plan 01: Tests, Logging & Docs Summary

**Durable pytest suite (31 tests), sanitized [API:*] logs, LOG-01 stderr events, and Portuguese root README — all without live LLM calls.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 3/3
- **Files modified:** 9
- **Commits:** 4 (3 task + 1 docs metadata)

## Accomplishments

- Pytest harness under `exercise-ai/tests/` with Pydantic factories and path grounding
- Full TEST-02 validator coverage including `Chave 'exercicios' ausente`
- LOG-01 events in `main.py`; LOG-02 type+status redaction in OpenAI/Gemini mappers
- Anti-leakage, mapper, and `run_demo` contracts promoted from Phase 2 verifies
- Root `README.md` documents setup, env vars, run, pytest, stdout vs stderr

## Task Commits

| Task | Commit | Message |
|------|--------|---------|
| 1 Tracer — pytest + TEST-02 | `1e5a006` | test(03-01): add pytest harness and core TEST-02 validator suite |
| 2 LOG-01/02 + EVAL suite | `79ef5a0` | feat(03-01): add LOG-01 events, LOG-02 redaction, and full EVAL suite |
| 3 Root README | `e78fb67` | docs(03-01): add root README with setup, env, run, and pytest |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] LOG-01 events invisible under redirect_stderr / empty caplog**
- **Found during:** Task 2
- **Issue:** `logging.StreamHandler(sys.stderr)` bound the stream object at init; `propagate=False` also left `caplog` empty
- **Fix:** `_StderrStream` wrapper that always writes to current `sys.stderr`; tests assert LOG-01 via redirected stderr
- **Files modified:** `exercise-ai/main.py`, `exercise-ai/tests/test_main.py`, `exercise-ai/tests/test_logging_security.py`
- **Commit:** `79ef5a0`

**2. [Rule 2 - Critical] Redact secrets in unparseable/refusal debug dumps**
- **Found during:** Task 2 (threat T-03-01 / D-06)
- **Issue:** Gemini unparseable and OpenAI refusal paths could echo env key values in response/refusal text
- **Fix:** `_redact_env_secrets` before printing those dumps
- **Files modified:** `exercise-ai/generator.py`, `exercise-ai/generator_gemini.py`
- **Commit:** `79ef5a0`

## Decisions Made

- TEST-02 "chave ausente" remains validator `exercicios` only; ERR-01 missing API keys live in `test_generators.py`
- No GitHub Actions, Phoenix, or persistent log files (D-07, D-10)

## Known Stubs

None.

## Threat Flags

None beyond plan threat model mitigations (T-03-01..T-03-04 addressed).

## Self-Check: PASSED

- All key artifacts present (tests, README, SUMMARY)
- Commits `1e5a006`, `79ef5a0`, `e78fb67` found in git log
- Final `pytest exercise-ai -q`: 31 passed
