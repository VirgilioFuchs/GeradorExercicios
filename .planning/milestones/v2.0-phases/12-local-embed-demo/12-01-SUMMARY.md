---
phase: 12-local-embed-demo
plan: 01
subsystem: demo
tags: [stdlib, http.server, AF_INET6, generate_batch, Host-Origin, Lock-409]

requires:
  - phase: 11-service-layer-extraction
    provides: generate_batch + ConfigError/InvalidRequestError/GenerationFailedError embed seam
provides:
  - Offline demo guards (assert_loopback, check_post_headers, lock_busy_response)
  - error_payload mapping for three service exception classes (D-10)
  - AF_INET6 DemoServer POST /gerar → generate_batch under Lock
  - Minimal tracer index.html POSTing application/json to /gerar
affects: [12-local-embed-demo]

actuals:
  tokens: 5659
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "stdlib ThreadingHTTPServer + address_family=AF_INET6 for [::1]"
    - "pure guards/error_map importable without listen or dotenv"
    - "demo-local save/restore of LLM_PROVIDER + LLM_REASONING_EFFORT around generate_batch"
    - "load_dotenv only under demo/serve.py __main__"

key-files:
  created:
    - demo/guards.py
    - demo/error_map.py
    - demo/serve.py
    - demo/index.html
    - demo/tests/test_guards.py
    - demo/tests/test_error_map.py
    - demo/tests/test_tracer_gerar.py
  modified: []

key-decisions:
  - "POST path /gerar; Host/Origin 403; Content-Type mismatch 415; busy Lock 409 with literal HTTP 409 (D-11)"
  - "Service errors returned as HTTP 200 + {ok:false,error} via error_payload; header/busy use real status codes"
  - "Tracer UI is minimal form only — full tabs/banner/README deferred to Plan 02"

patterns-established:
  - "Wave 0 pure helpers under demo/ tested offline without CI"
  - "sys.path insert exercise-ai/; import service/models only — never main"

requirements-completed: [DEMO-01, DEMO-02]

coverage:
  - id: D1
    description: "Pure guards: loopback refuse, Host/Origin/Content-Type allowlist, lock→409 helper"
    requirement: DEMO-02
    verification:
      - kind: unit
        ref: "demo/tests/test_guards.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "error_payload maps ConfigError/InvalidRequestError/GenerationFailedError (api_error_kind→kind)"
    requirement: DEMO-01
    verification:
      - kind: unit
        ref: "demo/tests/test_error_map.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "Tracer POST /gerar → mocked generate_batch with guards, Lock 409, typed errors"
    requirement: DEMO-01
    verification:
      - kind: unit
        ref: "demo/tests/test_tracer_gerar.py"
        status: pass
    human_judgment: false
  - id: D4
    description: "Operator live form → Gerando… → Exercícios/JSON tabs on http://[::1]:8642/"
    requirement: DEMO-01
    verification: []
    human_judgment: true
    rationale: "Full UI chrome and live LLM UAT belong to Plan 02; tracer only ships minimal POST form"

duration: 15min
completed: 2026-09-18
status: complete
---

# Phase 12 Plan 01: Local Embed Demo Tracer Summary

**Stdlib AF_INET6 demo on [::1]:8642 with POST /gerar → generate_batch, Host/Origin/JSON guards, Lock→409, and offline Wave 0 tests**

## Performance

- **Duration:** 15 min
- **Started:** 2026-09-18T13:45:14Z
- **Completed:** 2026-09-18T14:00:00Z
- **Tasks:** 2
- **Files modified:** 7 created

## Accomplishments

- Wave 0 pure `guards.py` / `error_map.py` with offline pytest (not in CI)
- Tracer `DemoServer` (ThreadingHTTPServer + AF_INET6) wiring POST `/gerar` to `service.generate_batch` under non-blocking Lock
- Minimal `index.html` form POSTing `application/json` to `/gerar` for embed-seam proof before Plan 02 chrome

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: Wave 0 failing tests** - `53a4d71` (test)
2. **Task 1 GREEN: guards + error_map** - `375f201` (feat)
3. **Task 2: tracer serve + index + tests** - `ce3c7bb` (feat)

**Plan metadata:** (this SUMMARY commit)

## Files Created/Modified

- `demo/guards.py` — `assert_loopback`, `check_post_headers`, `lock_busy_response`
- `demo/error_map.py` — `error_payload` for three service exception classes (D-10)
- `demo/serve.py` — AF_INET6 server; POST `/gerar`; dotenv only in `__main__`
- `demo/index.html` — minimal tracer form (GenerationRequest + provider/reasoning)
- `demo/tests/test_guards.py` — refuse non-loopback; headers; lock→409
- `demo/tests/test_error_map.py` — three-class error JSON shape
- `demo/tests/test_tracer_gerar.py` — mocked E2E success, ConfigError, 409, 415, GET without lock

## Decisions Made

- Followed plan discretion locks: `/gerar`, 403 Host/Origin, 415 Content-Type, 409 with literal `HTTP 409`
- Service exceptions mapped to `{ok:false,error}` at HTTP 200 so the client can badge by class/kind; protocol errors keep real status codes
- Tracer UI intentionally minimal — Plan 02 owns tabs/banner/README (D-01..D-16 chrome)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required for this plan (live UAT later needs operator `.env` keys).

## Next Phase Readiness

- Ready for Plan 02 UI/docs expansion (tabs Exercícios|JSON, banner/footnote, `demo/README.md`, root README pointer)
- Offline `pytest demo/tests -q` green; `pytest exercise-ai -q` unchanged and green; CI not modified

## Self-Check: PASSED

- FOUND: `demo/guards.py`, `demo/error_map.py`, `demo/serve.py`, `demo/index.html`, `demo/tests/test_guards.py`, `demo/tests/test_error_map.py`, `demo/tests/test_tracer_gerar.py`
- FOUND commits: `53a4d71`, `375f201`, `ce3c7bb`
- VERIFY: `pytest demo/tests -q` → 12 passed; `pytest exercise-ai -q` → 155 passed; `load_dotenv` only under `serve.py` `__main__`; CI workflow untouched

---
*Phase: 12-local-embed-demo*
*Completed: 2026-09-18*
