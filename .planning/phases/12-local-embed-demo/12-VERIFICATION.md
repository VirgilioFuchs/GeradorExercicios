---
phase: 12-local-embed-demo
verified: 2026-09-18T14:12:00Z
status: human_needed
score: 7/8 must-haves verified
behavior_unverified: 1
overrides_applied: 0
behavior_unverified_items:
  - truth: "Operator opens http://[::1]:8642/ and sees form → Gerando… → rendered Exercícios + contract JSON tabs, with live LLM and concurrent 409 in browser"
    test: "Run python demo/serve.py; open http://[::1]:8642/; submit presets; switch Exercícios|JSON; while first generate runs, fire second POST"
    expected: "Gerando… on submit; exercises + model_dump JSON after success; typed error badge on failure; second POST shows HTTP 409 sequential message; banner dismissible, footnote remains"
    why_human: "Needs live LLM keys, real browser paint, and concurrent timing — offline pytest mocks generate_batch and only asserts string markers"
human_verification:
  - test: "Live DEMO-01 happy path"
    expected: "Presets loaded; Gerar → Gerando… (submit disabled only); Exercícios render; JSON tab shows ExerciseBatch; error badge shows EN class + PT message + kind when forced"
    why_human: "Live LLM + browser; marker/tracer tests cannot prove paint or real generation"
  - test: "Live DEMO-02 concurrent 409"
    expected: "Second generation while first is in-flight returns HTTP 409 with literal HTTP 409 in the message"
    why_human: "Concurrency timing needs two overlapping requests against a real server"
  - test: "Banner dismiss + footnote / README anti-accretion glance"
    expected: "X hides banner for session; footnote stays; demo/README and root Embed match delete-at-close + http://[::1]:8642/"
    why_human: "Visual/session UX; docs markers already fail-closed in pytest"
---

# Phase 12: Local Embed Demo Verification Report

**Phase Goal:** Operator e time do host veem o fluxo de integração ponta a ponta numa demo local throwaway que consome o contrato da Phase 11.
**Verified:** 2026-09-18T14:12:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Operator opens `http://[::1]:8642/` and sees CLI-equivalent form, rendered exercises, raw contract JSON, **Gerando…**, and error by category (ROADMAP SC1 / DEMO-01) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | UI + client wired (`demo/index.html`, `demo/app.js`); marker tests pass; tracer E2E with mocked `generate_batch` passes. Live browser + LLM not exercised. |
| 2 | Server refuses non-loopback bind; busy Lock → HTTP 409; POST requires `application/json` + Host/Origin allowlist (ROADMAP SC2 / DEMO-02) | ✓ VERIFIED | `assert_loopback` / `check_post_headers` / `lock_busy_response` in `demo/guards.py`; wired in `demo/serve.py`; `test_guards.py` + `test_tracer_gerar.py` green |
| 3 | Throwaway banner + demo README expiry / delete-at-close (ROADMAP SC3 / DEMO-02) | ✓ VERIFIED | Banner + footnote in `demo/index.html`; full pack in `demo/README.md`; `test_docs_markers.py` + UI markers green |
| 4 | Offline `demo/tests` cover guards/error_map/tracer/UI/docs; demo not in CI | ✓ VERIFIED | `pytest demo/tests -q` → 17 passed; `.github/workflows/ci.yml` runs only `pytest exercise-ai -q` (no `demo`) |
| 5 | `load_dotenv` only under demo `__main__`; responses never render stderr or env secrets | ✓ VERIFIED | `load_dotenv` only in `serve.py` `if __name__ == "__main__"`; handler returns `model_dump` / `error_payload` only; no `import main` |
| 6 | Form: Contrato (`GenerationRequest`) vs Ambiente; tabs Exercícios \| JSON; schema hint before first success; Gerando… disables submit only (D-01..D-09) | ✓ VERIFIED | Markup + `app.js` behaviors present; `test_ui_markers.py` fail-closed |
| 7 | Errors: EN class badge + PT message + kind; client HTTP 409 text; keep-last-success on later failure (D-10..D-12) | ✓ VERIFIED | `error_map.error_payload` + UI `showError`; 409 path in server tests and client; `lastSuccessBatch` retained on error return paths in `app.js` |
| 8 | Root README Embed pointer to `demo/` + loopback URL + delete-at-close (D-15) | ✓ VERIFIED | `README.md` Embed section; `test_docs_markers.py` |

**Score:** 7/8 truths verified (1 present, behavior-unverified — live browser/LLM UAT)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `demo/guards.py` | loopback + headers + lock→409 | ✓ VERIFIED | Substantive; imported by serve + tests |
| `demo/error_map.py` | three-class `error_payload` | ✓ VERIFIED | ConfigError / InvalidRequestError / GenerationFailedError |
| `demo/serve.py` | AF_INET6 DemoServer + POST `/gerar` | ✓ VERIFIED | `address_family = socket.AF_INET6`; Lock; `generate_batch` |
| `demo/index.html` | PT chrome: banner, form, tabs, footnote | ✓ VERIFIED | Contrato, Ambiente, Exercícios, JSON, Gerando affordances |
| `demo/app.js` | fetch `/gerar`, tabs, busy, banner dismiss | ✓ VERIFIED | Wired from `index.html` script tag |
| `demo/README.md` | anti-accretion pack | ✓ VERIFIED | delete-at-close, `[::1]:8642`, netstat, no CI |
| `README.md` | Embed → demo pointer | ✓ VERIFIED | Short throwaway pointer |
| `demo/tests/*` | offline fail-closed coverage | ✓ VERIFIED | 5 test modules; 17 passed |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `demo/serve.py` do_POST `/gerar` | `service.generate_batch` | sys.path + env scope then call | ✓ WIRED | Lines ~182–188; mocked in `test_tracer_gerar.py` |
| `check_post_headers` | HTTP 403/415 | Host/Origin/Content-Type | ✓ WIRED | Unit + tracer 415 coverage |
| `_GEN_LOCK.acquire(blocking=False)` | HTTP 409 body | `lock_busy_response` / D-11 | ✓ WIRED | Message contains `HTTP 409` |
| `demo/app.js` fetch | POST `/gerar` | `application/json` body | ✓ WIRED | Contract fields + provider/reasoning |
| Error badge UI | `error.class` / `.message` / `.kind` | Plan 01 `error_payload` | ✓ WIRED | `showError` |
| Banner + footnote | `demo/README.md` expiry | D-13/D-14/D-16 | ✓ WIRED | Same delete-at-close / loopback language |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| Exercícios panel | `data.batch.exercicios` | `generate_batch` → JSON | Yes (live) / mocked in tests | ✓ FLOWING |
| JSON tab | `batch.model_dump()` | same | Yes | ✓ FLOWING |
| Error region | `error_payload(exc)` | service exceptions | Yes | ✓ FLOWING |
| Schema hint | `SCHEMA_HINT` literal | static until first success | Intentional empty-state | ✓ FLOWING (hint only) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Demo offline suite | `pytest demo/tests -q` | 17 passed in 11.76s | ✓ PASS |
| Package regression | `pytest exercise-ai -q` | 155 passed in 6.27s | ✓ PASS |
| AF_INET6 + `/gerar` | source read `demo/serve.py` | `AF_INET6`, path `/gerar`, `generate_batch` | ✓ PASS |
| Host/Origin 403, CT 415, Lock 409 | `test_guards` + tracer | assertions green | ✓ PASS |
| `load_dotenv` scope | `rg load_dotenv demo/` | only `__main__` in `serve.py` | ✓ PASS |
| Demo absent from CI | `rg demo .github/workflows` | no matches; CI = `pytest exercise-ai -q` | ✓ PASS |
| UI markers | Contrato, Ambiente, Exercícios, Gerando, tabs, banner | present in HTML/JS + marker tests | ✓ PASS |
| Live LLM browser UAT | — | not run | ? SKIP → human |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| — | — | No phase-declared `probe-*.sh` | SKIP |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| DEMO-01 | 12-01, 12-02 | Local page: form, exercises, JSON, Gerando…, errors by category | ? NEEDS HUMAN | Artifacts + markers + mocked tracer ✓; live UAT remaining |
| DEMO-02 | 12-01, 12-02 | Loopback refuse; Lock 409; JSON + Host/Origin; banner + README expiry | ✓ SATISFIED (automated) | Guards/tests/docs verified; concurrent browser 409 still listed for human glance |

No orphaned Phase 12 requirements.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| — | — | No TBD/FIXME/XXX in demo deliverables | — | — |
| — | — | No stub handlers / empty fetch | — | — |

### Source Assertions (requested)

| Check | Result |
| ----- | ------ |
| `AF_INET6` | ✓ `DemoServer.address_family = socket.AF_INET6` |
| `/gerar` | ✓ handler path + client `fetch("/gerar")` |
| Lock 409 | ✓ non-blocking acquire → `lock_busy_response()`; tests assert `HTTP 409` |
| Host/Origin | ✓ allowlist → 403 |
| Content-Type 415 | ✓ non-`application/json` → 415 |
| `load_dotenv` only in `__main__` | ✓ |
| No demo in CI | ✓ |

### Human Verification Required

#### 1. Live DEMO-01 happy path

**Test:** `python demo/serve.py` → open `http://[::1]:8642/` → submit presets → switch tabs  
**Expected:** Gerando…; Exercícios populated; JSON = contract dump; errors badge EN class + kind  
**Why human:** Live LLM + browser

#### 2. Live concurrent HTTP 409

**Test:** Overlap a second POST during an in-flight generate  
**Expected:** 409 + sequential message containing `HTTP 409`  
**Why human:** Timing; server path already unit-tested

#### 3. Banner dismiss / anti-accretion glance

**Test:** Dismiss banner; confirm footnote + README language  
**Expected:** Banner hidden for session; footnote + docs keep delete-at-close / `[::1]:8642`  
**Why human:** Session UX (docs markers already automated)

### Gaps Summary

No implementation gaps. Automated must-haves for DEMO-02 controls, docs, and offline tracer/UI markers are met. Phase status is **human_needed** solely because ROADMAP SC1 / DEMO-01 live browser+LLM acceptance (and optional concurrent 409 visual check) remain for the operator.

---

_Verified: 2026-09-18T14:12:00Z_
_Verifier: gsd-verifier (generic-agent workaround)_
