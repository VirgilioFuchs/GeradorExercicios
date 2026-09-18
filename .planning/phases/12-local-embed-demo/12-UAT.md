---
status: testing
phase: 12-local-embed-demo
source:
  - 12-VERIFICATION.md
  - 12-01-SUMMARY.md
  - 12-02-SUMMARY.md
started: 2026-09-18T14:15:00Z
updated: 2026-09-18T14:15:00Z
---

## Current Test

number: 1
name: Live DEMO-01 happy path
expected: |
  Start `python demo/serve.py`, open http://[::1]:8642/ (not localhost).
  Presets filled; click Gerar → see Gerando… with submit disabled only.
  Exercícios tab shows rendered exercises; JSON tab shows ExerciseBatch.
  On error, EN class badge + PT message + kind when present.
awaiting: user response

## Tests

### 1. Live DEMO-01 happy path
expected: Presets → Gerar → Gerando… → Exercícios + JSON tabs with live LLM batch; typed error badge when forced
result: pending

### 2. Live DEMO-02 concurrent 409
expected: While first generation runs, second POST/submit gets HTTP 409 with literal "HTTP 409" in the message (sequential contract)
result: pending

### 3. Banner dismiss + footnote / README glance
expected: X hides top banner until reload; footnote remains; demo/README + root Embed show delete-at-close and http://[::1]:8642/
result: pending

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Notes

Automated gates already green: `pytest demo/tests -q` (17), `pytest exercise-ai -q` (155). Phase stays pending until UAT complete via `$gsd-verify-work 12`.
