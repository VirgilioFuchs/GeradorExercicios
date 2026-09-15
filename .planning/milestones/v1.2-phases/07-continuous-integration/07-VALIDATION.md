---
phase: "07"
slug: "continuous-integration"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: true
created: "2026-09-11"
---

# Phase 07 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Mapped from `07-RESEARCH.md` Validation Architecture + `07-01-PLAN.md` verifies (CI-01 / CI-02).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest ≥8.0 (`exercise-ai/requirements.txt`) |
| **Config file** | none — discovery via `exercise-ai/tests/` + `conftest.py` path grounding |
| **Quick run command** | `pytest exercise-ai -q` |
| **Full suite command** | `pytest exercise-ai -q` (same; ~73 tests) |
| **Estimated runtime** | ~3 seconds locally |
| **Live LLM** | Forbidden — mocks/static factories only; CI must not inject API secrets |
| **Workflow shape checks** | Inline `python -c` asserts on `.github/workflows/ci.yml` and README (plan T1–T2) |

---

## Sampling Rate

- **After every task commit:** `pytest exercise-ai -q` plus the task’s workflow/README shape assert
- **After every plan wave:** Full suite + both shape asserts (ci.yml + README Como testar)
- **Before `/gsd-verify-work`:** Full suite green; ci.yml and README shape asserts pass
- **Max feedback latency:** 30 seconds (local pytest + file asserts; GitHub Actions run is operator/runtime)

---

## Requirement → Test Cross-Reference

| Requirement | Behavior | Gap status | Automated Command | File Exists? |
|-------------|----------|------------|-------------------|--------------|
| CI-01 | Install deps + run offline pytest; no LLM API secrets in job | COVERED (plan T1) | `pytest exercise-ai -q` (local proxy for job); `python -c` shape assert on `ci.yml` (no `llm_api_key` / `gemini_api_key` / `secrets.`) | ✅ suite exists; ❌ `ci.yml` until T1 |
| CI-02 | Pytest nonzero exit → job fail / visible red check; operator sees CI on PR | COVERED (plan T1–T2) | No `continue-on-error` in shape assert; README Como testar mentions GitHub Actions `CI` on `master` | ❌ workflow/README until T1–T2; platform red/green after first push (manual) |

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|----------------|-----------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | CI-01, CI-02 | T-07-01, T-07-03, T-07-04, T-07-05, T-07-06 | No LLM secrets / `secrets.` in workflow; `pull_request` only; `master` triggers; no `continue-on-error`; `permissions: contents: read` | unit + workflow shape | `pytest exercise-ai -q`; `python -c "…ci.yml shape OK…"` (see 07-01-PLAN T1) | ✅ suite; ❌ W0→T1 for ci.yml | ⬜ pending |
| 07-01-02 | 01 | 1 | CI-02 | — | Docs name workflow only; no sample secrets; local command unchanged | docs + unit | `python -c "…README CI note OK…"`; `pytest exercise-ai -q` | ✅ README; ❌ CI sentence until T2 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

### Shape-assert contract (from 07-01-PLAN)

**ci.yml must include:** `name: CI`, `master`, `ubuntu-latest`, `3.11`, `actions/checkout@v7`, `actions/setup-python@v7`, `pip install -r exercise-ai/requirements.txt`, `pytest exercise-ai -q`.

**ci.yml must omit:** `continue-on-error`, `workflow_dispatch`, `pull_request_target`, `matrix:`, `llm_api_key`, `gemini_api_key`, `secrets.` (case-insensitive for key names).

**README `## Como testar` chunk must include:** `pytest exercise-ai -q`, GitHub Actions mention, `master`, `CI`.

---

## Wave 0 Requirements

Existing infrastructure covers offline suite guarantees — no new pytest files or framework install.

- ✅ `exercise-ai/tests/` + `conftest.py` — mock suite (~73 tests); local proxy for CI job command
- ✅ `pytest` already in `exercise-ai/requirements.txt`
- ✅ Plan T1/T2 `<automated>` verifies create/check greenfield artifacts (not pre-stubs):
  - `.github/workflows/ci.yml` — created in T1
  - README CI one-liner under Como testar — added in T2

*Wave 0 complete: no MISSING test-file stubs; orchestration artifacts are execution outputs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| First GitHub Actions run shows check named `CI` / job `test` green or red on PR | CI-02 | Platform Checks UI after push; not automatable in-plan beyond YAML contract | After merge/push of workflow to `master` (or open PR targeting `master`), confirm Actions run appears; optional: push a known-failing commit once to see red, then revert |

*All other phase behaviors have automated verification (pytest + shape asserts).*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify (2 tasks, both verified)
- [x] Wave 0 covers all MISSING references (none — suite pre-exists; workflow/README are T1/T2 outputs)
- [x] No watch-mode flags
- [x] Feedback latency < 30s for automated verifies
- [ ] `nyquist_compliant: true` set in frontmatter *(set by validate-phase after execution)*

**Approval:** pending
