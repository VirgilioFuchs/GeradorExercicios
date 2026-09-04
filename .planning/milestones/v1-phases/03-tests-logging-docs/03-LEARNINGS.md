---
phase: "03"
phase_name: "tests-logging-docs"
project: "Gerador de Exercícios com IA"
generated: "2026-09-04T13:15:00.000Z"
counts:
  decisions: 7
  lessons: 4
  patterns: 5
  surprises: 4
missing_artifacts: []
---

# Phase 03 Learnings: tests-logging-docs

## Decisions

### TEST-02 "chave ausente" = validator `exercicios` only (not API env keys)

Absent or invalid `exercicios` on the batch triggers `Chave 'exercicios' ausente`; missing `LLM_API_KEY` / `GEMINI_API_KEY` stays ERR-01 in generator tests.

**Rationale:** Keeps VALD-02 and ERR-01 contracts distinct so the durable suite cannot conflate semantic validation with config errors.
**Source:** 03-CONTEXT.md (D-03), 03-01-PLAN.md, 03-01-SUMMARY.md, .planning/STATE.md

---

### LOG-01 via stdlib logging to stderr (no log files / Phoenix)

Emit start, params (no secrets), success, and failure/validation reason through `logging` (or a thin helper) on stderr; keep existing `[VALIDAÇÃO]` / `[API:*]` layers and JSON-only success stdout.

**Rationale:** Meets LOG-01 without introducing persistent observability stack deferred from Phase 2.
**Source:** 03-CONTEXT.md (D-05, D-07), 03-01-PLAN.md, 03-01-SUMMARY.md

---

### LOG-02: `[API:*]` logs type + status/code only

Mapper detail lines must use exception type plus `status_code`/`code` when present — never raw `str(exc)` — and never log `LLM_API_KEY` / `GEMINI_API_KEY` values. OpenAI generic fallback user message is fixed PT without embedding `exc` (WR-02).

**Rationale:** Closes WR-01 leakage surface; security baseline for the project (costly reversibility).
**Source:** 03-CONTEXT.md (D-06), 03-01-PLAN.md, 03-01-SUMMARY.md, .planning/STATE.md

---

### Suite layout: `exercise-ai/tests/` + Pydantic factories

Tests live under `exercise-ai/tests/` with `conftest.py` path grounding; prefer in-code Pydantic factories over JSON fixtures; canonical command `pytest exercise-ai -q` from repo root.

**Rationale:** Aligns imports with Phase 2 verifies, keeps fixtures typed and offline (TEST-01), and documents one runnable command (D-04).
**Source:** 03-CONTEXT.md (D-01, D-02, D-04), 03-01-PLAN.md

---

### Durable coverage includes EVAL remediations (D-03)

Minimum suite = full TEST-02 validator cases plus mocked OpenAI/Gemini mappers, `run_demo` stdout purity, and anti-leakage of API keys in stderr — no live LLM.

**Rationale:** Phase 2 verifies were ephemeral; EVAL-REVIEW must-fix items become the MVP regression baseline.
**Source:** 03-CONTEXT.md (D-03), 03-01-PLAN.md, 03-01-SUMMARY.md

---

### Root README in Portuguese; no CI this phase

Create root `README.md` covering setup, env vars, run, pytest, and stdout vs stderr. Do not add GitHub Actions — document pytest only.

**Rationale:** SCAF-04 onboarding without expanding into CI/Phoenix deferred work (D-10).
**Source:** 03-CONTEXT.md (D-08, D-09, D-10), 03-01-SUMMARY.md

---

### Assert LOG-01 via redirected stderr (dynamic stream handler)

LOG-01 pytest asserts capture redirected stderr rather than relying on empty `caplog` when `propagate=False`.

**Rationale:** Suite must fail if LOG-01 wiring is missing; static `StreamHandler(sys.stderr)` bound at init breaks under `redirect_stderr`.
**Source:** 03-01-SUMMARY.md (key-decisions, Deviations)

---

## Lessons

### `logging.StreamHandler(sys.stderr)` freezes the stream object at init

Under `redirect_stderr` / `caplog`, LOG-01 events were invisible because the handler held the original stderr and `propagate=False` left `caplog` empty.

**Context:** Found during Task 2 while asserting LOG-01; fixed with `_StderrStream` that always writes to current `sys.stderr`, and tests assert via redirected stderr.
**Source:** 03-01-SUMMARY.md (Deviations — Auto-fixed Issues)

---

### Redaction must cover refusal/unparseable debug dumps, not only mapper `[API:*]` lines

Gemini unparseable and OpenAI refusal paths could still echo env key values when dumping response/refusal text.

**Context:** Threat T-03-01 / D-06 during Task 2; fixed with `_redact_env_secrets` before those dumps in both generators.
**Source:** 03-01-SUMMARY.md (Deviations)

---

### Promote Phase 2 ephemeral verifies into named pytest modules early

Phase 2 Task 1/2 verify scripts were the blueprint; committing them as `test_validator.py`, `test_generators.py`, `test_main.py`, and `test_logging_security.py` closed EVAL durable-suite gaps.

**Context:** CONTEXT and PLAN treated EVAL must-fix as in-scope for Phase 3, not backlog.
**Source:** 03-CONTEXT.md, 03-01-PLAN.md, 03-01-SUMMARY.md

---

### Intentional malformed fixtures can emit Pydantic serialization warnings

`test_chave_exercicios_invalida_nao_lista` triggers `PydanticSerializationUnexpectedValue`; suite still passes.

**Context:** Verification noted the warning as informational, not a failure — expected when forcing non-list `exercicios`.
**Source:** 03-VERIFICATION.md (Anti-Patterns Found)

---

## Patterns

### Durable suite promotes Phase 2 ephemeral verifies

Lift one-off `python -c` / verify asserts into pytest modules under `exercise-ai/tests/` with the same path grounding.

**When to use:** Closing a phase that relied on manual or script verifies; building an MVP regression baseline without live network.
**Source:** 03-01-SUMMARY.md (patterns-established), 03-01-PLAN.md (proven_verify_commands)

---

### Security tests inject distinctive dummy keys and assert absence in stderr

Set unique dummy `LLM_API_KEY` / `GEMINI_API_KEY` values, force mapper auth/failure (and related dumps), capture stderr, assert substrings never appear.

**When to use:** LOG-02 / secret-leakage evals; any path that might interpolate exception or response bodies.
**Source:** 03-01-SUMMARY.md (patterns-established), 03-VERIFICATION.md

---

### Pytest factories in `conftest` + `sys.path` to `exercise-ai/`

Build `GenerationRequest` / `Exercise` / `ExerciseBatch` in code; insert package dir on `sys.path` so imports match the CLI layout.

**When to use:** Flat `exercise-ai/` package without installable packaging; offline validator and mapper unit tests.
**Source:** 03-01-SUMMARY.md (tech-stack.patterns), 03-CONTEXT.md (D-01, D-02)

---

### `[API:*]` detail = type + status only; never raw `str(exc)`

Helpers like `_openai_error_detail` / `_gemini_error_detail` format `type(exc).__name__` plus status/code fields.

**When to use:** Provider error mappers where SDK exception bodies may embed credentials or tokens.
**Source:** 03-01-SUMMARY.md (tech-stack.patterns), 03-01-PLAN.md (threat_model T-03-01)

---

### LOG-01 via stdlib logging with dynamic stderr stream

Bind a StreamHandler to a wrapper that always resolves `sys.stderr` at write time so redirects and pytest capture work.

**When to use:** CLI apps that need assertable stderr events under test without `caplog` propagation.
**Source:** 03-01-SUMMARY.md (tech-stack.patterns, Deviations)

---

## Surprises

### LOG-01 invisible under `redirect_stderr` despite “logging to stderr”

Expected stdlib logging to stderr to show up under pytest redirects; handler had already captured the original stream object.

**Impact:** Required `_StderrStream` fix and shifted LOG-01 asserts to redirected stderr capture; without it the suite could pass with missing events if asserts were weak.
**Source:** 03-01-SUMMARY.md (Deviations)

---

### Leakage surface beyond mapper `str(exc)` (refusal / unparseable dumps)

Plan focused WR-01 on `[API:*]` lines; Task 2 also found key echo in debug dumps of refusal/unparseable responses.

**Impact:** Extra `_redact_env_secrets` path in both generators; anti-leakage tests cover those failure paths.
**Source:** 03-01-SUMMARY.md (Deviations), 03-01-PLAN.md (threat_model)

---

### Token actuals far below estimate

Plan estimate was 48k tokens (confidence low); summary actuals recorded 8718 tokens for 3 tasks / 4 commits.

**Impact:** Phase finished under token budget; duration reported ~15–25 min — useful calibration sample once more phases have estimate+actual pairs.
**Source:** 03-01-PLAN.md (estimate), 03-01-SUMMARY.md (actuals, Performance)

---

### ROADMAP Phase 3 goal not user-story formatted despite `Mode: mvp`

Verifier mapped coverage from the PLAN objective story because ROADMAP goal text lacked «As a…, I want to…, so that…».

**Impact:** Informational only — verification still scored 7/7; future ROADMAP entries should match MVP mode formatting.
**Source:** 03-VERIFICATION.md (Anti-Patterns Found, User Flow Coverage)
