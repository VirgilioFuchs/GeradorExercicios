---
phase: "04"
slug: "cli-argparse"
status: verified
threats_open: 0
asvs_level: 1
created: "2026-09-08"
---

# Phase 04 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| argv → argparse | Untrusted CLI strings cross into `GenerationRequest` / `--out` path | Flag values, file path |
| process → `--out` filesystem | Write path chosen by operator; must write only validated batch JSON | `ExerciseBatch.model_dump()` |
| env → process | API keys via `.env`; CLI must not print values | `LLM_API_KEY`, `GEMINI_API_KEY` |
| stderr → developer | Stage labels + LOG-01 + D-11 messages | Params without secrets; env **names** only |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-04-01 | Information Disclosure | argparse / LOG-01 / help / D-11 | high | mitigate | Never log/print key **values**; LOG-01 params only; D-11 names env vars; `test_main` + `test_logging_security` assert absence | closed |
| T-04-02 | Tampering | `--out` file write | high | mitigate | Write only `validated_batch.model_dump()` JSON UTF-8; no sidecar dumps | closed |
| T-04-03 | Information Disclosure | stderr user errors | medium | mitigate | Plain PT errors; reuse LOG-02 redaction from generators | closed |
| T-04-04 | Elevation of Privilege | CLI `--out` path | low | accept | Local CLI trusts operator for path (same as running Python); no new network exposure | closed |
| T-04-SC | Tampering | pip installs | low | accept | No new packages; argparse is stdlib | closed |

### Verification evidence (ASVS L1)

| Threat ID | Evidence |
|-----------|----------|
| T-04-01 | `main.py` LOG-01 + `_ensure_provider_key`; `test_main.py` key-absence asserts; `test_run_failure_logs_omit_key_values` |
| T-04-02 | `main.run` → `Path.write_text(json.dumps(validated_batch.model_dump()…))`; dual-output tests |
| T-04-03 | Plain `print(str(err), file=sys.stderr)`; existing mapper redaction unchanged |
| T-04-04 | Accepted — local operator trust |
| T-04-SC | Accepted — no new deps |

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-04-04 | T-04-04 | Operator-chosen `--out` path is intentional local CLI trust | phase plan | 2026-09-08 |
| AR-04-SC | T-04-SC | No new pip packages in Phase 04 | phase plan | 2026-09-08 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-08 | 5 | 5 | 0 | gsd-verify-work / secure-phase (inline) |

---

## Sign-Off

- [x] All threats have a disposition
- [x] Accepted risks documented
- [x] `threats_open: 0`
- [x] `status: verified`
