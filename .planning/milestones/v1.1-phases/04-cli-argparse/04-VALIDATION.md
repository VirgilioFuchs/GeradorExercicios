---
phase: "04"
slug: "cli-argparse"
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-09-08"
validated: "2026-09-08"
source: reconstruct-from-artifacts
research: skipped
---

# Phase 04 — Validation Strategy

> Post-execution Nyquist contract from SUMMARY coverage + pytest suite + VERIFICATION.md.
> Research was skipped for Phase 4.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest ≥8.0 |
| **Quick run command** | `pytest exercise-ai/tests/test_main.py -q` |
| **Full suite command** | `pytest exercise-ai -q` |
| **Estimated runtime** | ~3 seconds (39 passed) |
| **Live LLM** | Forbidden — mocks only |

---

## Sampling Rate

- **After every task commit:** `pytest exercise-ai/tests/test_main.py -q`
- **After plan wave / before UAT:** `pytest exercise-ai -q`
- **Max feedback latency:** 15 seconds

---

## Requirement → Test Cross-Reference

| Requirement | Gap status | Primary tests | Evidence |
|-------------|------------|---------------|----------|
| CLI-04 | COVERED | `test_main.py` (dual-output, argparse rejects, provider, help) | SUMMARY D1–D4; VERIFICATION 7/7; UAT 5/5 pass |

---

## Per-Task Verification Map

| Task ID | Requirement | Test Type | Automated Command | Status |
|---------|-------------|-----------|-------------------|--------|
| 04-01-T1 | CLI-04 / D-14 | decision | human `proceed-d14` | ✅ |
| 04-01-T2 | CLI-04 | unit | `pytest exercise-ai/tests/test_main.py -q` | ✅ green |
| 04-01-T3 | CLI-04 | unit + docs | `pytest exercise-ai -q` + README/ROADMAP | ✅ green |

### Coverage map (SUMMARY)

| ID | Description | Command | Status |
|----|-------------|---------|--------|
| D1 | Dual-output text + `--out` JSON | `test_run_success_text_stdout_and_json_out` | ✅ |
| D2 | Argparse rejects inválidos / missing `--out` | `test_cli_rejects_*` | ✅ |
| D3 | `--provider` + D-11 missing key | `test_cli_missing_provider_key_specific_message` | ✅ |
| D4 | README + ROADMAP D-14 | docs review + SUMMARY | ✅ |

---

## Nyquist Compliance

- [x] Automated tests map to CLI-04
- [x] Full suite green without live LLM
- [x] UAT confirmation recorded (`04-UAT.md` complete)
- [x] `nyquist_compliant: true`
