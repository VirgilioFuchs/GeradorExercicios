---
gsd_state_version: 1.0
milestone: v2.2
milestone_name: Contrato de geração
current_phase: 16
current_phase_name: Domain skill index
status: phase_complete
stopped_at: Completed 16-01-PLAN.md
last_updated: "2026-09-25T13:04:19.750Z"
last_activity: 2026-09-25
last_activity_desc: Completed 16-01 — skills.generation skeleton + smoke test
state_head: 95c4fd5
progress:
  total_phases: 10
  completed_phases: 0
  total_plans: 1
  completed_plans: 1
  percent: 10
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-23)

**Core value:** Gerar exercícios de matemática confiáveis e estruturados (incluindo lotes mistos) com validação e adesão ao plano — também via `service.generate_batch`
**Current focus:** v2.2 Phase 16 — Domain skill index (16-01 complete; await verify/transition)

## Current Position

Phase: 16 (Domain skill index) — PLAN 01 COMPLETE
Plan: 01 / 01
Status: Completed 16-01-PLAN.md (orchestrator: verify / transition)
Last activity: 2026-09-25 — API skills package skeleton + get_persona_system smoke

## Performance Metrics

**Velocity:**

- Total plans completed (v2.0): 3
- Average duration: 9 min
- Total execution time: 26 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 11. Service Layer Extraction | 3/3 | 26 min | 9 min |
| 12. Local Embed Demo | 0 | — | — |
| 11 | 3 | - | - |
| 12 | 2 | - | - |
| 14 | 3 | - | - |

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 11 P01 | 6 min | 2 tasks | 7 files |
| Phase 11 P02 | 14 min | 3 tasks | 11 files |
| Phase 11 P03 | 6 min | 3 tasks | 8 files |
| Phase 16 P01 | 5 min | 3 tasks | 5 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- v2.0: Keep `generate_batch(...) -> ExerciseBatch` (do not widen return type)
- v2.0: Packaging (PKG-01) parked — lead item of next milestone
- v2.0: Print→logging deferred as known debt; host uses `redirect_stderr`
- v2.0: Demo = ThreadingHTTPServer + Lock → 409, `[::1]:8642`, stdlib only
- v2.0: Encoding harden + Gemini timeout are Phase 11 in-scope
- v2.0: Pure seam move first, then env/`kind`/hygiene
- [Phase 11]: Pure move only: generate_batch(request) with env bridge for CLI max_retries
- [Phase 11]: begin_run/flush live in service; run retains finally flush as safety net
- [Phase 11]: Error classes in service.py; leaf modules lazy-import to avoid cycles
- [Phase 11]: Validation exhaustion raises InvalidRequestError(kind=validation_exhausted)
- [Phase 11]: Postmortem CLI-owned; flush OSError-guarded; always-on scoped env restore
- [Phase 11]: Gemini HttpOptions.timeout=30000 ms (Context7 python-genai) — SDK timeout field is milliseconds; align magnitude to OpenAI 30s
- [Phase 11]: README Embed contract only; reserved names detection-only — D-12; no CONTRACT.md; packaging parked PKG-01
- [Phase 16]: API skill under exercise-ai/skills/generation; not agent skill folders (D-01/D-02)
- [Phase 16]: Public API is get_persona_system() only; rules.py stub deferred to 17-18 (D-06/D-07/D-09)

### Pending Todos

None yet.

### Blockers/Concerns

- First real host integration cannot succeed without unparking PKG-01 after v2.0
- Token NDJSON flush: Plan 11-02 uses guarded `OSError` no-op (D-07); no new env root this phase

## Deferred Items

Items acknowledged and deferred at milestone close, most recent first:

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| seeds | SEED-007-exercise-ai-persona-rules | dormant | 2026-09-23 | v2.1 |
| seeds | SEED-008-response-structure-over-prompt | dormant | 2026-09-23 | v2.1 |
| seeds | SEED-009-math-check-bncc-aligned | dormant | 2026-09-23 | v2.1 |
| Packaging | PKG-01 pyproject + rename `exercise_ai/` | Lead of next milestone | 2026-09-16 | v2.0 |
| Observability | OBS-01 usage/cost alongside batch | Next embed-hardening | 2026-09-16 | v2.0 |
| Logging | LOG-01 print→logging (~33 sites) | Known debt | 2026-09-16 | v2.0 |
| Seeds | SEED-005-usable-postmortem (dormant) | acknowledged at close | 2026-09-18 | v2.0 |
| Seeds | SEED-006-dynamic-batch-per-exercise | Promoted → v2.1 | 2026-09-21 | v2.1 |
| Seeds | SEED-001 BNCC (dormant) | Acknowledged at v1.2 close | 2026-09-15 | v1.2 |
| Seeds | SEED-003 B/C images / storytelling | After embed | 2026-09-16 | v2.0 |
| Ops | Nyquist VALIDATION gaps (phases 8–10) | Accepted tech debt | 2026-09-15 | v1.2 |
| Product | MySQL / analytics / personalização / agente | Deferred | 2026-09-04 | v2+ |

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|

## Session Continuity

Last session: 2026-09-25T13:04:19.716Z
Stopped at: Completed 16-01-PLAN.md
Resume file: None

## Operator Next Steps

- Orchestrator: verify Phase 16 / transition (`--no-transition` was set on executor)
- Next milestone phases: rules content (17–18), then prompts wiring (19+)
