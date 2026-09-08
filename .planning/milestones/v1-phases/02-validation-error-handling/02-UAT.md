---
status: complete
phase: 02-validation-error-handling
source:
  - 02-01-SUMMARY.md
started: 2026-09-04T12:04:00.000Z
updated: 2026-09-04T12:17:00.000Z
---

## Current Test

[testing complete]

## Tests

### 1. Confirmação de deliverables auto-verificados
expected: Os 4 deliverables auto-verificados refletem o comportamento real esperado da Fase 2 (validação + erros API/config)
result: pass
note: Confirmado pelo usuário após smoke DEMO_API_ERROR 12/12 e remoção do gancho demo

### 2. Semantic validator rejects bad type, empty/malformed exercicios, wrong quantity, whitespace fields with path messages
expected: Semantic validator rejects bad type, empty/malformed exercicios, wrong quantity, whitespace fields with path messages
result: pass
source: automated
coverage_id: D1

### 3. VALIDATION_REPORT_MODE all vs first_exercise; [VALIDAÇÃO]+raw JSON on failure without prefixing ValueError
expected: VALIDATION_REPORT_MODE all vs first_exercise; [VALIDAÇÃO]+raw JSON on failure without prefixing ValueError
result: pass
source: automated
coverage_id: D2

### 4. OpenAI/Gemini map_*_error helpers + dual-key missing message + ERR-03 empty/refusal/unparseable
expected: OpenAI/Gemini map_*_error helpers + dual-key missing message + ERR-03 empty/refusal/unparseable
result: pass
source: automated
coverage_id: D3

### 5. run_demo stdout JSON-only with Gerando/Validando on stderr; ValueError → SystemExit(1) plain stderr
expected: run_demo stdout JSON-only with Gerando/Validando on stderr; ValueError → SystemExit(1) plain stderr
result: pass
source: automated
coverage_id: D4

## Summary

total: 5
passed: 5
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none]
