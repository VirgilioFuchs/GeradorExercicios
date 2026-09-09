# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

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

## Cross-Milestone Trends

### Process Evolution

| Milestone | Closeout | Notes |
|-----------|----------|-------|
| v1 | tech_debt accepted | Nyquist/SECURITY debt carried |
| v1.1 | verified_closeout | Audit passed 6/6; phases archived |

### Recurring Friction

- Planning artifact gates (SECURITY, ROADMAP headings) surface late at ship/complete

---
*Updated after v1.1 archive — 2026-09-09*
