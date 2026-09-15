---
status: complete
quick_id: 260915-e1i
slug: wire-json-routing-to-exercicios-gerados-
---

# Quick Plan: Wire exercicios-gerados success/fail routing

## Goal

On CLI success, write the exercise JSON under `exercise-ai/exercicios-gerados/success/`. On failure, write an error log under `fail/erros/` and keep math postmortem under `fail/postmortem/`. Absolute `--out` paths (tests/tmp) stay unchanged.

## Locked approach

1. **Success:** If `--out` is a relative path (not absolute), resolve to `exercicios-gerados/success/<name>` (create dirs). Absolute paths unchanged.
2. **Fail:** On `run()` exception before exit, append/write `fail/erros/{YYYYMMDD-HHMMSS}.txt` with the PT error message (no secrets).
3. **Postmortem:** Default `POSTMORTEM_PATH` → `exercicios-gerados/fail/postmortem/math_postmortem.jsonl` (still injectable for tests).
4. Update README of that folder + main `--out` help; keep gitignore as-is.
5. Tests: relative out lands under success; absolute tmp unchanged; fail writes erros file; postmortem default path shape.

## Out of scope

Phase 10 wizard `gerar`; changing token-usage dir.
