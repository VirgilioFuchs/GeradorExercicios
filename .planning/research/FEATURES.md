# Feature Research

**Domain:** Exercise-generation AI contract (persona, pipeline concerns, schema-as-format-authority)
**Researched:** 2026-09-23
**Confidence:** HIGH on table stakes (SEED-007/008 + PROJECT.md v2.2 goals + Phase 14 partial hygiene); HIGH on anti-features that reintroduce LLM self-check or prompt-as-schema; MEDIUM on how far “light validation hooks” go beyond existing `validate` / `verify_plan_echo` / math_check

**Milestone:** v2.2 “Contrato de geração” — SEED-007 + SEED-008. Mixed batches, slot prompts, `verify_plan_echo`, demo/CLI/wizard bands, and Structured Outputs `ExerciseBatch` are **already shipped** (v2.1) and stay baseline. This milestone documents and hardens behavior/contract around generation — not a new product surface (no HTTP, BNCC, images, packaging).

---

## Feature Landscape

### Table Stakes (Operators / Agents Expect These)

Features assumed once “contrato de geração” is the milestone. Missing these = prompts and agents keep mixing think / answer / validate, or treat prompt prose as format safety.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Domain skill index for exercise generation** | Lab already has `skills/python-ai-engineering/SKILL.md` → generic AI rules; operators asked for the same pattern **specific to** generating exercises (persona, capabilities, what the system does/doesn’t do, pipeline order) | LOW–MEDIUM | e.g. `skills/exercise-generation/SKILL.md` (+ optional `.cursor/rules/30-exercise-generation.mdc` or `docs/EXERCISE-AI-CONTRACT.md`). Index points to authoritative rules; GSD plan/execute/review apply it. Single professor persona unless discuss unlocks variants |
| **Explicit validation vs thinking vs response separation (docs)** | Without a written triad, agents invent “validate in the prompt” or treat `reasoning_effort` as a pedagogical field | LOW | Table + short pipeline diagram: **Pensamento** = API effort (`reasoning.py`, run-level); **Resposta** = `Exercise` fields via Structured Outputs; **Validação** = Pydantic + `validator` + `math_check` + `verify_plan_echo` + RELY; **Config** = provider/model/env. Aligns with SEED-007 suggested architecture |
| **SYSTEM/USER prompt rewrite aligned to the contract** | Today `SYSTEM_PROMPT` still narrates field presence (“enunciado… resposta… explicação…”) and “formato solicitado”; USER already has slots (v2.1) but system is pre-contract | MEDIUM | Persona + pedagogical constraints + follow plan slots; **no** duplicate field API; keep PT-BR professor tone; preserve slot enumeration (SEED-006/Phase 14) |
| **Strip enunciado/resposta/explicação field-contract prose from prompts** | Prompt is not a safe format contract; Phase 14 removed field bullets from USER (D-03) but SYSTEM still restates the three fields | LOW | Format authority = `models.py` + `.parse()` / `response_format=ExerciseBatch` + validators. Prompt may teach **content** (topic, slot difficulty, band summary cue) only |
| **Light validation hooks in code (not LLM self-check)** | Core Value: LLM is not source of truth; “ask the model to validate” undermines the lab | LOW–MEDIUM | Prefer small, deterministic hooks around existing seams (e.g. assert prompt policy helpers, keep/strengthen plan-echo + structural checks). **Do not** add a second agent or “self-critique” pass as substitute for `validator` / math / RELY |
| **Offline tests asserting prompt policy** | Without tests, the next phase re-dumps schema into SYSTEM “for safety” | LOW | Assert: no full JSON schema dump; no enunciado/resposta/explicacao field-contract block; slot list **present** for mixed/uniform via `itens_ordenados`. Pure string/fixture tests — no live LLM |

### Differentiators (Competitive Advantage)

Not required for “docs exist,” but strengthen the lab’s Core Value (reliable structured generation) and make the contract agent-usable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Skill as single index for GSD + human operators** | Same pattern as python-ai-engineering: one entrypoint so plan/review don’t invent architecture | LOW | Skill lists capabilities (uniform + mixed lots, providers, RELY bounds) and **non-capabilities** (no LangChain validator-agent, no BNCC yet) |
| **Schema-first field policy for future Exercise fields** | When BNCC/images land later, order is Pydantic → validator → optional content hint in prompt — not the reverse | LOW | Document in contract; SEED-001/003 stay out of v2.2 implementation |
| **Authority split written once (format / plan / content)** | SEED-008 policy: format → models+SO; plan → `itens_ordenados` + `verify_plan_echo`; content → prompts (best-effort) | LOW | Stops “harden the prompt” as default fix for adherence bugs |
| **Prompt hygiene hooks (bound/escape request fields)** | `materia`/`topico` are interpolated raw today — injection / junk cost risk called out in SEED-008 | MEDIUM | Caps + control-char strip as **light** code hooks; differentiator if kept small; defer heavy sanitization frameworks |
| **Markers / constants for policy strings** | Tests and skills share the same “forbidden patterns” / required slot markers | LOW | Avoid brittle copy-paste assertions drifting from prompts |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **LLM self-check / “critic” agent in the prompt or second call** | “Make the model validate itself” | Duplicates deterministic validation; burns tokens; fails closed poorly; violates “LLM not source of truth” | Keep `validate_exercise_batch` + math_check + `verify_plan_echo` + bounded RELY |
| **Dump full JSON / Pydantic schema into SYSTEM_PROMPT** | Feels safer for Structured Outputs | Schema already enforced by API; dump can drift, bloat context, and teach agents that prompt = contract | `response_format=ExerciseBatch` + models; prompt = pedagogy only |
| **Re-list enunciado / resposta / explicação as prompt “API”** | Easy to “document” fields next to slots | False security; fights SEED-008; Phase 14 already banned on USER | Strip remaining SYSTEM prose; document fields in RESPONSE/Exercise contract doc |
| **Multi-persona taxonomy / “personalities” pack** | Seed title says personalidade | Bikeshed; not locked in discuss; YAGNI before single professor contract ships | One persona (professor PT-BR); variants only after discuss |
| **LangChain / CrewAI / multi-agent “validation crew”** | Industry fashion for “agents” | Explicit project exclusion; hides fundamentals this lab studies | Plain SDK + modules; skill documents the real pipeline order |
| **Redesign RELY / math_check / failover in v2.2** | “While we’re in the contract…” | Scope explosion; SEED-009 waits on BNCC; mixed RELY already works | Touch only light hooks that protect contract invariants |
| **Treating thinking (API effort) as a response field or pedagogical tipo** | Name collision with “raciocínio” | Already an anti-feature from v2.1 FEATURES; contract must keep the split visible | Document triad; keep `reasoning_effort` run-level |
| **HTTP / FastAPI product surface for the contract** | “Expose the contract as API” | Demo is throwaway; embed seam is `generate_batch` | Docs + skill + prompts + tests only |

## Already Built (Baseline — Do Not Re-scope as v2.2 MVP)

| Capability | Status | Implication for v2.2 |
|------------|--------|----------------------|
| Mixed `plano` / `itens` + uniform compat | Shipped v2.1 | Contract docs must describe both modes |
| Slot prompts (`build_prompts` + `slot_list`) | Shipped | Keep; rewrite must not remove slot enumeration |
| `verify_plan_echo` in RELY | Shipped | Cite as **plan** authority, not format |
| Demo / CLI `--plano` / wizard bands | Shipped | Out of scope unless copy must mention contract |
| Structured Outputs `ExerciseBatch` | Shipped | Format authority; prompts must defer to it |
| USER field-list removal (D-03 / SEED-008 partial) | Shipped Phase 14 | Finish the job on SYSTEM + lock with offline tests |

## Feature Dependencies

```
Domain skill index (SEED-007 A)
    └──requires──> Validation vs thinking vs response docs (SEED-007 C/D)
                       ├──requires──> Accurate pipeline diagram (prompt → LLM → validate → math → plan_echo → RELY)
                       └──enhances──> SYSTEM/USER prompt rewrite (SEED-007 E)

Strip field-contract prose (SEED-008 B/C)
    └──requires──> Schema-as-format-authority policy (SEED-008 A/B)
    └──requires──> Prompt rewrite (same change set preferred)
    └──enhances──> Offline prompt-policy tests (SEED-008 D)

Light validation hooks (code)
    └──requires──> Existing validator / verify_plan_echo / math_check (reuse)
    └──conflicts──> LLM self-check agent (anti-feature)
    └──enhances──> Prompt-policy tests (hooks may be the assert surface)

Prompt hygiene (bound materia/topico)
    └──enhances──> Strip field prose / rewrite
    └──conflicts──> Treating prompt sanitization as sufficient format security

Future Exercise fields (BNCC, images)
    └──requires──> Schema-first policy (document now; implement later)
    └──conflicts──> Prompt-first field invention
```

### Dependency Notes

- **Skill requires separation docs:** An index without the triad just renames generic AI rules; agents still confuse effort / fields / validators.
- **Strip prose + rewrite should land together:** Leaving SYSTEM field narration while “aligning to contract” recreates Pitfall-style false safety.
- **Offline tests require a stable policy:** Forbidden patterns (schema dump, field-contract bullets) and required patterns (slot list) must be named in the contract or constants.
- **Light hooks enhance, do not replace, RELY:** New code asserts invariants or hygiene; regenerations stay in the existing 1–2 attempt loop.
- **LLM self-check conflicts with Core Value:** Any “model, please verify your JSON” path is out of scope for v2.2.

## MVP Definition

### Launch With (v2.2)

Minimum to make “Contrato de geração” real for operators and GSD agents.

- [ ] **Domain skill index** (persona, capabilities, pipeline order) — SEED-007 A/B/D
- [ ] **Explicit validation / thinking / response separation** in that skill or linked rule/doc — SEED-007 C
- [ ] **SYSTEM + USER prompt rewrite** aligned to contract (slots kept; field-API prose removed from SYSTEM) — SEED-007 E + SEED-008 C
- [ ] **Strip remaining enunciado/resposta/explicação field-contract prose** — SEED-008
- [ ] **Light code-owned validation/hygiene hooks** (no LLM self-check) — SEED-007 E
- [ ] **Offline tests for prompt policy** (no schema dump; slots OK; no field-contract block) — SEED-008 D

### Add After Validation (v2.2.x / same milestone if capacity)

- [ ] **Dedicated RESPONSE-CONTRACT / EXERCISE-AI-CONTRACT doc** — trigger: skill alone is too dense for embed hosts
- [ ] **materia/topico length caps + control-char strip** — trigger: discuss marks injection hygiene as in-scope (SEED-008 C)
- [ ] **Shared policy constants/markers** for tests and skill cross-links — trigger: brittle string asserts in CI

### Future Consideration (post-v2.2)

- [ ] **Multiple personas** — defer until single contract is proven
- [ ] **BNCC / images / storytelling fields** — schema-first later (SEED-001/003); contract only documents the rule now
- [ ] **SEED-009 math_check × BNCC** — waits on SEED-001
- [ ] **PKG-01 / OBS-01 / LOG-01** — parked; not contract work
- [ ] **CAP-02 / TIPO-OPEN** — deferred past v2.2 per PROJECT.md

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Domain skill index (persona + pipeline) | HIGH | LOW–MEDIUM | P1 |
| Validation vs thinking vs response docs | HIGH | LOW | P1 |
| Prompt rewrite aligned to contract | HIGH | MEDIUM | P1 |
| Strip field-contract prose (finish SYSTEM) | HIGH | LOW | P1 |
| Offline prompt-policy tests | HIGH | LOW | P1 |
| Light code validation/hygiene hooks | HIGH | LOW–MEDIUM | P1 |
| RESPONSE/Exercise contract doc (standalone) | MEDIUM | LOW | P2 |
| Bound/escape materia/topico | MEDIUM | MEDIUM | P2 |
| Multi-persona pack | LOW | HIGH | P3 / anti until discuss |
| LLM self-check / schema-in-prompt | LOW (misframed) | MEDIUM–HIGH | — Anti-feature |
| RELY/math_check redesign | — | HIGH | Out of scope |

**Priority key:**
- P1: Must have for v2.2 launch
- P2: Should have when discuss/capacity allows
- P3: Nice to have / later milestone

## Competitor / Lab Feature Analysis

| Feature | Typical “AI quiz” SaaS | Generic agent frameworks | Our approach (v2.2) |
|---------|------------------------|--------------------------|---------------------|
| Persona / teacher voice | Marketing copy in UI; rarely a versioned skill | System prompt only | Versioned domain skill + short SYSTEM aligned to it |
| Output format trust | Prompt + hope; sometimes JSON mode | Tool schemas vary | Structured Outputs + Pydantic + validator = authority; prompt ≠ schema |
| Validation | Often another LLM pass or none | Critic agents common | Deterministic code path documented as the only validator |
| Thinking vs answer | Blurred (“show your work” in one blob) | Chain-of-thought in product text | API effort separate from enunciado/resposta/explicação |
| Plan adherence | Rare | Rare | Already shipped (`verify_plan_echo`); contract **names** it as plan authority |

## Sources

- SEED-007 — persona, rules, validation vs thinking vs response, skill index, prompt wiring
- SEED-008 — response structure over prompt; anti prompt-as-schema; policy tests; prompt hygiene
- `.planning/PROJECT.md` — v2.2 milestone goals (A3/B2: skill + prompts + light hooks; strip field prose)
- Shipped baseline: `exercise-ai/prompts.py`, `models.py` (`Exercise`/`ExerciseBatch`, `verify_plan_echo`), `validator.py`, `math_check.py`, `reliability.py`, `reasoning.py`, `service.generate_batch`
- Phase 14 CONTEXT D-03 / VERIFICATION — USER field-list removed; SYSTEM still has pre-existing field/quality prose
- Pattern to mirror: `skills/python-ai-engineering/SKILL.md`, `.cursor/rules/20-ai-engineering.mdc`
- Prior research: `.planning/research/PITFALLS.md` (schema ≠ instruction adherence); v2.1 FEATURES (tipo vs API effort split — still binding)

---
*Feature research for: exercise-generation AI contract (SEED-007 + SEED-008 / v2.2)*
*Researched: 2026-09-23*
