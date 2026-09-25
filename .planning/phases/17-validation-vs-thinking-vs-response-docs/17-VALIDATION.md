---
phase: "17"
slug: "validation-vs-thinking-vs-response-docs"
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-25"
---

# Phase 17 — Validation Strategy

> Docs-only CONTRACT-02. D-12: no new pytest. Nyquist = existing smoke + manual checklist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing) |
| **Config file** | none project-wide |
| **Quick run command** | `python -m pytest exercise-ai/tests/test_skills_generation.py -q` |
| **Full suite command** | `python -m pytest exercise-ai -q` |
| **Estimated runtime** | ~1–5 seconds (smoke) |

---

## Sampling Rate

- **After every task commit:** `python -m pytest exercise-ai/tests/test_skills_generation.py -q`
- **After every plan wave:** same smoke (full suite optional)
- **Before `$gsd-verify-work`:** smoke green + manual CONTRACT-02 checklist below
- **Max feedback latency:** ~5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Requirement | Threat Ref | Automated Command | File Exists? | Notes |
|---------|------|-------------|------------|-------------------|--------------|-------|
| 17-01-T1 | 17-01 | CONTRACT-02 | T-17-01 | Path/heading asserts in PLAN Task 1 `<automated>` | ❌ Wave 0 create `TRIAD.md` | Manual checklist fills gaps |
| 17-01-T2 | 17-01 | CONTRACT-02 | T-17-02 | `TRIAD_DOC` import/path assert in PLAN Task 2 | ❌ after `rules.py` edit | |
| 17-01-T3 | 17-01 | CONTRACT-02 / D-12 | — | `python -m pytest exercise-ai/tests/test_skills_generation.py -q` | ✅ | Regression only; no new test file |

---

## Manual CONTRACT-02 checklist

- [ ] `TRIAD.md` at `exercise-ai/skills/generation/TRIAD.md`
- [ ] Sections: Validação / Pensamento / Resposta (PT-BR)
- [ ] Pipeline one-liner; points to `AGENTS.md`
- [ ] Callout: `reasoning_effort` ≠ `tipo_raciocinio`
- [ ] Pointers include: validator, math_check, verify_plan_echo/RELY, reasoning, Exercise
- [ ] “Fora desta fase” → Phase 18 never-do + authority map
- [ ] `TRIAD_DOC` in `rules.py`; TODO retargeted; no `__init__` / `persona.py` / `prompts.py` edits

---

## Wave 0 Gaps

- [ ] Create `TRIAD.md` (implementation — not a test file)
- [x] No new pytest scaffolding (D-12 by design)

*After Wave 0: set `wave_0_complete: true`.*

---

## Manual Verification (no automation)

| Behavior | Why Manual | How to Verify |
|----------|------------|---------------|
| Triad prose quality / PT-BR clarity | Subjective | Read TRIAD.md against CONTEXT D-05..D-08 |
| Pointer completeness to code | Docs | Manual checklist above |

---

*Template: gsd-core/templates/VALIDATION.md · seeded from 17-RESEARCH.md Validation Architecture*
