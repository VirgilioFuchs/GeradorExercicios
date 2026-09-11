---
status: complete
phase: 07-continuous-integration
source:
  - 07-01-SUMMARY.md
started: "2026-09-11T13:28:00.000Z"
updated: "2026-09-11T14:15:00.000Z"
---

## Current Test

[testing complete]

## Tests

### 1. README documents CI
expected: |
  Open README.md section "## Como testar".
  You should see the local command `pytest exercise-ai -q` unchanged,
  plus one sentence stating that push/PR to `master` runs the GitHub Actions
  workflow named `CI` with that same command.
result: pass

### 2. Workflow file matches the CI contract
expected: |
  Open `.github/workflows/ci.yml`.
  You should see: `name: CI`; job `test`; `ubuntu-latest`; Python `3.11`;
  `actions/checkout@v7` and `actions/setup-python@v7`;
  `pip install -r exercise-ai/requirements.txt`; `pytest exercise-ai -q`;
  triggers on `push` and `pull_request` for `master` only;
  `permissions: contents: read`.
  You should NOT see matrix, coverage, secrets for LLM keys, `continue-on-error`,
  or `workflow_dispatch`.
result: pass

### 3. Local pytest suite still green
expected: |
  From the repo root, run `pytest exercise-ai -q`.
  The suite should pass (about 73 tests) without needing real LLM API keys.
result: pass

### 4. GitHub Actions check appears on push/PR
expected: |
  After pushing this branch or opening/updating a PR targeting `master`,
  the GitHub Checks / Actions tab should show a workflow run named `CI`
  with job `test` that ends green (pass) or red (fail) — visible status,
  no need for branch-protection API.
result: pass

## Summary

total: 4
passed: 4
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none yet]
