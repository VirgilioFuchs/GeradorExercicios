# EVAL-REVIEW — Phase 2: validation-error-handling

**Audit Date:** 2026-09-04
**AI-SPEC Present:** Yes
**Overall Score:** 16/100
**Verdict:** NOT IMPLEMENTED

## Dimension Coverage

| Dimension | Status | Measurement | Finding |
|-----------|--------|-------------|---------|
| Schema / key presence | PARTIAL | Code | Product guardrail in `validator.py` (isinstance / `exercicios` list checks). Ephemeral Task 1 `python -c` / claimed `.planning/_verify_02_t1.py` exercised cases, but **no durable pytest module or fixture file** remains in repo. AI-SPEC dataset (valid + missing/empty `exercicios`) not materialized. |
| Exact quantity | PARTIAL | Code | Quantity check implemented (`esperado N` / `recebido M`). Spot-checked once in plan verify; not retained as runnable suite against a reference batch set. |
| Non-empty fields (trim) | PARTIAL | Code | Strip-empty paths implemented for enunciado/resposta/explicacao. Dataset spec asked whitespace-only on **each** field plus multi-error cases; only a single `exercicios[0].resposta` whitespace case appears in documented verify — incomplete rubric coverage, not durable. |
| Error path specificity | PARTIAL | Code + Human | Path/`esperado`/`recebido` strings asserted in ephemeral verify. No recorded human spot-check of stderr UX wording (AI-SPEC High: Code + Human). |
| Missing API key UX | PARTIAL | Code | Dual-key `ValueError` implemented and message-substring checked in Task 2 verify. Durable suite absent; full UX rubric (exit 1, no traceback-as-primary) not locked in a committed CLI-level test. |
| API error typing | PARTIAL | Code | `map_openai_error` / `map_gemini_error` exist and were mocked in Task 2. SUMMARY notes OpenAI exception harness flakiness; verify harness **not committed**. No pytest parameterized cases for timeout/rate/network/auth. |
| Stdout purity | PARTIAL | Code | `run_demo` success/failure stdout contract verified ephemerally with mocks. No durable regression test; live dual-provider UAT capture (AI-SPEC §7) not evidenced as eval artifact. |
| No secret leakage | MISSING | Code + Human | **No eval asserts API key values never appear in stderr/logs.** Comments claim “never API keys,” but `[API:*]` logs `str(exc)` and Gemini may dump `response.text` with no redaction/secret-scan test. Critical rubric unmet. |

**Coverage Score:** 0/8 (0%)

## Infrastructure Audit

| Component | Status | Finding |
|-----------|--------|---------|
| Eval tooling (pytest) | Configured / Not found | `pytest>=8.0.0` listed in `exercise-ai/requirements.txt` but **zero** `test_*.py` / `conftest.py` / pytest invocations in tree. Primary tool from AI-SPEC never called. Plan verifies were one-shot `python -c`; `_verify_02_t*.py` referenced in VERIFICATION.md **absent** from `.planning/`. |
| Reference dataset | Missing | Planned 12–15 static JSON/Pydantic fixtures (valid, wrong count, empty/missing, per-field whitespace, multi-error, API mocks). **No** `*.jsonl`, fixture package, or eval dataset file found. |
| CI/CD integration | Missing | No `.github/workflows`, Makefile eval target, or `pytest exercise-ai -q` automation. AI-SPEC deferred suite to Phase 3 — gap remains against evaluation plan. |
| Online guardrails | Implemented | All four online guardrails wired on request path: `validate_exercise_batch` before stdout; missing-key `ValueError` before client init; `map_openai_error` / `map_gemini_error`; stage labels + errors on stderr only. |
| Tracing (stderr two-layer) | Configured | Phoenix correctly deferred. `[VALIDAÇÃO]` + raw JSON and `[API:openai|gemini]` detail logs exist on failure paths. Structured tracking of AI-SPEC §7 metrics (reason codes, exit distribution, provider) not implemented — free-text stderr only. |

**Infrastructure Score:** 40/100

## Critical Gaps

1. **No secret leakage (MISSING / Critical)** — No automated or documented eval proving logs never contain API key values; logging surfaces (`str(exc)`, raw response text) untested for leakage.

## Remediation Plan

### Must fix before production:

1. **Secret-leakage eval (BLOCKER):** Add pytest cases that set dummy keys, force failure paths (auth mapper, refusal, Gemini unparseable), capture stderr, and assert key substrings never appear. Add redaction if any path can echo secrets.
2. **Materialize reference dataset:** Commit 12–15 fixtures matching AI-SPEC composition (valid batch, too few/many, empty/malformed `exercicios`, whitespace per field, multi-error for `all`/`first_exercise`, missing-key + mocked API error cases).
3. **Durable pytest suite for Critical dimensions:** Convert PLAN Task 1/2 asserts into `exercise-ai/tests/` covering schema, quantity, non-empty fields, missing-key UX (exit 1 + plain stderr), stdout purity (`json.loads` on stdout only).

### Should fix soon:

1. **API error typing:** Parameterized tests for OpenAI four categories + Gemini status-code table (exact PT messages); keep harness SDK-tolerant (SUMMARY deviation).
2. **Error path specificity:** Assert path format `exercicios[i].campo` and expected/actual; optional short human review checklist for stderr wording in UAT.
3. **CI:** Add workflow/job running `pytest exercise-ai -q` once suite exists (aligns with AI-SPEC CI target).
4. **Retain verify assets:** Stop discarding `_verify_*.py` harnesses — promote into tests or `scripts/eval/`.

### Nice to have:

1. Structured reason-code prefixes for validation/API failures to support offline failure-rate review (LOG-* / Phase 3).
2. Reconsider Phoenix/Langfuse only if Phase 3 LOG-* requires hosted telemetry (out of Phase 2 scope).

## Files Found

| Path | Role |
|------|------|
| `exercise-ai/validator.py` | Online semantic guardrail + `[VALIDAÇÃO]` stderr |
| `exercise-ai/main.py` | Stdout isolation, fail-fast exit 1, stage labels |
| `exercise-ai/generator.py` | Missing-key check, `map_openai_error`, `[API:openai]` |
| `exercise-ai/generator_gemini.py` | `map_gemini_error`, `[API:gemini]`, empty/unparseable |
| `exercise-ai/requirements.txt` | Lists `pytest` (unused) |
| `.planning/phases/02-validation-error-handling/02-AI-SPEC.md` | Planned eval strategy (intent only) |
| `.planning/phases/02-validation-error-handling/02-01-PLAN.md` | Embedded ephemeral verify scripts (not durable suite) |
| `.planning/phases/02-validation-error-handling/02-VERIFICATION.md` | Claims `_verify_02_t1.py` / `_verify_02_t2.py` — **files not in repo** |
| `.planning/phases/02-validation-error-handling/02-UAT.md` | Human confirmation of deliverables; not rubric eval suite |

**Not found:** `test_*.py`, `eval_*`, `*.jsonl`, `promptfoo.yaml`, `.github/workflows/*`, langfuse/phoenix/braintrust/ragas usage, committed verify harnesses.
