---
status: complete
phase: 12-local-embed-demo
source:
  - 12-VERIFICATION.md
  - 12-01-SUMMARY.md
  - 12-02-SUMMARY.md
started: 2026-09-18T14:15:00Z
updated: 2026-09-18T14:39:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Live DEMO-01 happy path
expected: Presets → Gerar → Gerando… → Exercícios + JSON tabs with live LLM batch; typed error badge when forced
result: pass

### 2. Live DEMO-02 concurrent 409
expected: While first generation runs, second POST/submit gets HTTP 409 with literal "HTTP 409" in the message (sequential contract)
result: pass

### 3. Banner dismiss + footnote / README glance
expected: X hides top banner until reload; footnote remains; demo/README + root Embed show delete-at-close and http://[::1]:8642/
result: pass

## Summary

total: 3
passed: 3
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none yet]
