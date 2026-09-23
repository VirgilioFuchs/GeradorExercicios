# Phase 16: Domain skill index - Context

**Gathered:** 2026-09-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver the **API generation skill package skeleton** under `exercise-ai/skills/generation/`: public entrypoint for persona text that the generation pipeline will eventually consume. This phase does **not** wire `prompts.py`, does **not** fill real pedagogical rules, and does **not** create Cursor/Claude/Codex agent skills or `.cursor/rules` for this contract.

**Requirement:** CONTRACT-01 — reinterpreted by discuss as *API skill module index* (not GSD agent skill index).

</domain>

<decisions>
## Implementation Decisions

### Alvo do “skill”
- **D-01:** Skill is for the **API / runtime generation path** (persona used when creating exercises), **not** for GSD/agent tooling. — **Reversibility:** costly — undoing means reintroducing a parallel agent-facing contract and confusing two “skills” concepts.
- **D-02:** Do **not** create or extend agent folders (`.cursor`, `.claude`, `.codex`, etc.) for this milestone’s generation contract. — **Reversibility:** reversible for docs, but keep agent skill out of Phase 16 plans.

### Layout do pacote
- **D-03:** Package path: `exercise-ai/skills/generation/` with `__init__.py`, `persona.py`, and `rules.py`. — **Reversibility:** costly — renames touch imports once Phase 19 wires prompts.
- **D-04:** Phase 16 ships **skeleton + public export only**; `prompts.py` must **not** switch SYSTEM/USER to consume the skill yet (wiring belongs to later prompt phases).

### Conteúdo do esqueleto
- **D-05:** `persona.py` holds a **stub** persona (minimal placeholder string is OK).
- **D-06:** `rules.py` is **docstring / `pass` only**, plus a **TODO comment** listing future “nunca faça” items (LLM self-check, schema-in-prompt as format contract, etc.). Real rules content is for Phases 17–18.

### API pública
- **D-07:** Public surface: `get_persona_system() -> str` defined in `persona.py` and re-exported from `skills/generation/__init__.py`. No dataclass/`GenerationSkill` in this phase (YAGNI until rules have content). — **Reversibility:** reversible — user deferred final taste to verify-work; planner may note verify checkpoint.

### Idioma
- **D-08:** Skill texts and docstrings in **PT-BR**.

### Lista “nunca faça”
- **D-09:** Not implemented as data yet — only TODO bullets inside `rules.py` for later phases.

### Claude's Discretion
- Exact stub string wording for persona (as long as PT-BR and clearly a placeholder).
- Exact TODO bullet wording in `rules.py`.
- Whether `exercise-ai/skills/` needs a package-level `__init__.py` (yes if required for clean imports — implementer decides minimum that makes `from skills.generation import get_persona_system` work from package layout; respect how `exercise-ai` is run today — typically scripts with cwd/`sys.path` on `exercise-ai/`).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase / milestone
- `.planning/ROADMAP.md` — Phase 16 goal & success criteria (CONTRACT-01)
- `.planning/REQUIREMENTS.md` — CONTRACT-01
- `.planning/PROJECT.md` — v2.2 Contrato de geração; Active requirements
- `.planning/seeds/SEED-007-exercise-ai-persona-rules.md` — intent (persona/rules); **delivery vehicle overridden by D-01/D-02** (API package, not Cursor skill)
- `.planning/research/SUMMARY.md` — v2.2 research (stack: zero new deps; build order note — Phase 16 here is API skeleton, not Cursor skill)

### Patterns to mirror (structure only, not agent target)
- `skills/python-ai-engineering/SKILL.md` — *pattern reference for “index + pointed rules”*; do **not** copy into `.cursor` for this phase
- `exercise-ai/prompts.py` — future consumer; **do not modify in Phase 16** (D-04)

### Package context
- `exercise-ai/` — existing Python package layout (imports, tests under `exercise-ai/tests/`)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `exercise-ai/prompts.py` — `SYSTEM_PROMPT` / `build_prompts` will later import `get_persona_system()`; leave untouched now.
- Pytest under `exercise-ai/tests/` — optional smoke import test is in planner discretion if it helps CONTRACT-01 verification without expanding scope.

### Established Patterns
- Single-responsibility modules under `exercise-ai/` (no agent frameworks).
- PT-BR user-facing / domain strings already used in CLI/prompts.

### Integration Points
- Future: `prompts.py` ← `skills.generation.get_persona_system`
- Now: package must be importable when running from `exercise-ai` as today (same path conventions as other modules).

</code_context>

<specifics>
## Specific Ideas

- User wants a **dedicated folder** `exercise-ai/skills/{…}` for API skills that “montam” generation behavior.
- Subpackage `generation/` with persona vs rules split from day one, even if rules are empty.

</specifics>

<deferred>
## Deferred Ideas

- Cursor / `.cursor/rules` / GSD agent skill index (original SEED-007 slice A as agent-facing) — out of milestone delivery for agent folders; revisit only if product asks for agent tooling later.
- Filling `rules.py` with triad / authority / never-do content — Phases 17–18 (CONTRACT-02, CONTRACT-03) and related.
- Wiring persona into `SYSTEM_PROMPT` — Phase 19+ (PROMPT-02).
- Strip field-contract prose / slot preservation / hygiene / policy tests — Phases 20–25.
- Dataclass `GenerationSkill` — deferred until rules have real content (verify-work may revisit D-07).

</deferred>

---

*Phase: 16-Domain skill index*
*Context gathered: 2026-09-23*
