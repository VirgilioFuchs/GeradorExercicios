# Phase 17: Validation vs thinking vs response docs - Context

**Gathered:** 2026-09-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Document the **generation triad** so runtime readers (and later planners) do not invent prompt-side validation or confuse API thinking with response fields:

1. **Validation** = deterministic code only (`validator`, `math_check`, `verify_plan_echo`, RELY)
2. **Thinking** = run-level API `reasoning_effort` (via `reasoning.py`) — not an `Exercise` field and not pedagogy
3. **Response** = Structured Outputs `Exercise` fields only

**Requirement:** CONTRACT-02

**In scope:** Authoritative `TRIAD.md` under `exercise-ai/skills/generation/`, thin pointer from `rules.py`, short out-of-scope note toward Phase 18.

**Out of scope this phase:** Wiring `prompts.py`; filling detailed never-do catalog; authority map (CONTRACT-03 / Phase 18); loaders for external rule files; new pytest policy suite; agent-folder skills; changing `persona.py`.

</domain>

<decisions>
## Implementation Decisions

### Onde mora a tríade
- **D-01:** Ship both `rules.py` and `TRIAD.md` under `exercise-ai/skills/generation/`. — **Reversibility:** costly — path becomes the documented home for CONTRACT-02.
- **D-02:** `TRIAD.md` is **authoritative**; `rules.py` summarizes and points to it (if they diverge, fix to match TRIAD.md). — **Reversibility:** costly — establishes doc-over-code for this contract text.
- **D-03:** `rules.py` exposes `TRIAD_DOC = Path(__file__).with_name("TRIAD.md")` plus a docstring that directs readers to that file.
- **D-04:** Filename is `TRIAD.md` (English technical name).

### Profundidade do texto
- **D-05:** `TRIAD.md` = short section per leg (validation / thinking / response) **plus code-path pointers** (e.g. `validator.py`, `math_check.py`, plan-echo / RELY, `reasoning.py`, `models.Exercise`) — not a long FAQ/examples guide.
- **D-06:** Body language **PT-BR**; technical identifiers remain English (`reasoning_effort`, `Exercise`, module paths).
- **D-07:** Explicit **callout**: `reasoning_effort` is a run-level API knob — **not** pedagogical `tipo_raciocinio` (out of v2.2 product scope).
- **D-08:** Include **one-line pipeline** `prompt → LLM → validate → math_check → verify_plan_echo → RELY` and point at `AGENTS.md` / project constraints.

### Público-alvo
- **D-09:** Audience is **runtime / API package** readers (lab/host developers consuming `skills.generation`) — **not** a GSD/Cursor agent skill. — Carries Phase 16 D-01/D-02.
- **D-10:** Do **not** re-export `TRIAD_DOC` from `skills.generation.__init__` — keep `__all__` as `get_persona_system` only.
- **D-11:** Do **not** modify `persona.py` in Phase 17.
- **D-12:** No new offline pytest for TRIAD this phase — policy/offline tests remain Phases 24–25.

### Nunca faça / fora de escopo
- **D-13:** Phase 17 delivers **triad docs only**; detailed never-do list content waits for Phase 18 (with authority map / CONTRACT-03).
- **D-14:** Keep existing `# TODO` never-do bullets in `rules.py`, retargeted: never-do → Phase 18; triad → `TRIAD.md` / `TRIAD_DOC`.
- **D-15:** `TRIAD.md` includes a short **“Fora desta fase”** block (2–3 lines) pointing never-do detail + authority map to Phase 18.

### Claude's Discretion
- Exact PT-BR wording of triad sections and callout (must match D-05–D-08 substance).
- Exact set of code paths listed as pointers (must cover validation vs thinking vs response legs).
- Exact TODO comment rewording in `rules.py` while preserving foreshadow bullets.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase / milestone
- `.planning/ROADMAP.md` — Phase 17 goal & success criteria (CONTRACT-02)
- `.planning/REQUIREMENTS.md` — CONTRACT-02
- `.planning/PROJECT.md` — v2.2 Contrato de geração; Active requirements
- `.planning/seeds/SEED-007-exercise-ai-persona-rules.md` — triad intent (validation / thinking / response)
- `.planning/research/SUMMARY.md` — v2.2 research summary
- `.planning/research/PITFALLS.md` — self-check / thinking≠pedagogy pitfalls
- `.planning/research/ARCHITECTURE.md` — pipeline layers (prefer API package path from Phase 16 over any `.cursor/rules` wording still in research)

### Prior phase lock-in
- `.planning/phases/16-domain-skill-index/16-CONTEXT.md` — D-01..D-09 (API skill path; `rules.py` stub; no agent folders; no prompts wiring)
- `exercise-ai/skills/generation/rules.py` — current TODO stub to retarget
- `exercise-ai/skills/generation/persona.py` — do not modify (D-11)

### Code pointers for TRIAD.md content
- `AGENTS.md` — pipeline / LLM-not-source-of-truth constraints
- `exercise-ai/validator.py` — structural validation
- `exercise-ai/math_check.py` — math validation
- `exercise-ai/reliability.py` — RELY / plan-echo path (as applicable)
- `exercise-ai/reasoning.py` — `reasoning_effort` resolution
- `exercise-ai/models.py` — `Exercise` / Structured Outputs fields
- `exercise-ai/prompts.py` — future consumer; **do not modify in Phase 17**

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `exercise-ai/skills/generation/` package from Phase 16 — add `TRIAD.md`, update `rules.py` only.
- `token_usage` / package layout patterns already established under `exercise-ai/`.

### Established Patterns
- PT-BR domain docs + English identifiers (Phase 16 D-08).
- Public API kept narrow (`get_persona_system` only until needed).

### Integration Points
- Later: Phase 18 fills never-do / authority; Phase 19 wires persona into prompts; Phases 24–25 offline policy tests may assert triad text exists.

</code_context>

<specifics>
## Specific Ideas

- User wants a **future** architecture where specific rules can live in `.md` / `.yaml` / `.json` and be pointed/loaded — **explicitly deferred** (not stubbed in Phase 17).
- Prefer doc-as-source-of-truth for the triad (`TRIAD.md` wins over `rules.py` prose).

</specifics>

<deferred>
## Deferred Ideas

- **DEF-01:** Future rules-file architecture (load specific rules from `.md`/`.yaml`/`.json` via pointers) — not Phase 17.
- Detailed **nunca faça** catalog — Phase 18 (CONTRACT-03 / authority map companions).
- Authority map format → schema · plan → echo · content → prompts — Phase 18.
- Prompt persona wiring — Phase 19+.
- Offline policy tests asserting triad/never-do — Phases 24–25.
- Re-exporting `TRIAD_DOC` or expanding `__all__` — revisit only if a host needs it.

</deferred>

---

*Phase: 17-Validation vs thinking vs response docs*
*Context gathered: 2026-09-25*
