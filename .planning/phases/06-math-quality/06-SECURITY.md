---
phase: "06"
slug: "math-quality"
status: verified
threats_open: 0
asvs_level: 1
created: "2026-09-09"
---

# Phase 06 — Security

## Threat Register

| Threat ID | Severity | Disposition | Status |
|-----------|----------|-------------|--------|
| T-06-01 | high | mitigate — `[MATH]`/postmortem: index + math detail only; no API keys/payloads (LOG-02) | closed |
| T-06-02 | high | mitigate — postmortem only on final failure; `--out` only on success | closed |
| T-06-03 | medium | mitigate — stdlib bounded heuristics; single RELY max_retries loop | closed |
| T-06-04 | low | accept — local postmortem path trusts operator filesystem | closed |
| T-06-05 | low | accept — no new auth surface | closed |
| T-06-SC | low | accept — no new pip packages (stdlib only) | closed |

## Evidence

- Dual-channel math errors: detailed `[MATH]` on stderr; minimal PT raise without secrets
- Postmortem written only on final batch failure; suite asserts no write on success
- Math `ValueError` reuses `generate_validated_batch` only (no second retry loop)
- `pytest exercise-ai -q` — 73 passed

## Sign-Off

- [x] `threats_open: 0`
- [x] `status: verified`
