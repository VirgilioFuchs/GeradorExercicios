---
phase: 12-local-embed-demo
plan: 02
subsystem: demo
tags: [stdlib, html, fetch, throwaway, anti-accretion, DEMO-01, DEMO-02]

requires:
  - phase: 12-local-embed-demo
    provides: Plan 01 tracer POST /gerar + guards + error_payload on [::1]:8642
provides:
  - Full operator UX (Contrato/Ambiente, Exercícios|JSON tabs, Gerando…, error badges)
  - Keep-last-success + HTTP 409 messaging (D-09..D-12)
  - Dismissible throwaway banner + persistent footnote (D-13, D-16)
  - demo/README anti-accretion pack + root Embed pointer (D-14, D-15)
  - Fail-closed UI/docs marker tests
affects: [12-local-embed-demo]

actuals:
  tokens: 4710
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns:
    - "static demo/index.html + demo/app.js served by Plan 01 ThreadingHTTPServer"
    - "fail-closed Path.read_text marker tests for UI/docs strings"
    - "sessionStorage banner dismiss; footnote always visible"

key-files:
  created:
    - demo/app.js
    - demo/README.md
    - demo/tests/test_ui_markers.py
    - demo/tests/test_docs_markers.py
  modified:
    - demo/index.html
    - README.md

key-decisions:
  - "Split chrome into index.html + app.js; schema hint uses English ExerciseBatch field names"
  - "Presets Matemática / equação do 1º grau / medio / 2; provider empty=auto; reasoning default medium"
  - "Banner dismiss via sessionStorage; docs use literal http://[::1]:8642/ only"

patterns-established:
  - "PT chrome / EN contract identifiers in demo UI"
  - "Marker tests keep DEMO-01/02 strings fail-closed without browser automation"

requirements-completed: [DEMO-01, DEMO-02]

coverage:
  - id: D1
    description: "Form + Exercícios|JSON tabs + schema hint + Gerando… busy (D-01..D-09)"
    requirement: DEMO-01
    verification:
      - kind: unit
        ref: "demo/tests/test_ui_markers.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "Error badges + HTTP 409 + keep-last-success client behavior (D-10..D-12)"
    requirement: DEMO-01
    verification:
      - kind: unit
        ref: "demo/tests/test_ui_markers.py::test_app_js_has_client_behavior_markers"
        status: pass
    human_judgment: false
  - id: D3
    description: "Throwaway banner/footnote + demo/README + root Embed anti-accretion (D-13..D-16)"
    requirement: DEMO-02
    verification:
      - kind: unit
        ref: "demo/tests/test_docs_markers.py"
        status: pass
    human_judgment: false
  - id: D4
    description: "Live UAT: presets → Gerando… → tabs; concurrent POST → HTTP 409; banner dismiss"
    requirement: DEMO-01
    verification: []
    human_judgment: true
    rationale: "Requires operator browser + optional live LLM keys; phase verify-work / manual UAT"

duration: 10min
completed: 2026-09-18
status: complete
---

# Phase 12 Plan 02: Local Embed Demo UX Summary

**Operator demo UX with Contrato/Ambiente form, Exercícios|JSON tabs, Gerando…/error badges, throwaway banner, and anti-accretion docs**

## Performance

- **Duration:** 10 min
- **Started:** 2026-09-18T13:57:00Z
- **Completed:** 2026-09-18T14:05:00Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Expanded tracer into full DEMO-01 UI: presets, Contrato vs Ambiente, tabbed results, schema hint, busy/error UX
- Client keeps last success on failure; HTTP 409 messages include literal `HTTP 409`
- Anti-accretion chrome/docs (banner, footnote, `demo/README.md`, root Embed pointer) with fail-closed marker tests

## Task Commits

Each task was committed atomically:

1. **Task 1: Ship form + tabs + busy/error UX (D-01..D-12)** - `62eadfd` (feat)
2. **Task 2: Throwaway banner, footnote, demo README, root Embed pointer (D-13..D-16)** - `1e0d98e` (docs)

**Plan metadata:** (this SUMMARY commit)

## Files Created/Modified

- `demo/index.html` — PT chrome: banner, Contrato/Ambiente, tabs, error region, footnote
- `demo/app.js` — fetch `/gerar`, tabs, Gerando…, badges, keep-last-success, sessionStorage dismiss
- `demo/README.md` — full anti-accretion pack (delete-at-close, `[::1]:8642`, netstat, no CI)
- `README.md` — Embed section short pointer to `demo/`
- `demo/tests/test_ui_markers.py` — fail-closed UI string assertions
- `demo/tests/test_docs_markers.py` — fail-closed docs string assertions

## Decisions Made

- Followed plan discretion: HTML+JS split; English schema hint; presets and wizard-parity provider/reasoning
- Banner dismiss uses `sessionStorage` for the session; footnote always visible
- Document only bracketed `http://[::1]:8642/` (no IPv4-first alias)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None for offline marker tests. Live UAT needs operator `.env` keys and `python demo/serve.py`.

## Next Phase Readiness

- Phase 12 plans 01–02 complete for DEMO-01/DEMO-02 deliverables
- Ready for phase verify / UAT (`http://[::1]:8642/`)
- CI untouched (`pytest exercise-ai -q` only); Plan 01 server/guards unchanged

## Self-Check: PASSED

- FOUND: `demo/index.html`, `demo/app.js`, `demo/README.md`, `README.md`, `demo/tests/test_ui_markers.py`, `demo/tests/test_docs_markers.py`
- FOUND commits: `62eadfd`, `1e0d98e`
- VERIFY: `pytest demo/tests -q` → 17 passed; `pytest exercise-ai -q` → 155 passed; CI has no `demo` job

---
*Phase: 12-local-embed-demo*
*Completed: 2026-09-18*
