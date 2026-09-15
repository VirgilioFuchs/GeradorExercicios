---
phase: 09-token-usage-observability
plan: 01
subsystem: observability
tags: [token-usage, ndjson, stderr, openai, gemini, grok]

requires:
  - phase: 07-continuous-integration
    provides: Offline pytest CI contract (`pytest exercise-ai -q`)
provides:
  - Injectable `TokenUsageCollector` + NDJSON flush under day/provider folders
  - Provider extractors (OpenAI / Gemini / Grok) + approximate USD rate table
  - `[USAGE]` stderr lines + end-of-run summary; RELY attempt/error/success tags
affects: [08-provider-failover, operator-cost-visibility]

actuals:
  tokens: ~0
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns: [injectable-TOKEN_USAGE_DIR, ndjson-append-flush, indisponivel-sentinel, finally-only-flush]

key-files:
  created:
    - exercise-ai/token_usage/__init__.py
    - exercise-ai/token_usage/collector.py
    - exercise-ai/token_usage/extract.py
    - exercise-ai/token_usage/rates.py
    - exercise-ai/token-usage/.gitkeep
    - exercise-ai/tests/test_token_usage.py
  modified:
    - exercise-ai/generator.py
    - exercise-ai/generator_gemini.py
    - exercise-ai/reliability.py
    - exercise-ai/main.py
    - .gitignore
    - README.md

key-decisions:
  - "NDJSON append under token-usage/{YYYY-MM-DD}/{provider}.ndjson (D-01..D-03)"
  - "Missing usage/USD = string indisponível — never fabricate 0 (D-09)"
  - "Flush only in main.run finally; buffer cleared (idempotent) (D-04)"
  - "Grok USD prefers cost_in_usd_ticks/1e10; OpenAI/Gemini use local rate table (D-14)"

requirements-completed: [TOKEN-01, TOKEN-02, TOKEN-03]

duration: ~45min
completed: 2026-09-15
---

# Phase 09 Plan 01 — Summary

## What shipped

Token/cost observability for OpenAI, Gemini, and Grok: in-memory event accumulation per LLM round-trip, `[USAGE]` on stderr, and end-of-run NDJSON append under `exercise-ai/token-usage/{YYYY-MM-DD}/{provider}.ndjson`. Missing fields surface as `indisponível`. RELY retags validation regenerations as `attempt`. No new PyPI deps; no usage fields in `--out` exercise JSON; no Phase 8 failover.

## Files changed (this plan)

| File | Change |
|------|--------|
| `exercise-ai/token_usage/*` | **Created** — collector, extractors, rates |
| `exercise-ai/token-usage/.gitkeep` | **Created** — trackable empty data dir |
| `exercise-ai/generator.py` | **Modified** — OpenAI/Grok record + duration |
| `exercise-ai/generator_gemini.py` | **Modified** — per-API-call usage record |
| `exercise-ai/reliability.py` | **Modified** — retag attempt/error for RELY |
| `exercise-ai/main.py` | **Modified** — `begin_run` + `flush` in `finally` |
| `exercise-ai/tests/test_token_usage.py` | **Created** — mocked extract/append/redaction/RELY/summary |
| `.gitignore` | **Modified** — ignore generated NDJSON; keep `.gitkeep` |
| `README.md` | **Modified** — token-usage layout + approximate rates |

## Tests executed and results

| Command | Result |
|---------|--------|
| `pytest exercise-ai/tests/test_token_usage.py -q` | **10 passed**, exit 0 |
| `pytest exercise-ai -q` | **90 passed**, 2 warnings (pre-existing), exit 0 |
| PLAN extract/rates/README asserts | **OK** |

## Requirement status

| ID | Local evidence | Status |
|----|----------------|--------|
| TOKEN-01 | Per-call `record` append; RELY retag; no replace | **Met** |
| TOKEN-02 | NDJSON day+provider under gitignored `token-usage/` | **Met** |
| TOKEN-03 | `[USAGE]` + summary; mocked tests offline | **Met** |

## Self-Check: Requirements Satisfaction

| Requirement | Status | Evidence |
|-------------|--------|----------|
| TOKEN-01 | SATISFIED | Generators record each LLM call; collector never replaces prior events |
| TOKEN-02 | SATISFIED | Flush appends NDJSON; no secrets in lines; injectable dir for tests |
| TOKEN-03 | SATISFIED | Stderr `[USAGE]`; `test_token_usage.py` mocks only |

## Threat model notes

T-09-01…T-09-06: no prompts/keys in USAGE/NDJSON; short `error_kind`; append-only; usage orthogonal to `--out`; no new PyPI deps.

## Next

1. Phase 8 Provider Failover when ready (`$gsd-discuss-phase 8`).
2. Optional operator spot-check with real keys for live `[USAGE]` + NDJSON line.
