---
phase: 04-cli-argparse
plan: 01
subsystem: cli
tags: [argparse, dual-output, pydantic, pytest]

requires:
  - phase: 03-tests-logging-docs
    provides: pytest suite, LOG-01/LOG-02 logging, validate_exercise_batch
provides:
  - argparse CLI with PT long flags and required --out
  - run(request) pipeline with text stdout + JSON file
  - optional --provider override with D-11 missing-key messages
affects: [05-reliability, 06-math-quality]

actuals:
  tokens: 12000
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns: [dual-output text stdout + JSON --out, PT argparse ArgumentTypeError, LLM_PROVIDER env override per run]

key-files:
  created: []
  modified:
    - exercise-ai/main.py
    - exercise-ai/tests/test_main.py
    - exercise-ai/tests/test_logging_security.py
    - README.md
    - .planning/ROADMAP.md

key-decisions:
  - "D-14 confirmed proceed-d14: text stdout + required --out JSON"
  - "Provider override via os.environ LLM_PROVIDER for the process"
  - "Quantidade ceiling enforced in argparse type=_positive_quantidade (máximo 40)"

patterns-established:
  - "format_batch_text for D-15 layout; JSON only written to --out"
  - "build_parser() + main(argv) for testable CLI without subprocess"

requirements-completed: [CLI-04]

coverage:
  - id: D1
    description: Dual-output success path — D-15 text on stdout and JSON at --out
    requirement: CLI-04
    verification:
      - kind: unit
        ref: "exercise-ai/tests/test_main.py::test_run_success_text_stdout_and_json_out"
        status: pass
    human_judgment: false
  - id: D2
    description: Argparse rejects invalid dificuldade/provider/quantidade and missing --out pre-LLM
    requirement: CLI-04
    verification:
      - kind: unit
        ref: "exercise-ai/tests/test_main.py::test_cli_rejects_quantidade_zero_and_over_ceiling"
        status: pass
    human_judgment: false
  - id: D3
    description: --provider override and D-11 specific missing-key message
    requirement: CLI-04
    verification:
      - kind: unit
        ref: "exercise-ai/tests/test_main.py::test_cli_missing_provider_key_specific_message"
        status: pass
    human_judgment: false
  - id: D4
    description: README documents flags including --out and --provider; ROADMAP D-14 aligned
    requirement: CLI-04
    verification:
      - kind: other
        ref: "README.md + .planning/ROADMAP.md Phase 4 success criteria"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-09-08
status: complete
---

# Phase 4: CLI argparse Summary

**CLI gera exercícios com flags PT, texto legível no stdout e JSON obrigatório em `--out`.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-09-08T12:32:31Z
- **Completed:** 2026-09-08T12:45:00Z
- **Tasks:** 3/3
- **Files modified:** 5

## Accomplishments

- Replaced `run_demo` with `run(request, out_path)` + `format_batch_text` (D-13/D-14/D-15)
- Full argparse surface: demo defaults, required `--out`, `--provider`, quantidade 1–40, PT help/errors
- README + ROADMAP success criteria updated for dual-output contract; `pytest exercise-ai -q` → 39 passed

## Task Commits

1. **Task 1: Confirm D-14** - decision `proceed-d14` (no code commit)
2. **Task 2–3: Tracer + expansion** - `b8001ab` (feat)
3. **Task 3 docs: README + ROADMAP** - `0ecca1a` (docs)

## Deviations

- Tasks 2 and 3 implemented in one production commit (shared `main.py` surface); docs split into a second commit. Checkpoint Task 1 had no code.

## Self-Check: PASSED

- key-files exist; commits grep `04-01`; suite green
