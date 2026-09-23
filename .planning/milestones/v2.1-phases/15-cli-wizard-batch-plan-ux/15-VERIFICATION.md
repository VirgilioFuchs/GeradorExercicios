---
phase: 15-cli-wizard-batch-plan-ux
verified: 2026-09-23T13:00:00Z
status: passed
score: 4/4 roadmap criteria verified (offline)
---

# Phase 15: CLI / wizard batch-plan UX — Verification Report

**Phase Goal:** Operador define o plano com UX compacta (wizard + argparse); mesmo `GenerationRequest` da demo.
**Status:** passed (offline); optional live wizard smoke left to operator

## ROADMAP Success Criteria

| # | Criterion | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Wizard `gerar` band counts → request | ✓ | `wizard.py` + `test_gerar_main_uniform_via_bands` / `test_gerar_main_mixed_plano` |
| 2 | Argparse `--plano F,M,D` | ✓ | `main.py` + `test_cli_plano_*` |
| 3 | Docs: shared GenerationRequest | ✓ | `README.md` `--plano` + wizard bands |
| 4 | Caller matrix offline green | ✓ | `pytest exercise-ai` **198 passed** |

## Requirements

| ID | Status |
| --- | --- |
| UX-01 | Complete |
| UX-02 | Complete |

## Human (optional)

| Test | Expected |
| --- | --- |
| Live `python exercise-ai/main.py gerar` | Band prompts; mixed lote generates |
| Live `--plano 2,1,0 --out …` | Mixed batch with keys in `.env` |
