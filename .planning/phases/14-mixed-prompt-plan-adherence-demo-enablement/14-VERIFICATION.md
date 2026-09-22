---
phase: 14-mixed-prompt-plan-adherence-demo-enablement
verified: 2026-09-22T14:54:00Z
status: passed
score: 10/10 must-haves verified
behavior_unverified: 0
human_verification:
  - test: "Live DEMO-01 mixed band path"
    expected: "Three band inputs; soft-warn on sum=0 / sum>40 / qty≠sum; Gerar still enabled; mixed → plano in network/JSON; exercises adhere to slots"
    result: pass
    why_human: "Needs live LLM keys + real browser"
  - test: "Live DEMO-01 uniform legacy path"
    expected: "Single non-zero band → payload has dificuldade + quantidade=band count, no plano"
    result: pass
    notes: "G-14-4 closed via 14-03 + canonical unique-band compare; operator confirmed live"
    why_human: "Browser DevTools confirmation of payload shape"
---

# Phase 14: Mixed prompt + plan-adherence + demo enablement — Verification Report

**Phase Goal:** Lotes mistos são instruídos no prompt, verificados no validator/RELY, e habilitados na demo (mesmo `GenerationRequest`); RELY/math_check não são redesenhados.
**Verified:** 2026-09-22T13:01:29Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### ROADMAP Success Criteria

| # | Criterion | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Com plano misto, o prompt enumera cada slot → dificuldade esperada | ✓ VERIFIED | `prompts._format_slot_list` from `itens_ordenados`; hybrid labels; `test_mixed_prompt_enumerates_hybrid_slots` + uniform always-enumerate |
| 2 | Validator falha se count ou dificuldade por slot não aderir ao plano | ✓ VERIFIED | Plan echo is RELY-owned (`verify_plan_echo` after validate per D-05); fails on length, per-slot, and batch `dificuldades` summary — `test_verify_plan_echo_*` |
| 3 | Falhas de adesão/validação ainda entram no loop RELY existente (bounded) | ✓ VERIFIED | `reliability.py` L118–119 then existing `except ValueError`; `test_plan_echo_mismatch_retries_then_succeeds` / `_exhausts_validation`; `test_single_retry_loop_only` |
| 4 | math_check continua sem overhaul; fixtures offline cobrem mismatch de plano | ✓ VERIFIED | `validator.py` has no `verify_plan_echo`; `check_math_batch` unchanged ownership; offline echo mismatch fixtures in models + reliability tests |
| 5 | Demo UI permite contagens por banda e `POST /gerar` monta `plano` | ✓ VERIFIED | Offline markers + live UAT 4/4 (mixed + uniform after 14-03 / G-14-4) — see `14-UAT.md` |

### Observable Truths (plan must_haves)

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | User prompt always includes numbered slot list from `itens_ordenados` (uniform + mixed) with hybrid PT+enum labels (D-01..D-04; PROMPT-01) | ✓ VERIFIED | `prompts.py` `_HYBRID_LABELS` + `_format_slot_list`; `test_prompts.py` mixed + uniform |
| 2 | Prompt does not re-list enunciado/resposta/explicacao field contracts in user prompt (D-03; SEED-008) | ✓ VERIFIED | `USER_PROMPT_TEMPLATE` has slot list + topic requirements only; no field-contract bullets. (SYSTEM_PROMPT retains pre-existing quality prose, not a Structured Outputs field list.) |
| 3 | `generate_validated_batch` calls `validate_exercise_batch` then `verify_plan_echo`; not from `validator.py` (D-05, D-06; VAL-01) | ✓ VERIFIED | `reliability.py` order; `test_single_retry_loop_only` asserts echo in reliability source and absent from validator |
| 4 | `verify_plan_echo` fails closed on per-slot mismatch and batch `dificuldades` ≠ request summary (D-07) | ✓ VERIFIED | `models.verify_plan_echo` L211–229; `test_verify_plan_echo_passes_and_fails` + `_batch_dificuldades_summary_mismatch` + `_length_mismatch` |
| 5 | Plan-echo `ValueError` enters bounded RELY; math_check / retry bounds / failover not redesigned (D-08; VAL-02) | ✓ VERIFIED | Same `except ValueError` → retry / `validation_exhausted`; single-loop + echo exhaust tests pass |
| 6 | Demo Contrato form: three band counts + editable quantidade; dificuldade select removed (D-09, D-10) | ✓ VERIFIED | `demo/index.html` facil/medio/dificil + quantidade; no `name="dificuldade"`; `test_index_html_band_counts_and_soft_warn` |
| 7 | Soft-warn advisory for sum=0 / sum>40 / qty≠sum without blocking POST (D-11) | ✓ VERIFIED | `updateSoftWarn` + submit never gated on warn; CSS `#fff8e1` / `.soft-warn`; marker tests |
| 8 | Client sends `plano` only when 2+ bands > 0; uniform uses legacy shape with band dificuldade + band quantidade (D-12..D-14) | ✓ VERIFIED | `buildGerarPayload` in `app.js`; `test_app_js_payload_rules_uniform_vs_mixed` |
| 9 | `demo/serve.py` constructs `GenerationRequest` with `plano` when present (D-15) | ✓ VERIFIED | `req_kwargs["plano"]` when body has plano; no forced `dificuldade="medio"`; tracer passthrough |
| 10 | Offline demo tests cover mixed plano POST and UI markers | ✓ VERIFIED | `pytest demo/tests -q` → 23 passed |

**Score:** 10/10 plan must-haves verified (live DEMO-01 UAT complete 2026-09-22)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `exercise-ai/prompts.py` | Slot enumeration + hybrid labels | ✓ EXISTS + SUBSTANTIVE | `itens_ordenados` → numbered list; `fácil (facil)` etc. |
| `exercise-ai/models.py` | `verify_plan_echo` + summary check | ✓ EXISTS + SUBSTANTIVE | Slot + `batch.dificuldades` vs `request.dificuldades` |
| `exercise-ai/reliability.py` | Post-validate echo hook | ✓ EXISTS + SUBSTANTIVE | validate then `verify_plan_echo` |
| `exercise-ai/tests/test_prompts.py` | Mixed + uniform prompt tests | ✓ EXISTS + SUBSTANTIVE | New module |
| `exercise-ai/tests/test_models.py` | Echo mismatch fixtures | ✓ EXISTS + SUBSTANTIVE | Pass/fail/summary/length |
| `exercise-ai/tests/test_reliability.py` | Echo → RELY / exhaustion | ✓ EXISTS + SUBSTANTIVE | Retry + exhaust + layer assert |
| `demo/index.html` | Band inputs + soft-warn | ✓ EXISTS + SUBSTANTIVE | No dificuldade select |
| `demo/app.js` | Soft-warn + payload builder | ✓ EXISTS + SUBSTANTIVE | `buildGerarPayload` / `updateSoftWarn` |
| `demo/serve.py` | `plano` → `GenerationRequest` | ✓ EXISTS + SUBSTANTIVE | Conditional passthrough |
| `demo/tests/test_ui_markers.py` | Band / soft-warn / payload markers | ✓ EXISTS + SUBSTANTIVE | Fail-closed needles |
| `demo/tests/test_tracer_gerar.py` | Mixed plano tracer + qty drift 400 | ✓ EXISTS + SUBSTANTIVE | Mocked `generate_batch` |

**Artifacts:** 11/11 verified

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `GenerationRequest.itens_ordenados` | USER prompt slot list | `build_prompts` / `_format_slot_list` | ✓ WIRED | Always enumerate |
| `validate_exercise_batch` | `verify_plan_echo` | `generate_validated_batch` order | ✓ WIRED | validate then echo |
| `verify_plan_echo` ValueError | RELY retry / `validation_exhausted` | existing `except ValueError` | ✓ WIRED | Offline tests prove path |
| Demo band counts | POST `/gerar` JSON | `buildGerarPayload` | ✓ WIRED | mixed→plano; uniform→legacy |
| `body.plano` | `GenerationRequest(plano=...)` | `DemoHandler.do_POST` | ✓ WIRED | D-15 |
| `GenerationRequest` | service / RELY / prompts | existing `generate_batch` | ✓ WIRED | Same contract as Phase 13+14-01 |

### Prohibitions Check

| Prohibition | Status |
| ----------- | ------ |
| No `verify_plan_echo` in `validator.py` | ✓ Held |
| No RELY / math_check / failover redesign | ✓ Held |
| No field-contract bullets in user prompt | ✓ Held |
| No CLI/wizard compact plano (Phase 15) | ✓ Held (out of scope) |
| Soft-warn does not block submit | ✓ Held |
| Uniform does not always-send `plano` | ✓ Held |

## Requirements Coverage

| Requirement | Status | Evidence |
| ----------- | ------ | -------- |
| PROMPT-01 | ✓ SATISFIED | Slot enumeration tests + `prompts.py` |
| VAL-01 | ✓ SATISFIED | `verify_plan_echo` slot + summary; wired in RELY |
| VAL-02 | ✓ SATISFIED | Existing RELY bounds; math in validator; no redesign |
| DEMO-01 | ✓ SATISFIED | Offline form + payload + serve ✓; live UAT 4/4 in `14-UAT.md` |

**Coverage:** 4/4 requirements closed (offline + live UAT)

## Anti-Patterns Found

| File | Pattern | Severity | Impact |
| ---- | ------- | -------- | ------ |
| — | None blocking | — | — |

**Note:** `SYSTEM_PROMPT` still mentions enunciado/resposta/explicação as pedagogical quality (pre-existing). User-prompt field-list contracts were not reintroduced — aligned with D-03 plan prohibition scope.

## Human Verification Required

### 1. Live DEMO-01 mixed band path — PASSED

**Test:** `python demo/serve.py` → open `http://[::1]:8642/` → mixed bands → Gerar  
**Result:** pass (operator UAT 2026-09-22)

### 2. Live DEMO-01 uniform + soft-warn glance — PASSED

**Test:** Single non-zero band; soft-warn cases  
**Result:** pass after G-14-4 (14-03 + canonical `dificuldades` unique-band compare); operator confirmed

## Gaps Summary

**No open gaps.** Plans 14-01..14-03 must-haves hold; live DEMO-01 UAT complete (`14-UAT.md` status: complete).

## Automated Checks

| Suite | Command | Result |
| ----- | ------- | ------ |
| exercise-ai | `pytest exercise-ai -q` | 179 passed, 2 warnings |
| demo | `pytest demo/tests -q` | 23 passed |

## Verification Metadata

**Verification approach:** Goal-backward (ROADMAP SC + plan must_haves)  
**Must-haves source:** `14-01-PLAN.md` + `14-02-PLAN.md` frontmatter  
**Automated checks:** 2 suites passed, 0 failed  
**Human checks required:** 0 (both live DEMO-01 tests passed)  
**Spot-checked code:** `prompts.py`, `reliability.py`, `models.py` (`verify_plan_echo`), `demo/app.js`, `demo/serve.py`, `demo/index.html`

---
*Verified: 2026-09-22T14:54:00Z (re-verified after 14-03 + live UAT)*
*Initial verifier: gsd-verifier (subagent); human UAT closed by operator*

## VERIFICATION PASSED
