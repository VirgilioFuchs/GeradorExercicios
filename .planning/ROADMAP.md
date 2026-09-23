# Roadmap: Gerador de Exercícios com IA

## Milestones

- ✅ **v1 MVP** — Phases 1–3 (shipped 2026-09-04) — [archive](./milestones/v1-ROADMAP.md) · [requirements](./milestones/v1-REQUIREMENTS.md) · [phases](./milestones/v1-phases/) · [audit](./milestones/v1-MILESTONE-AUDIT.md)
- ✅ **v1.1 Qualidade do exercício** — Phases 4–6 (shipped 2026-09-09) — [archive](./milestones/v1.1-ROADMAP.md) · [requirements](./milestones/v1.1-REQUIREMENTS.md) · [phases](./milestones/v1.1-phases/) · [audit](./milestones/v1.1-MILESTONE-AUDIT.md)
- ✅ **v1.2 Ops & Resilience** — Phases 7–10 (shipped 2026-09-15) — [archive](./milestones/v1.2-ROADMAP.md) · [requirements](./milestones/v1.2-REQUIREMENTS.md) · [phases](./milestones/v1.2-phases/) · [audit](./milestones/v1.2-MILESTONE-AUDIT.md)
- ✅ **v2.0 Embed em Produção** — Phases 11–12 (shipped 2026-09-18) — [archive](./milestones/v2.0-ROADMAP.md) · [requirements](./milestones/v2.0-REQUIREMENTS.md) · [phases](./milestones/v2.0-phases/) · [audit](./milestones/v2.0-MILESTONE-AUDIT.md)
- ✅ **v2.1 Lotes dinâmicos** — Phases 13–15 (shipped 2026-09-23) — [archive](./milestones/v2.1-ROADMAP.md) · [requirements](./milestones/v2.1-REQUIREMENTS.md) · [phases](./milestones/v2.1-phases/) · [quick](./milestones/v2.1-quick/) · [audit](./milestones/v2.1-MILESTONE-AUDIT.md)
- 🚧 **v2.2 Contrato de geração** — Phases 16–25 (in progress) — **1 requirement per phase**

## Current Milestone: v2.2 Contrato de geração

**Goal:** Domain AI contract (persona/rules + validation≠thinking≠response) with schema-as-format-authority; prompts teach content only.

**Requirements:** 10 v2.2 · see [REQUIREMENTS.md](./REQUIREMENTS.md)  
**Phase policy:** Exactly one REQ-ID per phase (audit/verify granularity).

### Phase 16: Domain skill index

**Goal:** A Cursor/repo skill index exists for exercise generation (same pattern as python-ai-engineering).
**Requirements:** CONTRACT-01
**Success criteria:**

1. `skills/exercise-generation/SKILL.md` (or equivalent path) exists and points at authoritative rules
2. Skill describes what the generator does / does not do
3. Skill is discoverable for plan/execute/review agents

### Phase 17: Validation vs thinking vs response docs

**Goal:** Written triad so agents do not invent prompt-side validation or confuse API effort with response fields.
**Requirements:** CONTRACT-02
**Success criteria:**

1. Docs/rules state validation = deterministic code only
2. Thinking = API `reasoning_effort` (run-level), not an Exercise field
3. Response = Structured Outputs `Exercise` fields only

### Phase 18: Authority map (format / plan / content)

**Goal:** One authority map: format→schema · plan→echo · content→prompts.
**Requirements:** CONTRACT-03
**Success criteria:**

1. Authority map is documented in the contract/rules surface
2. Format authority explicitly names models + Structured Outputs (not prompt)
3. Plan authority explicitly names `verify_plan_echo` / `itens_ordenados`

### Phase 19: Prompt persona alignment

**Goal:** SYSTEM/USER prompts mirror persona and pedagogical rules from the domain contract.
**Requirements:** PROMPT-02
**Success criteria:**

1. SYSTEM prompt reflects professor PT-BR persona from the contract
2. Pedagogical rules from the contract appear in prompt content (not as schema)
3. Existing offline prompt tests still pass (no regression beyond intentional copy changes)

### Phase 20: Strip field-contract prose from prompts

**Goal:** Prompts no longer list enunciado/resposta/explicação as a format/API contract.
**Requirements:** PROMPT-03
**Success criteria:**

1. SYSTEM/USER lack field-contract blocks naming the triad as required JSON keys
2. No full JSON schema / ExerciseBatch dump in prompts
3. Format remains owned by Pydantic + Structured Outputs only

### Phase 21: Preserve slot enumeration

**Goal:** Phase 14 slot lists remain for uniform and mixed batches after prompt hygiene.
**Requirements:** PROMPT-04
**Success criteria:**

1. Built prompts still enumerate slots from `itens_ordenados` (uniform + mixed)
2. Hybrid difficulty labels remain where Phase 14 defined them
3. Offline tests covering slot presence stay green

### Phase 22: No LLM self-check path

**Goal:** Confirm and keep validation code-owned — no new model self-validation path.
**Requirements:** VAL-03
**Success criteria:**

1. Pipeline adds no “critic” / self-check LLM call
2. Skill/prompts do not instruct the model to validate schema or replace RELY
3. `validate_exercise_batch` + math_check + `verify_plan_echo` remain the adherence path

### Phase 23: Request-field hygiene (materia / topico)

**Goal:** Light bound and/or control-char strip on interpolated `materia`/`topico` before prompt build.
**Requirements:** VAL-04
**Success criteria:**

1. Hygiene runs before string interpolation into USER prompt
2. Empty/overlong/control-laden inputs are rejected or sanitized deterministically
3. Unit tests cover at least one bound and one strip/reject case

### Phase 24: Offline tests — no schema dumps in prompts

**Goal:** Pytest locks absence of schema/field-contract dumps in built prompts.
**Requirements:** TEST-01
**Success criteria:**

1. Offline test fails if field-contract triad dump returns to SYSTEM/USER
2. Offline test fails if fenced JSON ExerciseBatch schema example appears in prompts
3. Tests run without live LLM

### Phase 25: Offline tests — slot list present

**Goal:** Pytest locks that slot enumeration remains in built prompts.
**Requirements:** TEST-02
**Success criteria:**

1. Offline test asserts slot list for a mixed plan request
2. Offline test asserts slot list for a uniform request
3. Full `pytest exercise-ai` green at phase close

## Phases (shipped)

<details>
<summary>✅ v1 MVP (Phases 1–3) — SHIPPED 2026-09-04</summary>

- [x] Phase 1: Project Setup & LLM Pipeline (1/1 plans)
- [x] Phase 2: Validation & Error Handling (1/1 plans)
- [x] Phase 3: Tests, Logging & Docs (1/1 plans)

</details>

<details>
<summary>✅ v1.1 Qualidade do exercício (Phases 4–6) — SHIPPED 2026-09-09</summary>

- [x] Phase 4: CLI argparse (1/1 plans)
- [x] Phase 5: Reliability & Error Edges (1/1 plans)
- [x] Phase 6: Math Quality (1/1 plans)

</details>

<details>
<summary>✅ v1.2 Ops & Resilience (Phases 7–10) — SHIPPED 2026-09-15</summary>

- [x] Phase 7: Continuous Integration (1/1 plans)
- [x] Phase 8: Provider Failover (1/1 plans)
- [x] Phase 9: Token Usage Observability (1/1 plans)
- [x] Phase 10: Interactive CLI Wizard (1/1 plans)

</details>

<details>
<summary>✅ v2.0 Embed em Produção (Phases 11–12) — SHIPPED 2026-09-18</summary>

- [x] Phase 11: Service Layer Extraction (3/3 plans) — completed 2026-09-16
- [x] Phase 12: Local Embed Demo (2/2 plans) — completed 2026-09-18

</details>

<details>
<summary>✅ v2.1 Lotes dinâmicos (Phases 13–15) — SHIPPED 2026-09-23</summary>

- [x] Phase 13: Request schema & plan contract (1/1 plans) — completed 2026-09-22
- [x] Phase 14: Mixed prompt + plan-adherence + demo enablement (3/3 plans) — completed 2026-09-22
- [x] Phase 15: CLI / wizard batch-plan UX (2/2 plans) — completed 2026-09-23

</details>

## Deferred / open (not in v2.2 phases)

- PKG-01, OBS-01, LOG-01
- CAP-02, TIPO-OPEN
- SEED-001 / 003 / 005 / 009

---
*Roadmap updated: 2026-09-23 — v2.2 split to 1 REQ per phase (16–25)*
