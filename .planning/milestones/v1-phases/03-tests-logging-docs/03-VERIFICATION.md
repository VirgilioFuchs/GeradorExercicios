---
phase: 03-tests-logging-docs
verified: 2026-09-04T12:56:00Z
status: passed
score: 7/7 must-haves verified
behavior_unverified: 0
overrides_applied: 0
verdict: PASS
pytest: "31 passed, 2 warnings in 2.00s (exit 0)"
---

# Phase 3: Tests, Logging & Docs Verification Report

**Phase Goal:** Cobertura de testes do validador, observabilidade básica e documentação de uso  
**Verified:** 2026-09-04T12:56:00Z  
**Status:** passed  
**Verdict:** PASS  
**Re-verification:** No — initial verification

## User Flow Coverage

User story (from `03-01-PLAN.md` objective; ROADMAP goal text is not user-story formatted despite `Mode: mvp`):

«As a developer maintaining the exercise generator, I want to run durable pytest coverage, safe development logs, and follow a root README, so that I can verify quality and onboard without leaking secrets or calling live LLMs.»

| Step | Expected | Evidence | Status |
|------|----------|----------|--------|
| Run tests | `pytest exercise-ai -q` green, no live LLM | Verifier ran suite: 31 passed; mocks/factories only in `tests/` | ✓ |
| Safe logs | Start/params/success/fail on stderr; keys never leaked | `main.py` LOG-01 + `test_main.py` / `test_logging_security.py` | ✓ |
| Follow README | Setup, env, run, pytest, stdout/stderr in PT | Root `README.md` sections + keyword check | ✓ |
| Outcome | Quality verifiable and onboarding without secret leak / live LLM | Suite + redaction + README all verified below | ✓ |

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | ------- | ---------- | -------------- |
| 1 | From repo root, `pytest exercise-ai -q` passes with no live LLM network calls | ✓ VERIFIED | Verifier ran: `31 passed, 2 warnings in 2.00s`, exit 0. Tests use factories/mocks only (no live OpenAI/Gemini calls in suite). |
| 2 | Validator suite covers valid, invalid structure, absent/invalid `exercicios` (TEST-02 chave ausente), empty list, wrong quantity, whitespace paths | ✓ VERIFIED | `test_validator.py`: `test_chave_exercicios_ausente_via_missing_attr` and `test_chave_exercicios_invalida_nao_lista` assert `Chave 'exercicios' ausente`; plus valid, non-batch, empty, esperado/recebido, whitespace path. |
| 3 | Parameterized mapper tests cover OpenAI four categories and Gemini status table with mocks; missing API env keys as ERR-01 | ✓ VERIFIED | `test_generators.py` — ERR-01 missing keys explicitly documented as not TEST-02; OpenAI/Gemini mapper cases with `[API:*]` asserts; mocks only. |
| 4 | `run_demo` with mocked generate: success stdout parseable JSON only; ValueError → SystemExit(1) plain stderr | ✓ VERIFIED | `test_main.py::test_run_demo_success_stdout_json_only`, `test_run_demo_value_error_exits_one_plain_stderr`. |
| 5 | LOG-01 events: start, params without secrets, success/failure, validation reason — asserted by pytest | ✓ VERIFIED | `main.py` emits via stdlib logging; `test_main.py` asserts `Início da geração`, `materia=`/`topico=`/`quantidade=`, no `LLM_API_KEY=`/`GEMINI_API_KEY=`, success and failure/validation reason. |
| 6 | LOG-02: dummy keys never in stderr; `[API:*]` logs type + status/code only (no raw `str(exc)`) | ✓ VERIFIED | `_openai_error_detail` / `_gemini_error_detail` use `type(exc).__name__` + status; `test_logging_security.py` forces key-in-exception bodies and asserts dummy keys absent from stderr. |
| 7 | Root README.md documents setup, env vars, run, pytest, stdout JSON vs stderr in Portuguese | ✓ VERIFIED | `README.md` has Setup, Variáveis de ambiente (`LLM_API_KEY`, `GEMINI_API_KEY`, `LLM_PROVIDER`), `python exercise-ai/main.py`, `pytest exercise-ai -q`, Stdout vs stderr. Keyword check: all required tokens present. |

**Score:** 7/7 truths verified (0 present, behavior-unverified)

### Roadmap Success Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | `pytest` passa com casos: JSON válido, inválido, chave ausente, campo faltando, quantidade errada, lista vazia | ✓ | Full suite green; `test_validator.py` covers all listed cases; chave ausente = `exercicios` |
| 2 | Testes não fazem chamadas reais ao LLM | ✓ | Mocks/static factories; no network client construction in happy-path tests |
| 3 | Logs registram início, parâmetros (sem segredos), sucesso/falha e motivo de validação | ✓ | `main.py` + pytest asserts |
| 4 | `README.md` documenta setup, variáveis de ambiente e como executar | ✓ | Root README PT sections |

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------ | ------- |
| `exercise-ai/tests/conftest.py` | sys.path + Pydantic factories | ✓ VERIFIED | Inserts `exercise-ai/` on path; `make_request` / `make_exercise` / `make_batch` |
| `exercise-ai/tests/test_validator.py` | TEST-02 durable cases | ✓ VERIFIED | Includes chave `exercicios` ausente |
| `exercise-ai/tests/test_generators.py` | Mocked mappers + ERR-01 | ✓ VERIFIED | Wired to `map_openai_error` / `map_gemini_error` |
| `exercise-ai/tests/test_main.py` | stdout purity + LOG-01 | ✓ VERIFIED | Calls `run_demo` under mocks |
| `exercise-ai/tests/test_logging_security.py` | Anti-leakage | ✓ VERIFIED | Dummy `LLM_API_KEY` / `GEMINI_API_KEY` substrings |
| `exercise-ai/main.py` | LOG-01 logging | ✓ VERIFIED | `logging` → stderr; no log files |
| `exercise-ai/generator.py` | Sanitized `[API:openai]` | ✓ VERIFIED | type + status only |
| `exercise-ai/generator_gemini.py` | Sanitized `[API:gemini]` | ✓ VERIFIED | type + status only |
| `README.md` | PT setup/run/pytest | ✓ VERIFIED | Root file |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `tests/conftest.py` | `models.py` | factories build ExerciseBatch | ✓ WIRED | Imports `ExerciseBatch` / `GenerationRequest` |
| `tests/test_validator.py` | `validator.py` | `validate_exercise_batch` | ✓ WIRED | Direct calls under pytest |
| `main.py` | `logging` | LOG-01 around generate/validate | ✓ WIRED | `logger.info` / `logger.error` |
| `generator.py` | stderr `[API:openai]` | redacted detail | ✓ WIRED | `print(f"[API:openai] {_openai_error_detail(exc)}", …)` |
| `README.md` | `requirements.txt` | pip install path | ✓ WIRED | `pip install -r exercise-ai/requirements.txt` |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `test_*` fixtures | Pydantic models | In-code factories | Yes (static, intentional) | ✓ FLOWING |
| `run_demo` tests | stdout JSON | Mocked `generate_exercises` → `model_dump` | Yes under mock | ✓ FLOWING |
| `[API:*]` stderr | detail string | `_openai_error_detail` / `_gemini_error_detail` | Type/status only | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Full suite (canonical D-04) | `pytest exercise-ai -q` | 31 passed, exit 0 | ✓ PASS |
| TEST-02 chave ausente | Inspect + suite includes `test_chave_exercicios_*` | Asserts `Chave 'exercicios' ausente` | ✓ PASS |
| LOG-02 anti-leak | Suite includes `test_logging_security.py` | Dummy keys absent from stderr | ✓ PASS |
| README keywords | `python -c` keyword assert | missing=[] | ✓ PASS |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| — | — | No phase-declared probes | SKIPPED |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| TEST-01 | 03-01 | Unit tests without live LLM | ✓ SATISFIED | pytest suite mocks/static only |
| TEST-02 | 03-01 | valid/invalid/chave ausente/missing field/wrong qty/empty | ✓ SATISFIED | `test_validator.py` — chave = `exercicios`, not API env keys |
| LOG-01 | 03-01 | Start, params, success/fail, validation reason | ✓ SATISFIED | `main.py` + `test_main.py` asserts |
| LOG-02 | 03-01 | API keys never in logs | ✓ SATISFIED | Redaction helpers + `test_logging_security.py` |
| SCAF-04 | 03-01 | README setup + run | ✓ SATISFIED | Root `README.md` PT |

No orphaned Phase 3 requirements found.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| — | — | No TBD/FIXME/XXX in phase artifacts | — | — |
| pytest warning | — | PydanticSerializationUnexpectedValue in `test_chave_exercicios_invalida_nao_lista` | ℹ️ Info | Intentional malformed fixture; does not fail suite |
| pytest warning | — | google.genai `_UnionGenericAlias` DeprecationWarning | ℹ️ Info | Third-party; unrelated to phase goal |
| ROADMAP | Phase 3 | `Mode: mvp` but goal not «As a…, I want to…, so that…» | ℹ️ Info | PLAN objective has user story; coverage mapped from PLAN |

### Deferred / Non-goals Confirmed Absent

- No `.github/workflows` (D-10)
- No Phoenix / persistent log files (D-07)
- No RELY retry, argparse, MATH-01 added this phase

### Human Verification Required

None — all must-haves are programmatically verified.

### Gaps Summary

None. Phase goal achieved in the codebase.

---

_Verified: 2026-09-04T12:56:00Z_  
_Verifier: Claude (gsd-verifier)_  
_Commit: left to orchestrator (docs(03): verification report)_
