---
phase: 11-service-layer-extraction
verified: 2026-09-16T15:25:00Z
status: passed
score: 7/7 must-haves verified
behavior_unverified: 0
overrides_applied: 0
decision_coverage:
  honored: 15
  total: 15
  not_honored: []
gaps: []
deferred: []
---

# Phase 11: Service Layer Extraction Verification Report

**Phase Goal:** Host embute o gerador in-process via `generate_batch` e recebe `ExerciseBatch` validado (ou erro discriminável), sem derrubar o processo; CLI argparse e wizard `gerar` permanecem idênticos.
**Verified:** 2026-09-16T15:25:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | ------- | ---------- | -------------- |
| 1 | Host chama `generate_batch(request)` e recebe `ExerciseBatch` — sem print de exercício, sem `--out`, sem `sys.exit` no caminho de biblioteca (EMBED-01 / SC1) | ✓ VERIFIED | `service.generate_batch` returns batch; no `sys.exit`/batch print in `service.py`; `test_generate_batch_returns_batch_without_stdout_dump`, `test_generate_batch_raises_normal_exception` |
| 2 | Host distingue config / pedido inválido / geração esgotada via subclasses + `.kind` sem casar PT (EMBED-02 / SC2) | ✓ VERIFIED | `ConfigError` / `InvalidRequestError` / `GenerationFailedError` in `service.py`; raise sites migrated; `test_config_error_kind_missing_key`, `test_validation_exhaustion_raises_invalid_request_error` |
| 3 | CLI argparse + wizard `gerar` intactos; bound 1–40 no domínio e argparse (EMBED-03 / SC3) | ✓ VERIFIED | `main.run` delegates then presents/exits; wizard calls `main.run`; `Field(ge=1, le=40)` + `_positive_quantidade`; `test_run_still_writes_out_and_exits_on_failure`, `test_models.py`, suite 155 passed (orchestrator) |
| 4 | Após qualquer `generate_batch`, `LLM_PROVIDER` / `LLM_REASONING_EFFORT` restaurados (EMBED-04 / SC4) | ✓ VERIFIED | `_scoped_env` always snapshots/restores; `test_generate_batch_restores_env_after_provider_mutation` |
| 5 | Client Gemini com timeout HTTP finito; pior caso documentado (EMBED-05 / SC5) | ✓ VERIFIED | `HttpOptions(timeout=30000)` in `generator_gemini.get_client`; README worst-case note; `test_gemini_client_http_timeout_is_30000_ms` |
| 6 | Diagnósticos/CLI não quebram em cp1252 com glifos `√`/`→` (EMBED-06 / SC5) | ✓ VERIFIED | FAILOVER hop uses ASCII `->`; validator `_write_stderr_safe` + `ensure_ascii`; CLI `reconfigure(utf-8, replace)`; `test_encoding.py` (5 tests) |
| 7 | README contrato curto: assinatura, JSON, 3 subclasses, reservados, sequencial (EMBED-07 / SC5) | ✓ VERIFIED | README Embed/biblioteca section with all anchors; reserved module list; sequential contract; Gemini timeout note |

**Score:** 7/7 truths verified (0 present, behavior-unverified)

Supporting (wired into truths above, not scored separately):

- **D-15:** `service.py` has no `import main` / `from main` — `test_service_source_does_not_import_main`
- **D-06/D-07:** service path writes no postmortem; CLI `main.run` owns `_write_postmortem`; flush `OSError` guarded — `test_service_path_exhaustion_writes_no_postmortem`, `test_flush_oserror_does_not_mask_generation_error`, `test_math_exhaustion_prefix_and_postmortem` via `main.run`

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------ | ------- |
| `exercise-ai/service.py` | Public `generate_batch` + error classes + `_scoped_env` | ✓ VERIFIED | Substantive; wired from `main` and tests; no `main` import |
| `exercise-ai/main.py` | CLI adapter: delegate → print/`--out`/fail-log/exit | ✓ VERIFIED | `generate_batch` call; postmortem on ValueError; `sys.exit`; stdio reconfigure |
| `exercise-ai/models.py` | `quantidade` 1–40 + non-empty `topico` | ✓ VERIFIED | `Field(ge=1, le=MAX_QUANTIDADE)`; strip validator |
| `exercise-ai/generator_gemini.py` | Finite `HttpOptions.timeout=30000` | ✓ VERIFIED | Client constructed with ms timeout |
| `exercise-ai/failover.py` | ASCII FAILOVER hop; ConfigError on secondary key | ✓ VERIFIED | Runtime print uses `->` (Unicode arrows only in docstring) |
| `exercise-ai/reliability.py` | Validation exhaustion → `InvalidRequestError`; no library postmortem write | ✓ VERIFIED | Raises `kind=validation_exhausted`; `_write_postmortem` defined but only called from `main` |
| `exercise-ai/token_usage/collector.py` | Flush OSError guard | ✓ VERIFIED | `except OSError` around write path |
| `exercise-ai/tests/test_service.py` | Host-path tracer | ✓ VERIFIED | 9 tests covering return/raise/env/errors/FS |
| `exercise-ai/tests/test_models.py` | Domain bounds | ✓ VERIFIED | 0/41 reject; 1/40 accept; empty topico |
| `exercise-ai/tests/test_encoding.py` | cp1252 regressions | ✓ VERIFIED | FAILOVER + validation + reconfigure |
| `README.md` | Embed contract section | ✓ VERIFIED | Three-subclass table + reserved + sequential + timeout |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `main.run` | `service.generate_batch` | delegate pipeline; CLI owns presentation/exit | ✓ WIRED | `validated_batch = generate_batch(request)` |
| `service.generate_batch` | `failover.generate_with_failover` | `begin_run` + `resolve_max_retries(None)` + flush finally | ✓ WIRED | Body of `generate_batch` |
| `service.generate_batch` | `_scoped_env` finally | always restore provider/reasoning | ✓ WIRED | `with _scoped_env():` wraps body |
| `main.run` except ValueError | `reliability._write_postmortem` | CLI-only postmortem | ✓ WIRED | Only call site of `_write_postmortem` is `main.py` |
| `flush_token_usage` / collector | OSError guard | finally must not mask primary error | ✓ WIRED | collector + service finally |
| `generator_gemini.get_client` | `types.HttpOptions(timeout=30000)` | ms per google-genai | ✓ WIRED | Client constructor |
| `failover` FAILOVER line | ASCII `->` | cp1252-safe stderr | ✓ WIRED | Runtime format string; encoding tests |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `generate_batch` return | `ExerciseBatch` | `generate_with_failover` → reliability pipeline | Yes (mocked in tracer; real in integration suite) | ✓ FLOWING |
| CLI `--out` JSON | `validated_batch.model_dump()` | Result of `generate_batch` in `run` | Yes | ✓ FLOWING |
| Error `.kind` | exception attrs | Raise sites (generator/failover/reliability/reasoning/main) | Yes | ✓ FLOWING |
| Env restore | `LLM_PROVIDER` / `LLM_REASONING_EFFORT` | Snapshot in `_scoped_env` | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Host seam + errors + env + FS | `pytest exercise-ai/tests/test_service.py -q` | 9 passed | ✓ PASS |
| Domain bounds | `pytest exercise-ai/tests/test_models.py -q` | 6 passed | ✓ PASS |
| cp1252 FAILOVER line | `pytest …/test_encoding.py::test_failover_diagnostic_encodes_on_cp1252` | passed | ✓ PASS |
| Gemini timeout pin | `pytest …/test_generators.py::test_gemini_client_http_timeout_is_30000_ms` | passed | ✓ PASS |
| Full offline suite | (orchestrator prior run) | 155 passed | ✓ PASS (reported) |

Combined verifier-run subset: **18 passed** in ~2.2s (service + models + two named checks).

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| — | — | No phase-declared `scripts/*/tests/probe-*.sh` | SKIP |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| EMBED-01 | 11-01 | `generate_batch` → batch; no print/out/exit | ✓ SATISFIED | Truth 1; `service.py` + `test_service.py` |
| EMBED-02 | 11-02 | Discriminable config/invalid/exhausted via kind/subclasses | ✓ SATISFIED | Truth 2; error classes + raise sites |
| EMBED-03 | 11-01, 11-02 | CLI/wizard identical; domain+argparse 1–40 | ✓ SATISFIED | Truth 3; `main`/`wizard`/`models` |
| EMBED-04 | 11-02 | Env restored after any call | ✓ SATISFIED | Truth 4; `_scoped_env` |
| EMBED-05 | 11-03 | Gemini finite timeout + worst-case docs | ✓ SATISFIED | Truth 5; `generator_gemini` + README |
| EMBED-06 | 11-03 | cp1252-safe diagnostics/CLI | ✓ SATISFIED | Truth 6; encoding harden + tests |
| EMBED-07 | 11-03 | Short contract docs + reserved names | ✓ SATISFIED | Truth 7; README section |

No orphaned Phase 11 requirements — all seven EMBED-* appear in plans and REQUIREMENTS.md.

### Decision Coverage

All 15 CONTEXT decisions (D-01…D-15) honored in shipped artifacts (plans, summaries, and code). Non-blocking gate: 15/15.

| Decision | Honored? | Evidence |
| -------- | -------- | -------- |
| D-01 signature request-only | yes | `def generate_batch(request: GenerationRequest)` |
| D-02 return `ExerciseBatch` | yes | Annotated return + tests |
| D-03 error subclasses | yes | Three classes under ValueError/RuntimeError |
| D-04 rich attrs | yes | `.kind` / `retriable` / `api_error_kind` |
| D-05 logger not print conversion | yes | service logger; ~33 stderr prints remain |
| D-06 no service postmortem/fail-log | yes | CLI-only postmortem call site |
| D-07 flush OSError guard | yes | collector + service finally |
| D-08 always-on env restore | yes | `_scoped_env` |
| D-09 domain 1–40 + argparse kept | yes | models + `_positive_quantidade` |
| D-10 cp1252 harden | yes | ASCII hop + safe dump + reconfigure |
| D-11 Gemini timeout + README worst case | yes | 30000 ms + README |
| D-12 README contract (not CONTRACT.md) | yes | Embed section present |
| D-13 pure move first | yes | Plan 01 then 02/03 (historical) |
| D-14 CLI/wizard zero regression | yes | wizard→`main.run`; SystemExit tests |
| D-15 service↛main | yes | source + test |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| — | — | No TBD/FIXME/XXX debt markers in phase-touched production files | — | — |
| `failover.py` | docstring | Unicode `→`/`↔` in docstring only | ℹ️ Info | Not on runtime stderr path; encoding tests cover prints |

**Prohibitions (judgment-tier, LLM non-authoritative):** No kwargs on `generate_batch`; return type not widened; no Settings object; no CONTRACT.md; packaging/rename untouched; internal print→logging not done — all appear satisfied in code/docs. Flag: *unverified-prohibition — human review recommended* (soft; does not block AFK `passed`).

### Human Verification Required

None — all must-have truths have automated behavioral evidence; no PRESENT_BEHAVIOR_UNVERIFIED items.

### Gaps Summary

No gaps. Phase goal achieved: embed seam is host-callable with discriminable errors, CLI intact, env restore, Gemini timeout, cp1252 harden, and README contract.

---

_Verified: 2026-09-16T15:25:00Z_
_Verifier: gsd-verifier (generic-agent workaround)_
