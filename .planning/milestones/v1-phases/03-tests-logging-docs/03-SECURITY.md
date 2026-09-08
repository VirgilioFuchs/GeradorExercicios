---
phase: "03"
slug: "tests-logging-docs"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-04"
---

# Phase 03 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| env → process | API keys enter via `.env` / environment; must never cross into stdout JSON or durable logs | `LLM_API_KEY`, `GEMINI_API_KEY` (secret) |
| LLM provider → generators | Untrusted exception bodies / response text may embed key fragments | Provider `exc` bodies, refusal/response text |
| CLI stderr → developer | Detail logs (`[API:*]`, `[VALIDAÇÃO]`, LOG-01) are trusted for ops but must not contain secrets | Sanitized type/status + request params |
| test suite → network | Tests must stay offline (mocks/static only) | Fixture data only; no live LLM traffic |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-03-01 | Information Disclosure | `map_openai_error` / `map_gemini_error` `[API:*]` lines | high | mitigate | `_openai_error_detail` / `_gemini_error_detail` log type + status/code only (no raw `str(exc)`); `_redact_env_secrets` on refusal/unparseable dumps; `test_logging_security.py` anti-leakage | closed |
| T-03-02 | Information Disclosure | LOG-01 parameter / failure logs in `main.py` | medium | mitigate | `logger.info` emits `materia`/`topico`/`dificuldade`/`quantidade` only; never env key values; `test_main.py` asserts `LLM_API_KEY=` / `GEMINI_API_KEY=` absent from stderr | closed |
| T-03-03 | Information Disclosure | README / docs | low | mitigate | Root `README.md` documents var names and format hints only; no sample secret values | closed |
| T-03-04 | Tampering | pytest suite vs live API | medium | mitigate | Suite uses mocks/static factories only (`TEST-01`); no network in `pytest exercise-ai -q` | closed |
| T-03-SC | Tampering | pip installs | low | accept | No new packages this phase; `pytest` already in `requirements.txt` | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on (`high`) count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

### Verification evidence (ASVS L1)

| Threat ID | Evidence |
|-----------|----------|
| T-03-01 | `exercise-ai/generator.py` (`_openai_error_detail`, `map_openai_error`, `_redact_env_secrets`); `exercise-ai/generator_gemini.py` (mirror); `exercise-ai/tests/test_logging_security.py` |
| T-03-02 | `exercise-ai/main.py` (`_configure_logging`, LOG-01 `logger.info`/`logger.error`); `exercise-ai/tests/test_main.py` |
| T-03-03 | `README.md` — env table lists names/`sk-...`/`AIza...` format hints only |
| T-03-04 | `exercise-ai/tests/*` — MagicMock/`monkeypatch`/factories; SUMMARY coverage D1–D4 pass |
| T-03-SC | Accepted — see Accepted Risks Log |

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-03-SC | T-03-SC | No new pip packages in Phase 03; supply-chain surface unchanged from prior `requirements.txt` | phase plan (disposition: accept) | 2026-09-04 |
| AR-02-WR03 | WR-03 (Phase 02 review) | Empty-choices edge case deferred by `03-CONTEXT.md`; out of Phase 03 scope — residual accepted deferral, not an open Phase 03 threat | CONTEXT deferred / secure-phase auto | 2026-09-04 |
| AR-02-WR04 | WR-04 (Phase 02 review) | Gemini transport edge case deferred by `03-CONTEXT.md`; out of Phase 03 scope — residual accepted deferral, not an open Phase 03 threat | CONTEXT deferred / secure-phase auto | 2026-09-04 |

*Accepted risks do not resurface in future audit runs.*
*WR-03/WR-04 are residual deferred risks from Phase 02; they are not OPEN entries in this phase register and do not increment `threats_open`.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-04 | 5 | 5 | 0 | gsd-secure-phase (auto) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-04
