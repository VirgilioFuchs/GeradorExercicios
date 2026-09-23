---
phase: 15-cli-wizard-batch-plan-ux
plan: 01
status: complete
completed: "2026-09-23"
commit: "2f15428"
---

# Summary: 15-01 plan_ux + argparse --plano

## Done
- `exercise-ai/plan_ux.py` — `parse_plano_csv`, `build_request_kwargs`, `soft_warn_bands`
- `main.py` — `--plano F,M,D` wired; legacy path unchanged
- Tests: `test_plan_ux.py`, `test_cli_plano.py` (10 passed)

## Key decisions applied
- Mixed → `plano` + quantidade=sum
- Uniform → legacy dificuldade + band count
- Zero bands → ValueError
