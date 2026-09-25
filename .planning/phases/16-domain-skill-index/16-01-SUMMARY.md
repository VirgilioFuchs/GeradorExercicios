---
phase: 16-domain-skill-index
plan: 01
subsystem: api
tags: [skills, persona, generation, pydantic-adjacent, offline-test]

requires:
  - phase: prior exercise-ai layout
    provides: sys.path convention via conftest (exercise-ai/ on path) and token_usage re-export pattern
provides:
  - Importable skills.generation package with get_persona_system() -> str
  - rules.py skeleton with TODO never-do bullets for Phases 17–18
  - Offline smoke test locking CONTRACT-01 public API
affects:
  - 17-18 rules content
  - 19+ prompts wiring (get_persona_system consumer)

actuals:
  tokens: 354
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "API skill package under exercise-ai/skills/generation/ (not agent SKILL.md)"
    - "token_usage-style __init__ re-export + __all__ for public get_*"

key-files:
  created:
    - exercise-ai/skills/__init__.py
    - exercise-ai/skills/generation/__init__.py
    - exercise-ai/skills/generation/persona.py
    - exercise-ai/skills/generation/rules.py
    - exercise-ai/tests/test_skills_generation.py
  modified: []

key-decisions:
  - "D-01/D-02: Skill is API/runtime package, not Cursor/Claude/Codex agent skill"
  - "D-07: Public surface is get_persona_system() only; no GenerationSkill dataclass"
  - "D-06/D-09: rules.py is docstring + pass + TODO never-do bullets only"

patterns-established:
  - "skills.generation mirrors token_usage absolute imports from exercise-ai on sys.path"
  - "Parent skills/__init__.py is minimal package marker; re-exports live only on generation/"

requirements-completed: [CONTRACT-01]

coverage:
  - id: D1
    description: "Importable get_persona_system from skills.generation returns nonempty str"
    requirement: CONTRACT-01
    verification:
      - kind: unit
        ref: "exercise-ai/tests/test_skills_generation.py#test_get_persona_system_returns_nonempty_str"
        status: pass
      - kind: other
        ref: "python -c import skills.generation.get_persona_system assert nonempty str"
        status: pass
    human_judgment: false
  - id: D2
    description: "Package tree exercise-ai/skills/generation/ with persona.py and rules.py stub"
    requirement: CONTRACT-01
    verification:
      - kind: other
        ref: "path checks + rules.py TODO/pass markers via python -c"
        status: pass
    human_judgment: false

duration: 5 min
completed: 2026-09-25
status: complete
---

# Phase 16 Plan 01: Domain skill index Summary

**API generation skill package under `exercise-ai/skills/generation/` with public `get_persona_system()` stub and empty `rules.py` shell — CONTRACT-01 as API/runtime index, not an agent skill.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-09-25T13:00:00Z
- **Completed:** 2026-09-25T13:05:00Z
- **Tasks:** 3/3
- **Files:** 5 created

## Accomplishments

- Created `exercise-ai/skills/` + `generation/` package with PT-BR stub persona and re-export mirror of `token_usage`
- Added `rules.py` skeleton with TODO nunca-faça bullets (LLM self-check, schema-in-prompt, prompts wiring deferral)
- Locked offline smoke: `test_get_persona_system_returns_nonempty_str`

## Task Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Tracer: skills.generation + get_persona_system | 3b1f081 | `skills/__init__.py`, `generation/__init__.py`, `persona.py` |
| 2 | Expansion: rules.py stub + TODO nunca-faça | 344e112 | `generation/rules.py` |
| 3 | Smoke test: offline import | 8726385 | `tests/test_skills_generation.py` |

## Deviations from Plan

None - plan executed exactly as written.

## TDD Gate Compliance

Task 3 is `tdd="true"` but tests the public API delivered by Tasks 1–2 in the same plan. RED was not a separate failing commit — the smoke test passed on first run against the already-committed stub (expected for post-tracer smoke).

## Known Stubs

| File | Line | Stub | Reason |
|------|------|------|--------|
| `exercise-ai/skills/generation/persona.py` | get_persona_system return | PT-BR PLACEHOLDER persona string | D-05 intentional; real persona later |
| `exercise-ai/skills/generation/rules.py` | module body | `pass` + TODO nunca-faça only | D-06/D-09; real rules Phases 17–18 |

## Authentication Gates

None.

## Verification Results

- Import smoke: **PASS** (exit 0)
- `pytest exercise-ai/tests/test_skills_generation.py -q`: **PASS** (`1 passed`)
- Files present: **PASS** (`skills/{__init__,generation/{__init__,persona,rules}}`)
- `prompts.py` unmodified; no `.cursor`/`.claude`/`.codex` skill created for this contract: **PASS**

## Next

Ready for next plan in Phase 16 (or phase verify/transition via orchestrator — `--no-transition`).

## Self-Check: PASSED

- FOUND: exercise-ai/skills/__init__.py
- FOUND: exercise-ai/skills/generation/__init__.py
- FOUND: exercise-ai/skills/generation/persona.py
- FOUND: exercise-ai/skills/generation/rules.py
- FOUND: exercise-ai/tests/test_skills_generation.py
- FOUND: commits 3b1f081, 344e112, 8726385
