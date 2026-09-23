---
phase: 14-mixed-prompt-plan-adherence-demo-enablement
plan: 02
subsystem: ui
tags: [demo, plano, soft-warn, band-counts, GenerationRequest, DEMO-01]

requires:
  - phase: 14-mixed-prompt-plan-adherence-demo-enablement
    provides: slot prompts + verify_plan_echo in RELY (Plan 14-01)
  - phase: 13-request-schema-plan-contract
    provides: PlanoDificuldade / GenerationRequest.plano contract
provides:
  - Demo form with three band counts + soft-warn (non-blocking)
  - Client payload: mixed→plano; uniform→legacy dificuldade + band quantidade
  - demo/serve.py passes plano into GenerationRequest
affects:
  - 15-cli-wizard-ux

actuals:
  tokens: 2800
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns:
    - "soft-warn advisory only; server/Pydantic hard gate"
    - "plano only when mixed (2+ bands > 0); uniform keeps legacy shape"

key-files:
  created: []
  modified:
    - demo/index.html
    - demo/app.js
    - demo/serve.py
    - demo/tests/test_ui_markers.py
    - demo/tests/test_tracer_gerar.py

key-decisions:
  - "Defaults facil=0, medio=2, dificil=0, quantidade=2 per UI-SPEC"
  - "Zero-band POST allowed with soft-warn; editable quantidade only"
  - "serve omits default dificuldade=medio when absent so plano is not dropped"

patterns-established:
  - "DEMO: soft-warn surface (#fff8e1) distinct from .error-region (#a00)"
  - "DEMO: uniform quantidade prefers band count over editable field"

requirements-completed: [DEMO-01]

coverage:
  - id: D1
    description: Demo Contrato has three band count inputs and soft-warn; dificuldade select removed
    requirement: DEMO-01
    verification:
      - kind: unit
        ref: demo/tests/test_ui_markers.py#test_index_html_band_counts_and_soft_warn
        status: pass
    human_judgment: false
  - id: D2
    description: Client sends plano only when mixed; uniform uses dificuldade from sole band and band quantidade
    requirement: DEMO-01
    verification:
      - kind: unit
        ref: demo/tests/test_ui_markers.py#test_app_js_payload_rules_uniform_vs_mixed
        status: pass
    human_judgment: false
  - id: D3
    description: serve.py constructs GenerationRequest with plano; mixed POST tracer sees ordered facil/medio
    requirement: DEMO-01
    verification:
      - kind: integration
        ref: demo/tests/test_tracer_gerar.py#test_gerar_mixed_plano_passthrough
        status: pass
      - kind: integration
        ref: demo/tests/test_tracer_gerar.py#test_gerar_plano_qty_drift_returns_400
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-09-22
status: complete
---

# Phase 14 Plan 02: Demo band UX + plano passthrough Summary

**Throwaway demo authors mixed/uniform batches via three band counts with soft-warn, posting `plano` only when mixed; `serve.py` wires `plano` into `GenerationRequest`.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-09-22T09:50:00-03:00
- **Completed:** 2026-09-22T10:10:00-03:00
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Replaced single `dificuldade` select with `facil` / `medio` / `dificil` counts + editable `quantidade`
- Soft-warn (`#band-soft-warn`) for sum=0 / sum>40 / qty≠sum — advisory only, never blocks POST
- Client payload: mixed → `plano`; uniform → legacy `{dificuldade, quantidade}` with band-preferred qty
- `demo/serve.py` passes `plano` into `GenerationRequest` (D-15)
- Offline demo suite green (`pytest demo/tests -q` → 23 passed)

## Task Commits

1. **Task 1: Demo form band counts, soft-warn, uniform/mixed payload** - `bfecea2` (feat)
2. **Task 2: serve.py plano passthrough + mixed tracer tests** - `fe66620` (feat)

**Plan metadata:** (this SUMMARY commit)

## Files Created/Modified
- `demo/index.html` — band inputs, soft-warn CSS/region; dificuldade select removed
- `demo/app.js` — `updateSoftWarn` + `buildGerarPayload` (D-11..D-14)
- `demo/serve.py` — `plano` passthrough; no forced `dificuldade="medio"` when absent
- `demo/tests/test_ui_markers.py` — band / soft-warn / payload markers
- `demo/tests/test_tracer_gerar.py` — mixed plano tracer + qty-drift 400; Exercise echo fields

## Decisions Made
- Followed CONTEXT D-09..D-15 and UI-SPEC copy/colors exactly
- Did not touch exercise-ai RELY/prompts (Plan 14-01)
- Did not update STATE.md / ROADMAP.md (executor instruction)

## Deviations from Plan

None - plan executed exactly as written

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- DEMO-01 complete: mixed `plano` is live on the throwaway demo
- CLI/wizard compact plan UX remains Phase 15
- Ready for phase verify / next roadmap step

---
*Phase: 14-mixed-prompt-plan-adherence-demo-enablement*
*Completed: 2026-09-22*
