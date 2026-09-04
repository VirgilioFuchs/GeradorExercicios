---
phase: 02-validation-error-handling
verified: 2026-09-04T11:55:00Z
status: passed
score: 6/6 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 2: Validation & Error Handling Verification Report

**Phase Goal:** Validação estrutural/semântica das respostas LLM e tratamento explícito de erros de API/config — apenas JSON válido em stdout; falhas claras em stderr.
**Verified:** 2026-09-04T11:55:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

Merged from ROADMAP Phase 2 success criteria + PLAN `must_haves.truths` (deduplicated).

| # | Truth | Status | Evidence |
| --- | ------- | ---------- | -------------- |
| 1 | Validador rejeita estrutura inválida: non-`ExerciseBatch`, chave/`exercicios` ausente/inválida/vazia, quantidade incorreta, campos só-whitespace — mensagens PT com paths e esperado vs recebido | ✓ VERIFIED | `validator.py` isinstance + list/empty/qty/strip checks; Task 1 automated: non-instance, empty, malformed, `esperado 2`/`recebido 1`, `exercicios[0].resposta`, report modes `all` vs `first_exercise` |
| 2 | Cada falha de validação retorna mensagem específica identificando o problema (VALD-05 / SC2) | ✓ VERIFIED | Distinct PT strings per case; joined with `"; "`; field paths `exercicios[i].campo`; Task 1 asserts per-case messages |
| 3 | Falha de validação: texto PT plano em stderr (`print(str(err))` sem wrappers), log `[VALIDAÇÃO]` + JSON bruto, `sys.exit(1)`, sem retry | ✓ VERIFIED | `validator._log_validation_failure`; `main.py` `print(str(val_err), file=sys.stderr)` + `sys.exit(1)`; Task 2 `run_demo` ValueError → `SystemExit(1)`, stdout vazio, `generate_exercises` call_count==1 |
| 4 | Ausência de chaves de API levanta `ValueError` nomeando `GEMINI_API_KEY` e `LLM_API_KEY` antes de qualquer chamada (ERR-01 / SC3) | ✓ VERIFIED | `_MISSING_KEY_MSG` in `generator.py` / `generator_gemini.py`; `_resolve_provider` + both `get_client`; Task 2 clears env → both names in message |
| 5 | Timeout, rate limit, conexão e auth (OpenAI + Gemini) mapeiam para `RuntimeError` PT distintos; payload vazio/não-parseável → `RuntimeError`; logs `[API:openai]` / `[API:gemini]` (ERR-02–04 / SC4) | ✓ VERIFIED | `map_openai_error` / `map_gemini_error`; Gemini table + `GEMINI_ERROR_CLASSIFICATION:` priority-1 N/A; Task 2 category needles + exact Gemini messages + empty/refusal/parsed-None paths |
| 6 | Em sucesso, stdout é só JSON UTF-8 (`ensure_ascii=False`); `Gerando…` / `Validando…` só em stderr; `run_demo` mock sucesso sem retry | ✓ VERIFIED | Task 2: `json.loads(stdout)` with 3 exercises; stage labels absent from stdout and present on stderr; `gen.call_count == 1` |

**Score:** 6/6 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------ | ------- |
| `exercise-ai/validator.py` | Semantic post-parse validation + `VALIDATION_REPORT_MODE` + two-layer logging | ✓ VERIFIED | Exists; substantive (~67 lines); wired from `main.py`; contains `VALIDATION_REPORT_MODE` |
| `exercise-ai/main.py` | Stage labels stderr, `print(str(err))`, fail-fast exit 1, stdout JSON-only | ✓ VERIFIED | Contains `print(str(val_err)`, `Gerando…`, `Validando…`, `ensure_ascii=False`; no forbidden wrappers |
| `exercise-ai/generator.py` | Dual-key missing message + `map_openai_error` | ✓ VERIFIED | Contains `map_openai_error`, `_MISSING_KEY_MSG`, OpenAI typed catches |
| `exercise-ai/generator_gemini.py` | Gemini classification table + `map_gemini_error` + empty-response RuntimeError | ✓ VERIFIED | Contains `map_gemini_error`, `GEMINI_ERROR_CLASSIFICATION:`, empty/unparseable paths |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `exercise-ai/main.py` | `exercise-ai/validator.py` | `validate_exercise_batch(batch, request)` after generation | ✓ WIRED | Line 39: `validate_exercise_batch(batch, request)` |
| `exercise-ai/main.py` | `exercise-ai/generator.py` | `generate_exercises(request)` before validation | ✓ WIRED | Line 36: `generate_exercises(request)` |
| `exercise-ai/generator.py` | `exercise-ai/generator_gemini.py` | provider dispatch on gemini | ✓ WIRED | Conditional import + `generate_gemini(...)` when provider == gemini |
| `exercise-ai/validator.py` | `exercise-ai/models.py` | `ExerciseBatch` + `GenerationRequest` semantic checks | ✓ WIRED | Imports and type/quantity/field checks against both models |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `main.run_demo` | `batch` | `generate_exercises(request)` | Real provider path (mocked in verify) | ✓ FLOWING |
| `main.run_demo` | `validated_batch` | `validate_exercise_batch(batch, request)` | Same object if valid; raises if invalid | ✓ FLOWING |
| `main.run_demo` | stdout JSON | `validated_batch.model_dump()` | Real dump of validated model | ✓ FLOWING |
| `map_*_error` | user RuntimeError | Exception type/status_code | Mapped PT message (not silenced) | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Validator semantic + report modes + main D-05 source | `python .planning/_verify_02_t1.py` | `Tracer validation path verified` (exit 0) | ✓ PASS |
| API mappers + missing keys + ERR-03 + run_demo contract | `python .planning/_verify_02_t2.py` | `API error mapping and CLI contract verified` (exit 0) | ✓ PASS |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| — | — | No phase-declared `scripts/*/tests/probe-*.sh` | SKIP |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| VALD-01 | 02-01 | Rejeita JSON inválido / estrutura ausente | ✓ SATISFIED | Post-parse: non-`ExerciseBatch` rejected; raw JSON invalid handled at generator parse (ERR-03) per D-01 |
| VALD-02 | 02-01 | Verifica presença/validade de `exercicios` | ✓ SATISFIED | Missing/non-list → `"Chave 'exercicios' ausente ou inválida."`; empty list → vazia |
| VALD-03 | 02-01 | Quantidade igual à solicitada | ✓ SATISFIED | `esperado N … recebido M` message; Task 1 |
| VALD-04 | 02-01 | Campos obrigatórios não vazios (strip) | ✓ SATISFIED | `exercicios[i].{field} está vazio`; whitespace treated empty |
| VALD-05 | 02-01 | Motivo claro por caso | ✓ SATISFIED | Path + expected/actual; report mode collects messages |
| ERR-01 | 02-01 | Erro claro sem API key | ✓ SATISFIED | Names both `GEMINI_API_KEY` and `LLM_API_KEY` + `.env` |
| ERR-02 | 02-01 | Rede, timeout, rate limit | ✓ SATISFIED | OpenAI isinstance map + Gemini status_code table |
| ERR-03 | 02-01 | Resposta vazia / estrutura inválida | ✓ SATISFIED | OpenAI refusal/parsed-None; Gemini empty/unparseable |
| ERR-04 | 02-01 | Erros não silenciados; mensagens úteis | ✓ SATISFIED | Plain stderr user line + `[API:*]`/`[VALIDAÇÃO]` detail; exit 1 |

No orphaned Phase 2 requirements (all VALD-* / ERR-* claimed by 02-01-PLAN).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| — | — | No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK` in phase-modified files | — | — |
| — | — | No retry loops / LangChain / CrewAI / AutoGen in phase code | — | — |
| `exercise-ai/requirements.txt` | — | `pytest` listed (dep only; suite deferred to Phase 3) | ℹ️ Info | Expected per plan deferral |

### Human Verification Required

None — all must-have behaviors exercised by automated spot-checks (mocked providers; no live API required for phase goal).

### Gaps Summary

None. Phase goal achieved: only valid UTF-8 JSON on success stdout; validation and API/config failures emit clear Portuguese diagnostics on stderr with fail-fast exit 1.

---

_Verified: 2026-09-04T11:55:00Z_
_Verifier: Claude (gsd-verifier)_
