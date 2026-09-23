---
phase: 13-request-schema-plan-contract
verified: 2026-09-23T13:20:00Z
status: passed
score: 5/5 roadmap criteria verified (offline)
retroactive: true
---

# Phase 13: Request schema & plan contract — Verification Report

**Phase Goal:** Domínio tipado para plano misto/uniforme com invariantes; embed `generate_batch → ExerciseBatch` intacto.
**Status:** passed (retroactive seal — SUMMARY + suite evidence; gap filled at v2.1 audit)
**Re-verification:** No — first written VERIFICATION after Phase 13 execute

## ROADMAP Success Criteria

| # | Criterion | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Request com specs por item **ou** modo uniforme | ✓ | `GenerationRequest` + `plano`/`itens` XOR; `test_mixed_plano_expands_facil_medio`, `test_uniform_legacy_normalizes_dificuldades` |
| 2 | `quantidade` ≠ len(plano) rejeitado antes da LLM | ✓ | normalize raises; `test_quantidade_mismatch_plano_rejected` |
| 3 | Cada exercício pode ecoar `dificuldade` do slot | ✓ | required `Exercise.dificuldade` + `verify_plan_echo`; `test_exercise_and_batch_require_echo_fields`, `test_verify_plan_echo_passes_and_fails` |
| 4 | Cap quantidade permanece **40** | ✓ | `le=MAX_QUANTIDADE`; `test_max_quantidade_cap_unchanged` |
| 5 | Suite uniforme continua verde | ✓ | Phase close: 172 passed; audit recheck: `pytest exercise-ai` **198 passed** |

## Requirements

| ID | Status | Evidence |
| --- | --- | --- |
| BATCH-01 | Complete | `plano` / `itens` / equal-split; XOR tests |
| BATCH-02 | Complete | qty ↔ plan length fail-closed at Pydantic |
| BATCH-03 | Complete | echo fields + pure `verify_plan_echo` |
| BATCH-04 | Complete | uniform legacy normalize |
| CAP-01 | Complete | `MAX_QUANTIDADE == 40` |

## Notes

- `verify_plan_echo` intentionally **not** wired into RELY in this phase (Phase 14).
- Prompts / CLI / demo untouched here by design.
