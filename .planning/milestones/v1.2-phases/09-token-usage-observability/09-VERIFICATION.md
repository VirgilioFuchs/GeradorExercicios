# Phase 9 Verification — Token Usage Observability

**Phase:** 09-token-usage-observability  
**Plan:** 09-01  
**Verified:** 2026-09-15  
**Verifier:** gsd-verifier (generic-agent)

## Status

**passed**

## Score

**7/7** must_have truths · **4/4** artifacts · **4/4** key_links · prohibitions clean · ROADMAP success criteria 1–5 met

## Automated evidence

| Command | Result |
|---------|--------|
| `pytest exercise-ai -q` | **90 passed**, 2 warnings (pre-existing: google.genai deprecation; pydantic serializer in validator test), exit 0 (~3.0s) |

No live LLM; no committed usage NDJSON required.

## Must-have truths

| # | Truth | Result | Evidence |
|---|-------|--------|----------|
| 1 | Each LLM round-trip records usage; no replace of prior in-memory events (D-10/11/13; TOKEN-01) | **PASS** | `collector.record` appends only; OpenAI/Grok via `generator._record_*` + `extract_openai_usage`/`extract_grok_usage`; Gemini via `_record_gemini_usage` + `extract_gemini_usage`; RELY retags via `retag_last` without dropping events |
| 2 | Missing token/USD → PT `indisponível`, never fabricated `0` (D-09) | **PASS** | `rates.INDISPONIVEL = "indisponível"`; `_token_or_indisponivel(None)` → sentinel; tests `test_extract_openai_usage_and_missing_indisponivel`, `test_missing_usage_never_fabricates_zero`, `test_rate_table_unknown_model_indisponivel` |
| 3 | End-of-run flush NDJSON append under `token-usage/{YYYY-MM-DD}/{provider}.ndjson`; local civil date; no overwrite (D-01…D-04; TOKEN-02) | **PASS** | `TokenUsageCollector.flush` opens `"a"`, day via `datetime.now().astimezone().date().isoformat()`; `flush_token_usage()` **only** in `main.run` `finally`; buffer cleared after flush (idempotent); `test_record_flush_ndjson_append_and_idempotent`, `test_main_run_flush_in_finally` |
| 4 | Stderr `[USAGE]` + end-of-run summary by provider (D-07/08/18; TOKEN-03) | **PASS** | `_print_usage_line` / `_print_run_summary`; fields `in`/`out`/`total`/`duration_ms`/`usd`; summary sums numeric USD only + `eventos_sem_preco`; `test_end_of_run_summary_numeric_vs_indisponivel` |
| 5 | Events carry `success`\|`error`\|`attempt` covering RELY / API errors / successes (D-12) | **PASS** | Generators record `success`/`error`; Gemini model-fallback intermediate calls use `attempt`; `reliability.generate_validated_batch` retags to `attempt` on retriable invalid/validation and `error` on final validation failure; `test_rely_attempt_status_retag` |
| 6 | Grok ticks → `usd_source=api`; OpenAI/Gemini rate table; unknown model → USD `indisponível` (D-14/15/17) | **PASS** | `extract_grok_usage` prefers `cost_in_usd_ticks/1e10`; `estimate_usd_from_rates` for OpenAI/Gemini; unknown → `(INDISPONIVEL, "indisponivel")`; tests for ticks + unknown model |
| 7 | Mocked tests + injectable `TOKEN_USAGE_DIR`; no live LLM / no committed usage files (D-19/20) | **PASS** | `test_token_usage.py` (10 tests) monkeypatches `TOKEN_USAGE_DIR`; mocks `usage` / `usage_metadata` / ticks; `.gitignore` ignores `exercise-ai/token-usage/**` keeps `.gitkeep` |

## Artifacts

| Artifact | Result | Notes |
|----------|--------|-------|
| `exercise-ai/token_usage/` | **PASS** | `__init__.py`, `collector.py`, `extract.py`, `rates.py`; exports `TokenUsageCollector`, `begin_run`, `flush_token_usage`, extractors |
| `exercise-ai/token-usage/.gitkeep` | **PASS** | Present; generated `*.ndjson` gitignored |
| `exercise-ai/tests/test_token_usage.py` | **PASS** | Contains `indisponível`; covers extract, flush/append, redaction, RELY, summary, main finally |
| `.gitignore` | **PASS** | `exercise-ai/token-usage/**` + `!exercise-ai/token-usage/.gitkeep` |

## Key links

| Link | Result | Notes |
|------|--------|-------|
| generators → extract + `record` | **PASS** | `generator.py`, `generator_gemini.py` measure `duration_ms` and record per API call |
| reliability → status retag | **PASS** | `retag_last("attempt"|"error")` without a second retry loop |
| `main.run` finally → flush | **PASS** | Single production call site; no flush before `sys.exit` |
| `TOKEN_USAGE_DIR` injectable | **PASS** | Module-level Path; tests override under `tmp_path` |

## Prohibitions (spot-check)

| Prohibition | Result |
|-------------|--------|
| No Phase 8 failover / second RELY-math loop | **PASS** — usage only observes; no failover code |
| No Admin billing APIs / pricing scrape / FX | **PASS** — local rate table only |
| No Phoenix / DB / agent frameworks | **PASS** |
| No secrets / raw prompts in `[USAGE]` or NDJSON | **PASS** — stderr prints metadata fields only; `test_usage_stderr_redacts_secrets_spirit` asserts no `sk-secret` / prompt body |
| No usage fields in `--out` exercise JSON | **PASS** — `test_main_run_flush_in_finally` asserts `prompt_tokens` absent from dumped JSON |
| No pricing/flush in validator / math_check | **PASS** — no `token_usage` refs in `validator.py` |
| No live LLM in pytest | **PASS** — suite green offline |

## ROADMAP success criteria

| # | Criterion | Result |
|---|-----------|--------|
| 1 | Per-call quantitative tokens; no erase prior same-run records | **PASS** |
| 2 | End-of-run history in dedicated folder (ROADMAP `.json` → locked NDJSON per D-01/plan) | **PASS** |
| 3 | Stderr usage lines without API keys | **PASS** |
| 4 | OpenAI, Gemini, Grok same schema; missing = explicit (indisponível) | **PASS** |
| 5 | Mocked extract/append/flush tests; CI offline | **PASS** |

## Gaps

None blocking. Optional operator live-key spot-check (noted in SUMMARY) remains out of automated verification scope.

## Verdict

Phase 9 delivers TOKEN-01/02/03 against plan must_haves, CONTEXT D-01…D-20, and ROADMAP criteria. Full suite green offline.
