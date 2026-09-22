---
status: diagnosed
phase: 14-mixed-prompt-plan-adherence-demo-enablement
source:
  - 14-01-SUMMARY.md
  - 14-02-SUMMARY.md
  - 14-VERIFICATION.md
started: 2026-09-22T13:17:00Z
updated: 2026-09-22T14:14:00Z
---

## Current Test

number: 4
name: Live DEMO-01 uniform legacy path
expected: |
  Uma sola banda > 0 → payload com dificuldade + quantidade=contagem da banda, sem plano.
awaiting: none — session complete

## Tests

### 1. Quantidade unlock + cold start
expected: quantidade first at 0; bands disabled until qty > 0; page loads from fresh serve
result: pass

### 2. Soft-warn sem bloquear submit
expected: Com qty e bandas desalinhadas, aparece aviso #fff8e1; Gerar ainda envia o POST
result: pass

### 3. Live DEMO-01 mixed band path
expected: 2+ bandas > 0 → POST inclui plano; Exercícios renderizam; dificuldades por slot aderentes
result: pass

### 4. Live DEMO-01 uniform legacy path
expected: Uma sola banda > 0 → payload com dificuldade + quantidade=contagem da banda, sem plano
result: issue
reported: "deu invalid request error InvalidRequestError após 1 regenerações: resumo dificuldades diverge: esperado ['medio'], obtido ['medio', 'medio'] kind: validation_exhausted"
severity: blocker

## Summary

total: 4
passed: 3
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- gap_id: G-14-4
  truth: "Uniform single-band POST succeeds; ExerciseBatch.dificuldades echoes request summary (e.g. ['medio']) not per-exercise repetition"
  status: failed
  reason: "User reported: InvalidRequestError após 1 regenerações: resumo dificuldades diverge: esperado ['medio'], obtido ['medio', 'medio'] kind: validation_exhausted"
  severity: blocker
  test: 4
  root_cause: "verify_plan_echo requires batch.dificuldades == request.dificuldades (unique band summary, D-07/D-10). Structured Outputs schema describes dificuldades as a list without uniqueness/length-1..3 constraint; the model often emits one entry per exercise (['medio','medio'] for qty=2). Per-slot Exercise.dificuldade may be fine; RELY regenerates the same shape and exhausts."
  artifacts:
    - exercise-ai/models.py (ExerciseBatch.dificuldades Field + verify_plan_echo summary check)
    - exercise-ai/prompts.py (no guidance on batch dificuldades summary)
  missing:
    - Prompt or schema cue that dificuldades is unique bands used (1–3), fácil→médio→difícil — not N copies
    - Optional: canonicalize comparison via _band_summary(exercicios) if PRODUCT accepts relaxing exact list equality for duplicate padding
  debug_session: ""
