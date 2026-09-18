---
phase: "12"
slug: "local-embed-demo"
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-18"
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `12-RESEARCH.md` ## Validation Architecture (user-forced research despite `workflow.research: false`).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest ≥8.0 (existing) |
| **Config file** | none project-wide — discovery via `pytest exercise-ai` |
| **Quick run command** | `pytest demo/tests -q` (once Wave 0 exists; **not CI**) |
| **Full suite command** | `pytest exercise-ai -q` (unchanged; must stay green; ignores `demo/`) |
| **Estimated runtime** | ~30–90 seconds (exercise-ai full); demo/tests ~seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest demo/tests -q` when present; else `pytest exercise-ai/tests/test_service.py -q`
- **After every plan wave:** Run `pytest exercise-ai -q`
- **Before `$gsd-verify-work`:** Full suite must be green + manual UAT for DEMO-01/02
- **Max feedback latency:** 90 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 12-01-T1 | 12-01 | 1 | DEMO-02 | T-12-01 | Refuse non-loopback bind | unit | `pytest demo/tests/test_guards.py::test_refuse_non_loopback -x` | ❌ W0 | ⬜ pending |
| 12-01-T1 | 12-01 | 1 | DEMO-02 | T-12-02 | Host/Origin/Content-Type allowlist | unit | `pytest demo/tests/test_guards.py -q` | ❌ W0 | ⬜ pending |
| 12-01-T1 | 12-01 | 1 | DEMO-02 | T-12-03 | Lock busy → 409 | unit | `pytest demo/tests/test_guards.py -q` | ❌ W0 | ⬜ pending |
| 12-01-T1 | 12-01 | 1 | DEMO-01 | T-12-04 | Exception → error JSON shape | unit | `pytest demo/tests/test_error_map.py -q` | ❌ W0 | ⬜ pending |
| 12-01-T2 | 12-01 | 1 | DEMO-01/02 | T-12-02..04 | Tracer POST /gerar mocked E2E | unit | `pytest demo/tests -q` | ❌ W0 | ⬜ pending |
| 12-02-T1 | 12-02 | 2 | DEMO-01 | T-12-06 | Form/tabs/Gerando…/live LLM | manual UAT | Operator opens `http://[::1]:8642/` | N/A | ⬜ pending |
| 12-02-T2 | 12-02 | 2 | DEMO-02 | T-12-07 | Banner + README anti-accretion | manual / doc | Read `demo/README.md` + UI | N/A | ⬜ pending |

*Planner must replace TBD Task IDs when writing PLAN.md. Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `demo/tests/test_guards.py` — loopback assert, Host/Origin/Content-Type, lock→409 helper
- [ ] `demo/tests/test_error_map.py` — maps three exception classes (+ `kind` / `api_error_kind`) to response dict
- [ ] Pure helpers in `demo/` (`assert_loopback`, `check_post_headers`, `error_payload`) so tests need no socket listen
- [ ] **Do not** add `demo` to GitHub Actions

*Existing `pytest exercise-ai` infrastructure covers package regression; demo tests are Wave 0.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live form → Gerando… → Exercícios/JSON tabs | DEMO-01 | Needs live LLM + browser | Start demo, use presets, submit, check tabs and schema/JSON |
| Concurrent second POST → HTTP 409 | DEMO-02 | Timing/concurrency | Hold first generate; second POST expects 409 + sequential message |
| Banner + README expiry / delete-at-close | DEMO-02 | Doc/UX acceptance | Read banner/footnote + `demo/README.md` anti-accretion pack |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 90s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
