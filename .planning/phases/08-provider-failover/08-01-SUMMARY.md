---
phase: 08-provider-failover
plan: 01
subsystem: reliability
tags: [failover, openai, gemini, api_error_kind, stderr]

requires:
  - phase: 05-reliability-error-edges
    provides: generate_validated_batch RELY loop + permanent/retriable error contract
  - phase: 09-token-usage-observability
    provides: begin_run / finally flush_token_usage preserved across envelope
provides:
  - Thin failover envelope `generate_with_failover` (OpenAI ↔ Gemini only)
  - `api_error_kind` on permanent mappers (auth vs availability)
  - Offline D-12 mocked matrix in test_failover.py
  - `[FAILOVER]` stderr without secrets
affects: [10-interactive-wizard, operator-resilience]

actuals:
  tokens: 12000
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns: [thin-failover-envelope, api_error_kind-eligibility, injectable-switch_provider]

key-files:
  created:
    - exercise-ai/failover.py
    - exercise-ai/tests/test_failover.py
  modified:
    - exercise-ai/generator.py
    - exercise-ai/generator_gemini.py
    - exercise-ai/main.py
    - exercise-ai/tests/test_main.py
    - exercise-ai/tests/test_output_paths.py
    - exercise-ai/tests/test_token_usage.py
    - README.md

key-decisions:
  - "Envelope in failover.py; main.run calls generate_with_failover (D-07)"
  - "Eligible kinds: timeout|rate_limit|connection|generic; auth/refusal/invalid/math never (D-01; D-02; D-08)"
  - "Grok excluded from peer pair (D-06); at most one switch (D-09)"
  - "Default switch mutates LLM_PROVIDER; injectables for offline tests"

patterns-established:
  - "is_failover_eligible: retriable is False AND api_error_kind in eligible set"
  - "[FAILOVER] primary → secondary (kind) + [FAILOVER] usado: peer — never secrets"

requirements-completed: [FAILOVER-01, FAILOVER-02, FAILOVER-03]

coverage:
  - id: D1
    description: Eligible primary API failure retries once on OpenAI↔Gemini peer via generate_validated_batch
    requirement: FAILOVER-01
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_failover.py::test_openai_to_gemini_failover_success
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_failover.py::test_gemini_to_openai_eligible_kinds
        status: pass
    human_judgment: false
  - id: D2
    description: Envelope reuses generate_validated_batch only — no nested RELY/math loop
    requirement: FAILOVER-02
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_failover.py::test_openai_to_gemini_failover_success
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_failover.py::test_secondary_failure_propagates_no_third
        status: pass
    human_judgment: false
  - id: D3
    description: "[FAILOVER] stderr identifies providers without secrets; --out works after secondary"
    requirement: FAILOVER-03
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_failover.py::test_run_failover_writes_out_and_redacts
        status: pass
    human_judgment: false

duration: ~40min
completed: 2026-09-15
status: complete
---

# Phase 8: Provider Failover Summary

**OpenAI ↔ Gemini auto-failover via a thin envelope around `generate_validated_batch`, with `api_error_kind` discrimination and a full offline D-12 mock matrix.**

## Performance

- **Duration:** ~40 min
- **Tasks:** 3/3
- **Commits:** 3 (implementation, docs, planning)

## Accomplishments

- Permanent API mappers tag `api_error_kind` (`auth` / `timeout` / `rate_limit` / `connection` / `generic` / `refusal`).
- `failover.generate_with_failover` switches at most once; Grok skips; missing secondary key fails in PT before second call.
- `main.run` wired through the envelope; token `begin_run` / `finally` flush unchanged.
- README documents operator-facing failover rules (no `--no-failover`, Grok excluded).

## Verification

```text
pytest exercise-ai/tests/test_failover.py -q  → 16 passed
pytest exercise-ai -q                         → 125 passed
```

## Deviations

- Semgrep MCP timed out on scan request; not blocking — LOG-02 redaction covered by tests.
- Existing tests that patched `main.generate_validated_batch` updated to `generate_with_failover`.

## Self-Check: PASSED

- [x] failover.py exists with `is_failover_eligible` + `generate_with_failover`
- [x] api_error_kind on OpenAI + Gemini permanent mappers
- [x] main.run uses envelope
- [x] test_failover.py D-12 matrix
- [x] README failover note
- [x] FAILOVER-01..03 checkboxes
