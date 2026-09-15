---
status: complete
quick_id: 260915-e1i
slug: wire-json-routing-to-exercicios-gerados-
---

# Quick Summary: Wire exercicios-gerados success/fail routing

## What shipped

CLI artifact routing under `exercise-ai/exercicios-gerados/`:

- **Success:** relative `--out` → `success/<basename>`; absolute paths unchanged (tests/tmp)
- **Fail:** `run()` exceptions write `fail/erros/erro-YYYYMMDD-HHMMSS.txt` (PT message, no secrets)
- **Postmortem:** default `POSTMORTEM_PATH` → `fail/postmortem/math_postmortem.jsonl` (still injectable)

## Files

| File | Change |
|------|--------|
| `exercise-ai/output_paths.py` | **Created** — resolve success + write fail error log |
| `exercise-ai/main.py` | Resolve out; mkdir; write fail logs on exceptions |
| `exercise-ai/reliability.py` | Default postmortem under fail/postmortem |
| `exercise-ai/tests/test_output_paths.py` | **Created** — path + run routing |
| `exercicios-gerados/README.md`, root `README.md` | Document layout + `--out` |

## Tests

`pytest exercise-ai -q` → **109 passed**

## Out of scope (unchanged)

Phase 10 wizard; token-usage directory
