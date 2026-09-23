# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v2.1 — Lotes dinâmicos

**Shipped:** 2026-09-23  
**Phases:** 3 | **Plans:** 6 | **Tasks:** 8

### What Was Built
- Typed `GenerationRequest` with `plano`/`itens` XOR, qty invariants, difficulty echoes, CAP 40
- Slot prompts + `verify_plan_echo` in RELY; unique-band `dificuldades` (G-14-4)
- Demo band counts → mixed/uniform payloads; live UAT 4/4
- CLI `--plano` + wizard band UX via shared `plan_ux`

### What Worked
- Schema-first (13) before prompt/RELY (14) before CLI/wizard (15) — same contract everywhere
- Demo vertical slice in Phase 14 avoided dead schema
- Milestone audit sealed missing Phase 13 VERIFICATION before close

### What Was Inefficient
- REQUIREMENTS BATCH/CAP checkboxes left Pending after Phase 13 ship
- Phase 13 VERIFICATION.md missing until audit
- Branch still `gsd/ship-phase-03-*` through v2.1

### Patterns Established
- Mixed → `plano`; uniform → legacy `dificuldade`+`quantidade` (never always-send-plano)
- Plan echo owned by RELY after validate; not `validator.py`
- Shared `plan_ux` for argparse/wizard/demo payload parity

### Key Lessons
1. Seal VERIFICATION.md in execute-phase even when SUMMARY has coverage
2. Flip REQUIREMENTS checkboxes when phase SUMMARY lists `requirements-completed`
3. Acknowledge dormant seeds at close if promoting to next milestone (do not delete)

### Cost Observations
- Suite: **198** package tests offline; ~2 days (2026-09-21 → 09-23)
- Notable: quick tasks (GPT-6 models, per-model reasoning) archived with milestone

---

## Milestone: v1.1 — Qualidade do exercício

**Shipped:** 2026-09-09  
**Phases:** 3 | **Plans:** 3 | **Tasks:** 9

### What Was Built
- CLI argparse with PT flags, text stdout + required `--out` JSON (CLI-04)
- Bounded `generate_validated_batch` with retriable API edges and duration logs (RELY/ERR-05)
- Stdlib math checks (arithmetic + `ax+b=c`) into the same RELY loop (MATH-01/02)

### What Worked
- Tracer-first vertical slices per phase; Phase 5 hook reused cleanly by Phase 6
- Dual-channel error pattern (`[VALIDAÇÃO]` / `[MATH]` / `[API:*]`) stayed consistent
- Milestone audit + ship gate after verification kept closeout honest

### What Was Inefficient
- ROADMAP heading `## Future Themes (post v1.1)` truncated milestone window (fixed before archive)
- Phase 6 missing SECURITY.md blocked ship until added at PR time
- Branch still named `gsd/ship-phase-03-*` through phases 4–6

### Patterns Established
- Math failures must raise `ValueError` from `validate_exercise_batch` only — no second retry loop
- Uninterpretable math → pass + postmortem record (D-02)
- Ship requires `threats_open: 0` SECURITY.md when enforcement is on

### Key Lessons
1. Keep version tokens out of non-milestone ROADMAP headings (`v1.1` in “Future Themes” broke `milestone.complete`)
2. Create SECURITY.md during execute/verify, not at ship time
3. Prefer stdlib heuristics for MVP math; vendor only if research proves need

### Cost Observations
- Suite grew to 73 pytest cases with no live LLM
- Notable: research skipped for Phase 6 (config); VALIDATION.md optional gap accepted

---

## Milestone: v2.0 — Embed em Produção

**Shipped:** 2026-09-18  
**Phases:** 2 | **Plans:** 5 | **Tasks:** 12

### What Was Built
- Pure `service.generate_batch(request) -> ExerciseBatch` with `main.run` as CLI adapter
- Host-safe seam: 1–40 bounds, error subclasses/`kind`, always-on env restore, guarded flush
- cp1252-safe diagnostics, Gemini 30s timeout, README embed contract
- Stdlib demo on `[::1]:8642` with guards + full UI (form, tabs, Gerando…, errors)

### What Worked
- Pure seam move first (suite green) before env/`kind`/encoding hygiene
- Demo consumes contract only (no `main`); dotenv stays in demo `__main__`
- UAT closed the live gap after verification human_needed

### What Was Inefficient
- Phase 12 Nyquist VALIDATION left as draft (not reconciled)
- Packaging PKG-01 parked again — real host embed still blocked
- Branch name still `gsd/ship-phase-03-*` through v2.0

### Patterns Established
- Keep return type `-> ExerciseBatch`; host maps subclasses via `kind`
- Throwaway demo = stdlib ThreadingHTTPServer + Lock→409 + anti-accretion banner
- Milestone audit `passed` with accepted deferred PKG/OBS/LOG as next-milestone debt

### Key Lessons
1. Do not widen the embed return type in the same milestone as the seam extraction
2. Demo outside package/CI keeps product surface clean
3. Acknowledge dormant seeds at close so audit-open does not block archive

### Cost Observations
- Suite: 155 package + 17 demo tests, no live LLM
- Timeline: 2026-09-16 → 2026-09-18 (~3 days); ~57 files / +5525 LOC in milestone range

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Closeout | Notes |
|-----------|----------|-------|
| v1 | tech_debt accepted | Nyquist/SECURITY debt carried |
| v1.1 | verified_closeout | Audit passed 6/6; phases archived |
| v1.2 | override_closeout | Seeds SEED-001/003 acknowledged |
| v2.0 | override_closeout | Audit passed; SEED-005/006 acknowledged; phases archived by `milestone.complete` |
| v2.1 | override_closeout | Audit passed; SEED-007/008/009 acknowledged; phases+quick archived |

### Recurring Friction

- Planning artifact gates (SECURITY, ROADMAP headings, missing VERIFICATION) surface late at ship/complete
- Packaging rename keeps slipping; blocks real host embed
- Nyquist VALIDATION often left draft after execute
- Long-lived branch name `gsd/ship-phase-03-*` across milestones

---
*Updated after v2.1 archive — 2026-09-23*
