---
phase: 10-interactive-cli-wizard
plan: 01
subsystem: cli-ux
tags: [wizard, gerar, argparse, reasoning, medium, input-mock]

requires:
  - phase: 04-cli-argparse
    provides: GenerationRequest CLI surface + run() entry + demo defaults
  - phase: 09-token-usage-observability
    provides: reasoning.py DEFAULT_REASONING_EFFORT / resolve_reasoning_effort
provides:
  - Interactive PT wizard via first token `gerar` (wizard.py)
  - Tips under each of 7 prompts; Enter defaults; JSON path re-prompt
  - Global DEFAULT_REASONING_EFFORT = medium (D-08)
  - Offline mocked input/isatty tests (test_wizard.py)
affects: [operator-ux, ci-argparse-coexistence]

actuals:
  tokens: 14000
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns: [gerar-dispatch-before-argparse, injectable-input-isatty, thin-wizard-calls-run]

key-files:
  created:
    - exercise-ai/wizard.py
    - exercise-ai/tests/test_wizard.py
  modified:
    - exercise-ai/main.py
    - exercise-ai/reasoning.py
    - exercise-ai/tests/test_reasoning.py
    - exercise-ai/.env.example
    - README.md

key-decisions:
  - "First token gerar opens wizard; extra tokens rejected with PT message (D-01)"
  - "Argparse path unchanged without gerar (D-02; WIZ-03)"
  - "Wizard always calls main.run — no failover re-implementation (D-15)"
  - "DEFAULT_REASONING_EFFORT medium globally; Enter → medium (D-08)"
  - "Reasoning tip: Grok/Gemini honor + gpt-4o-mini may ignore (D-09)"

patterns-established:
  - "wizard.collect_wizard_answers injectable input_fn/isatty_fn for CI"
  - "Tips constants on stdout; errors/non-TTY on stderr"

requirements-completed: [WIZ-01, WIZ-02, WIZ-03]

coverage:
  - id: D1
    description: gerar opens tip-backed 7-question wizard on TTY; non-TTY fails without input()
    requirement: WIZ-01
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_wizard.py::test_collect_defaults_and_all_tips
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_wizard.py::test_non_tty_fails_without_input
        status: pass
    human_judgment: false
  - id: D2
    description: Answers map to GenerationRequest + env + run(); Enter defaults; JSON re-prompt; reasoning medium
    requirement: WIZ-02
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_wizard.py::test_gerar_main_calls_run_with_mapped_request
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_wizard.py::test_provider_enter_leaves_unset
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_reasoning.py::test_resolve_reasoning_default_medium
        status: pass
    human_judgment: false
  - id: D3
    description: Argparse coexistence; mocked input; no live LLM; no profiles/max-retries prompts
    requirement: WIZ-03
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_wizard.py::test_argparse_path_does_not_invoke_wizard
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_wizard.py::test_no_profile_or_max_retries_prompts
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-09-15
status: complete
---

# Phase 10: Interactive CLI Wizard — Plan 01 Summary

**Portuguese `gerar` wizard maps tip-backed Q&A into existing `main.run`, with global reasoning default `medium` and argparse kept for CI.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 2/2
- **Commits:** 4 (reasoning default; wizard+main; README; planning docs)

## Accomplishments

- `exercise-ai/wizard.py` — TTY guard, 7 prompts + tips, defaults, re-prompt invalid enums/bounds and empty JSON path
- `main.main` detects first token `gerar` before argparse; rejects extra tokens; calls `run_wizard` → `run`
- `DEFAULT_REASONING_EFFORT = "medium"` aligned across reasoning.py, argparse help, `.env.example`, README, tests
- Offline `test_wizard.py` (8 tests) + updated `test_reasoning.py`; full suite 133 passed

## Deviations

- None vs 10-01-PLAN / D-01…D-15; deferred items (GUI, profiles, max-retries in wizard, argparse replacement, failover redesign) not implemented

## Verification

- `pytest exercise-ai/tests/test_wizard.py -q` → 8 passed
- `pytest exercise-ai/tests/test_reasoning.py -q` → 12 passed
- `pytest exercise-ai -q` → 133 passed
