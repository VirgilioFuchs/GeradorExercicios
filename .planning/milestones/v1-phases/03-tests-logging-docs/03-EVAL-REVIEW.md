# EVAL-REVIEW — Phase 3: tests-logging-docs

**Audit Date:** 2026-09-04
**AI-SPEC Present:** No
**Overall Score:** 61.5/100
**Verdict:** NEEDS WORK

> State B audit: no phase AI-SPEC. Scored against Phase 2 EVAL-REVIEW dimensions/remediations (what Phase 3 was locked to close via D-03/D-06) plus general AI-eval infrastructure practices from `ai-evals.md`.

## Dimension Coverage

| Dimension | Status | Measurement | Finding |
|-----------|--------|-------------|---------|
| Schema / key presence | COVERED | Code | Durable `test_validator.py`: non-`ExerciseBatch`, missing `exercicios` attr, non-list `exercicios` → `Chave 'exercicios' ausente`; `[VALIDAÇÃO]` on stderr only. Phase 2 ephemeral verifies promoted. |
| Exact quantity | COVERED | Code | `test_wrong_quantity_esperado_recebido` asserts `esperado 2` / `recebido 1` + stderr dump. |
| Non-empty fields (trim) | PARTIAL | Code | Whitespace path asserted for `exercicios[0].resposta`; multi-error covers `enunciado`. **No dedicated whitespace case for `explicacao`.** Phase 2 dataset asked per-field coverage. |
| Error path specificity | COVERED | Code | Path form `exercicios[i].campo` + `VALIDATION_REPORT_MODE` `all` vs `first_exercise` in pytest. Human UX wording checklist still absent (optional). |
| Missing API key UX | PARTIAL | Code | ERR-01 message naming both keys tested via `_resolve_provider()`. **No `run_demo` end-to-end** asserting SystemExit(1) + empty stdout + plain stderr for absent keys. |
| API error typing | COVERED | Code | Parameterized OpenAI timeout/rate/connection/auth + Gemini status-code table with exact PT messages and `[API:*]` presence; SDK-tolerant harness committed. |
| Stdout purity | COVERED | Code | `test_run_demo_success_stdout_json_only` / fail-fast ValueError → exit 1, empty stdout, plain stderr. Stage labels on stderr only. |
| No secret leakage | PARTIAL | Code | Redaction shipped (`_openai_error_detail` / `_gemini_error_detail` type+status; `_redact_env_secrets` on dumps). Anti-leak tests cover mapper auth + Gemini unparseable + run_demo failure. **OpenAI refusal path with key-in-refusal text not asserted** (Phase 2 must-fix listed refusal). |

**Coverage Score:** 5/8 (62.5%)

### Phase 2 remediation closure

| Phase 2 must-fix / should-fix | Status after Phase 3 |
|----------------------------------|----------------------|
| Secret-leakage eval (BLOCKER) | Mostly closed — redaction + suite; refusal path gap → PARTIAL |
| Materialize reference dataset (12–15 fixtures) | Partial — Pydantic factories in `conftest.py` (D-02) cover composition; no `*.jsonl` / fixture package |
| Durable pytest suite | Closed — 31 tests under `exercise-ai/tests/` |
| API error typing parameterized | Closed |
| Error path specificity | Closed (code) |
| CI workflow | Explicitly deferred (D-10) — still Missing |
| Retain verify harnesses | Closed — promoted into pytest modules |

## Infrastructure Audit

| Component | Status | Finding |
|-----------|--------|---------|
| Eval tooling (pytest) | ok | `pytest>=8.0` in requirements; suite invoked (`pytest exercise-ai -q` — 31 passed per VERIFICATION). No Promptfoo/Braintrust/RAGAS (appropriate for structured-extraction MVP). |
| Reference dataset | partial | In-code factories cover valid, wrong qty, empty/missing `exercicios`, whitespace (partial fields), multi-error modes, missing-key, mocked API errors. No committed JSONL/static fixture set matching Phase 2 “12–15” artifact. |
| CI/CD integration | missing | No `.github/workflows`, Makefile target, or automated gate. Deferred by D-10; README documents manual `pytest exercise-ai -q` only. |
| Online guardrails | ok | Request-path guardrails still live: `validate_exercise_batch` before stdout; missing-key before client; typed mappers; stderr stage / `[VALIDAÇÃO]` / `[API:*]`. |
| Tracing (stderr + LOG-01) | partial | Phoenix/Langfuse correctly deferred (D-07). LOG-01 start/params/success/failure on stderr with pytest asserts. Still free-text — no structured reason codes / metric flywheel. |

**Infrastructure Score:** 60/100

## Critical Gaps

None — no dimension remains **MISSING**. Phase 2 secret-leakage BLOCKER was reduced to PARTIAL (WARNING) by durable anti-leak tests + redaction; residual gap is quantified (OpenAI refusal path untested).

## Remediation Plan

### Must fix before production:

_(No MISSING/BLOCKER dimensions remaining.)_

### Should fix soon:

1. **Secret-leakage refusal path:** In `test_logging_security.py`, mock OpenAI completion with `refusal` containing `DUMMY_LLM_KEY`; assert key absent from stderr and from raised `RuntimeError` (redaction already in `generator.py`).
2. **Per-field whitespace:** Add pytest cases for whitespace-only `enunciado` and `explicacao` (mirror `test_whitespace_field_path_message`).
3. **Missing-key CLI UX:** Drive `run_demo` with both API env keys cleared (mock or real resolve path) and assert `SystemExit(1)`, empty stdout, plain PT stderr naming both keys.
4. **CI:** Add GitHub Actions (or equivalent) running `pytest exercise-ai -q` — closes Phase 2 should-fix and general eval lifecycle practice (deferred intentionally in Phase 3).

### Nice to have:

1. Commit a small static fixture set (`tests/fixtures/*.json` or `.jsonl`, 10–15 cases) for eval reproducibility beyond factories.
2. Structured reason-code prefixes on validation/API failures for offline failure-rate review.
3. **Factual / math correctness (MATH-01):** Product-level eval gap for an exercise generator — out of Phase 3 scope; required before trusting live LLM outputs as pedagogically correct.
4. Phoenix/Langfuse only if future LOG-* requires hosted telemetry.

## Files Found

| Path | Role |
|------|------|
| `exercise-ai/tests/conftest.py` | Path grounding + Pydantic factories (dataset substitute) |
| `exercise-ai/tests/test_validator.py` | Schema, quantity, whitespace, report-mode evals |
| `exercise-ai/tests/test_generators.py` | ERR-01, OpenAI/Gemini mapper typing, refusal/empty/unparseable |
| `exercise-ai/tests/test_main.py` | Stdout purity, fail-fast, LOG-01 events |
| `exercise-ai/tests/test_logging_security.py` | Anti-leakage (mapper + Gemini unparseable + run_demo) |
| `exercise-ai/main.py` | LOG-01 stderr events |
| `exercise-ai/generator.py` | Sanitized `[API:openai]`, `_redact_env_secrets` |
| `exercise-ai/generator_gemini.py` | Sanitized `[API:gemini]`, `_redact_env_secrets` |
| `README.md` | Setup / pytest / stdout vs stderr docs |
| `.planning/phases/02-validation-error-handling/02-EVAL-REVIEW.md` | Prior gaps Phase 3 targeted |

**Not found:** phase `03-AI-SPEC.md`, `*.jsonl` eval datasets, `promptfoo.yaml`, `.github/workflows/*`, langfuse/phoenix/braintrust/ragas usage.
