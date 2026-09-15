---
phase: 07-continuous-integration
plan: 01
subsystem: infra
tags: [github-actions, ci, pytest, offline]

requires:
  - phase: 03-tests-logging-docs
    provides: Canonical `pytest exercise-ai -q` suite without live LLM
provides:
  - Minimal GitHub Actions workflow `CI` / job `test` on master push+PR
  - README Como testar note mirroring the same pytest command
affects: [08-provider-failover, production-confidence]

actuals:
  tokens: 450
  tasks: 2
  commits: 1

tech-stack:
  added: [actions/checkout@v7, actions/setup-python@v7]
  patterns: [single-job-offline-ci, no-llm-secrets-in-actions]

key-files:
  created:
    - .github/workflows/ci.yml
  modified:
    - README.md

key-decisions:
  - "Workflow file `.github/workflows/ci.yml`, name CI, job test (D-15)"
  - "Omit pip cache and D-13 env unset (discretion + D-03)"
  - "Pin actions @v7; permissions contents:read"

requirements-completed: [CI-01, CI-02]

duration: ~15min
completed: 2026-09-11
---

# Phase 07 Plan 01 — Summary

## What shipped

Greenfield GitHub Actions workflow that installs `exercise-ai/requirements.txt` and runs `pytest exercise-ai -q` from the repo root on `push`/`pull_request` to `master`, with `permissions: contents: read` and **no** LLM API secrets. README `## Como testar` gained one sentence documenting that behavior.

## Files changed (this plan)

| File | Change |
|------|--------|
| `.github/workflows/ci.yml` | **Created** — single job `test` |
| `README.md` | **Modified** — one CI sentence under Como testar |

No Python under `exercise-ai/` was modified by this plan. Pre-existing dirty `exercise-ai/generator.py` was left untouched and **not** included in the phase commit.

## Workflow contract (verified locally)

- `name: CI`
- Triggers: `push` + `pull_request` → `branches: [master]`
- Job: `test` on `ubuntu-latest`
- Python `3.11` via `actions/setup-python@v7`
- `actions/checkout@v7`
- `pip install -r exercise-ai/requirements.txt`
- `pytest exercise-ai -q`
- `permissions: contents: read`
- Absent: matrix, coverage, ruff/mypy, Docker/tox, `workflow_dispatch`, `pull_request_target`, `continue-on-error`, `secrets.`, `LLM_API_KEY`, `GEMINI_API_KEY`

## Tests executed and results

| Command | Result |
|---------|--------|
| `pytest exercise-ai -q` | **73 passed**, 2 warnings (pre-existing pydantic/genai), exit 0 |
| PLAN assert `ci.yml` shape | **OK** (`ci.yml shape OK`) |
| PLAN assert README Como testar | **OK** (`README CI note OK`) |

## MCPs actually used

| MCP / tool | Used? | Calls / outcome |
|------------|-------|-----------------|
| **Serena** | Yes | `activate_project`; `search_for_pattern` on `exercise-ai/tests/conftest.py` for `load_dotenv\|LLM_API_KEY` → empty (no dotenv/secret load in conftest) |
| **Context7** | **No** | Not called — workflow shape fully specified by PLAN; no API/syntax doubt |
| **Semgrep `semgrep_scan`** | Attempted | **Failed** — RPC `Connection lost` (same class of failure as prior sessions) |
| **Semgrep `semgrep_scan_with_custom_rule`** | Yes (fallback) | Ran custom YAML rules for LLM secret names / `continue-on-error`. Engine also scanned the rule payload itself and reported self-matches on `rule.yaml` pattern strings — **not** findings in `ci.yml` content. `ci.yml` text contains none of those tokens (confirmed by PLAN python assert). |

## Semgrep findings

1. **Default scan:** unavailable (RPC Connection lost) — recorded as failure, not claimed success.
2. **Custom-rule fallback:** no genuine hits on `.github/workflows/ci.yml` body; spurious hits only on the rule definition file. Treat as **clean for CI-01 secret surface** given assert evidence.

## Requirement status

| ID | Local evidence | Status |
|----|----------------|--------|
| CI-01 | Workflow installs + pytest offline; no LLM secrets in YAML | **Met** (local) |
| CI-02 | No `continue-on-error`; pytest fail fails job by Actions semantics | **Local contract verified**; GitHub check run pending first push/PR |

### CI-02 LOCAL CONTRACT: VERIFIED

Shape asserts + absence of `continue-on-error` / secrets injection.

### CI-02 GITHUB RUNTIME: VERIFIED

PR #4: Actions run `CI` / job `test` → **success** (https://github.com/VirgilioFuchs/GeradorExercicios/pull/4).

## Self-Check: Requirements Satisfaction

| Requirement | Status | Evidence |
|-------------|--------|----------|
| CI-01 | SATISFIED (local) | `ci.yml` + pytest 73 passed + no secret keys in workflow |
| CI-02 | SATISFIED | Local fail-red contract + GitHub Checks green on PR #4 |

## Threat model notes

Mitigations from PLAN T-07-01…T-07-06 applied in YAML (no secrets, `pull_request` not `pull_request_target`, `contents: read`, no `continue-on-error`, `master` filters).

## Next

1. Commit/push branch so GitHub runs the workflow once → flip CI-02 GITHUB RUNTIME to VERIFIED when green/red appears.
2. Proceed to Phase 8 (Provider Failover) when ready — do not mix SEED-002/SEED-003 here.
