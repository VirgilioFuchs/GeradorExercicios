---
gsd_state_version: 1.0
milestone: v2.1
milestone_name: Lotes dinâmicos
current_phase: 14
current_phase_name: Mixed prompt + plan-adherence + demo enablement
status: ready_to_discuss
stopped_at: Phase 14 executed — verification human_needed (live demo UAT)
last_updated: "2026-09-22T13:03:41.530Z"
last_activity: 2026-09-22
last_activity_desc: Resumed; Phase 13 complete — next discuss Phase 14
state_head: 65833eeff1db70edb09859e3cff429bcf2179414
progress:
  total_phases: 3
  completed_phases: 0
  total_plans: 3
  completed_plans: 3
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-21)

**Core value:** Gerar exercícios de matemática confiáveis e estruturados com validação de formato — agora também como biblioteca embutível
**Current focus:** v2.1 Phase 14 — Mixed prompt + plan-adherence + demo enablement

## Current Position

Phase: 14 (Mixed prompt + plan-adherence + demo enablement) — READY TO EXECUTE
Plan: —
Status: Ready to discuss Phase 14
Last activity: 2026-09-22 — Session resumed (Phase 13 shipped)

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

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 11 P01 | 6 min | 2 tasks | 7 files |
| Phase 11 P02 | 14 min | 3 tasks | 11 files |
| Phase 11 P03 | 6 min | 3 tasks | 8 files |

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

### Pending Todos

None yet.

### Blockers/Concerns

- First real host integration cannot succeed without unparking PKG-01 after v2.0
- Token NDJSON flush: Plan 11-02 uses guarded `OSError` no-op (D-07); no new env root this phase

## Deferred Items

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| Packaging | PKG-01 pyproject + rename `exercise_ai/` | Lead of next milestone | 2026-09-16 | v2.0 |
| Observability | OBS-01 usage/cost alongside batch | Next embed-hardening | 2026-09-16 | v2.0 |
| Logging | LOG-01 print→logging (~33 sites) | Known debt | 2026-09-16 | v2.0 |
| Seeds | SEED-005-usable-postmortem (dormant) | acknowledged at close | 2026-09-18 | v2.0 |
| Seeds | SEED-006-dynamic-batch-per-exercise | Promoted → v2.1 | 2026-09-21 | v2.1 |
| Seeds | SEED-007-exercise-ai-persona-rules (dormant) | planted | 2026-09-21 | v2.1 |
| Seeds | SEED-008-response-structure-over-prompt (dormant) | planted | 2026-09-22 | v2.1 |
| Seeds | SEED-001 BNCC (dormant) | Acknowledged at v1.2 close | 2026-09-15 | v1.2 |
| Seeds | SEED-003 B/C images / storytelling | After embed | 2026-09-16 | v2.0 |
| Ops | Nyquist VALIDATION gaps (phases 8–10) | Accepted tech debt | 2026-09-15 | v1.2 |
| Product | MySQL / analytics / personalização / agente | Deferred | 2026-09-04 | v2+ |

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 1 | wizard: matéria before tipo de exercício | 2026-09-16 | 80072d4 | — |
| 2 | model catalogs GPT/Gemini/Grok from Modelos.txt + capacity fallbacks | 2026-09-21 | 961fc2e | 260921-d9y-add-gpt-gemini-grok-model-catalogs-from- |
| 3 | demo model picker from model_catalog | 2026-09-21 | f9fbbbc | 260921-dsv-demo-select-model-from-model-catalog-lis |

## Session Continuity

Last session: 2026-09-22T13:03:41.205Z
Stopped at: Phase 14 executed — verification human_needed (live demo UAT)
Resume file: .planning/phases/14-mixed-prompt-plan-adherence-demo-enablement/14-VERIFICATION.md

## Operator Next Steps

- `$gsd-discuss-phase 14` (PROMPT-01, VAL-01/02, DEMO-01) — then plan/execute
