# Pitfalls Research

**Domain:** Adding AI generation contract (persona/rules skill) + schema-as-format-authority to an existing GeradorExercicios lab (Structured Outputs, Phase 14 slot prompts, `verify_plan_echo`, RELY, math_check, AGENTS.md “LLM is not source of truth”)
**Researched:** 2026-09-23
**Confidence:** HIGH for lab-specific failure modes (prompts.py, models, validator ownership, Phase 14 D-01..D-04); MEDIUM for how aggressively agents over-harden prompts under a new skill

> Scope note. v2.1 already shipped mixed plans, slot lists, and plan-echo. This milestone (**v2.2 Contrato de geração**, SEED-007 + SEED-008) does **not** re-litigate BATCH/CAP/UX. Focus is mistakes when **adding** a domain skill/contract and making **schema + code** the format authority while prompts stay content-only.
>
> Prior pitfall carried forward: **schema ≠ prompt** (v1 / v2.1 research Pitfall 1; SEED-008). Providers that enforce JSON schema do **not** enforce pedagogical adherence or “safe” instructions in `materia`/`topico`.
>
> Suggested phase labels below match SEED-007/008 slices until ROADMAP numbers Phases 16+. Keep the prevention intent if renumbered.

---

## Critical Pitfalls

### Pitfall 1: Duplicating JSON schema into SYSTEM_PROMPT

**What goes wrong:**
Agents “harden” generation by pasting `Exercise` / `ExerciseBatch` field trees, example JSON, or “obrigatório: enunciado, resposta, explicacao…” into `SYSTEM_PROMPT` / user template. Two sources of truth drift: Pydantic adds a field (BNCC, echo, …) and the prompt still documents the old tree — or the prompt invents fields the schema never had. Structured Outputs already enforces shape; the duplicate prose burns tokens and invites the model to “helpfully” narrate JSON outside `response_format`.

**Why it happens:**
Habit from free-form JSON eras; SEED-007 persona work feels incomplete without “listing the output”. Phase 14 already removed user-prompt field bullets (D-03) but `SYSTEM_PROMPT` still has quality prose about enunciado/resposta/explicação — easy to expand into a full schema dump under “contract alignment”.

**How to avoid:**
Policy: **format authority = `models.py` + `.parse()` / provider schema + `validate_exercise_batch`**. Prompt may describe *pedagogical quality* (“explicação passo a passo”) without naming the API tree or dumping JSON Schema. Document the contract in README / `RESPONSE-CONTRACT` for *humans and hosts*, not inside the LLM system string. Offline test: prompt must **not** contain a full field-schema dump or fenced JSON example of `ExerciseBatch`.

**Warning signs:**
- PR “aligns prompts to contract” only adds longer field lists; no model change.
- `SYSTEM_PROMPT` grows with backticks / `"enunciado":` examples.
- New `Exercise` field ships in models but prompt still lists the old triad as “the” contract.

**Phase to address:** SEED-008 Slice A (output contract doc) + Slice B (anti-prompt-as-schema policy) before Slice E (prompt rewrite).

---

### Pitfall 2: Asking the model to “validate itself” instead of code

**What goes wrong:**
Contract/skill tells the model: “verifique se a resposta está correta”, “confira a quantidade”, “valide o JSON antes de retornar”. Operators believe reliability improved; AGENTS.md is violated. Real checks (`validate_exercise_batch`, `check_math_batch`, `verify_plan_echo`, RELY) stay unchanged or get skipped “because the prompt already validates”. Failures become polite wrong answers that pass schema.

**Why it happens:**
SEED-007’s triad (validation / thinking / response) is easy to misread as *three prompt sections* rather than *three layers of the system*. Generic agent skills encourage “self-critique” loops. Validators are invisible to the LLM, so authors pad the prompt.

**How to avoid:**
Skill must state explicitly: **Validation = deterministic code only**; LLM produces **response** fields; API **reasoning_effort** is thinking, not a validator. Never add a “validation agent” or prompt-only self-check as a substitute for RELY. Light hooks in v2.2 may *document* or *assert policy offline* — they must not move ownership into the model. Mirror AGENTS.md / PROJECT constraints in the skill’s “never do” list.

**Warning signs:**
- Skill or SYSTEM_PROMPT contains “valide”, “confira o schema”, “antes de responder, revise”.
- Plan proposes removing or weakening pytest validator coverage “covered by prompt”.
- RELY never fires on structural issues because nothing raises in code.

**Phase to address:** SEED-007 Slice C (concern split) + Slice A/B (skill/rules) — lock before prompt wiring (Slice E).

---

### Pitfall 3: Confusing `reasoning_effort` with pedagogical `tipo`

**What goes wrong:**
Contract tables or wizard copy merge “pensamento” with “tipo de raciocínio”. Implementers map pedagogical intent into `resolve_reasoning_effort()` / `--reasoning`, or name skill sections `reasoning` with values `low|medium|high`. Cost spikes; pedagogical taxonomy (TIPO-OPEN, deferred) never reaches the enunciado; Phase 14 hybrid slot labels stay difficulty-only while docs claim “raciocínio por exercício”.

**Why it happens:**
SEED-007 literally says separate validation / thinking / response — “thinking” sounds like pedagogy. v2.1 already hit this (prior PITFALLS Pitfall 3); a new skill can reintroduce the collision in prose even if code is clean.

**How to avoid:**
Canonical names in contract: **`reasoning_effort`** (run-level API knob via `reasoning.py`) vs **`tipo_raciocinio` / pedagogical type** (deferred TIPO-OPEN — out of v2.2 product scope unless discuss explicitly pulls it). Skill diagram: Config → Persona → Structured response → Code validation. Do not invent per-item effort in the contract.

**Warning signs:**
- Skill glossary equates “pensamento do modelo” with “tipo de exercício”.
- Prompt adds “raciocínio: high” on slots.
- Token/`[USAGE]` rises after “persona” work with no quantity change.

**Phase to address:** SEED-007 Slice C (split table) early in discuss; reinforce in any prompt/skill copy review. Do not implement TIPO-OPEN inside v2.2 by accident.

---

### Pitfall 4: Over-hardening prompts while leaving schema unchanged

**What goes wrong:**
Milestone “feels done”: long SYSTEM_PROMPT, persona paragraphs, few-shot examples — but `Exercise` / `ExerciseBatch`, validators, and generators are untouched. Format and plan adherence do not improve; injection surface grows; Phase 14 slot adherence still depends on echo fields the prompt cannot replace. Opposite of project constraint: *harden schema/validation, not prompt theater*.

**Why it happens:**
Prompt edits are visible and low-friction; schema changes need generator + test + RELY wire-through. SEED-008 is easy to “satisfy” with more instructions instead of authority docs + policy tests.

**How to avoid:**
Definition of done for schema-as-authority: (1) human-facing response contract, (2) policy tests that **forbid** schema dumps and **require** slot list preservation, (3) prompt stripped of field-contract prose, (4) any new output guarantee lands in Pydantic + validator first. Persona text is allowed only as content/tone guidance. If a requirement needs a new guarantee, add a field or check — do not add a paragraph.

**Warning signs:**
- Diff is 90% `prompts.py` / skill markdown; zero `models.py` / `validator.py` / test policy changes.
- Acceptance criteria are “prompt mentions X” with no offline assertion on code ownership.
- Regression: plan-echo or length tests unchanged while prompt doubles in size.

**Phase to address:** SEED-008 Slices A–D as a package; treat Slice E prompt rewrite as last and smallest.

---

### Pitfall 5: Skill that contradicts AGENTS.md / validator ownership

**What goes wrong:**
New `skills/exercise-generation/SKILL.md` (or `.cursor/rules/30-…`) tells agents to “ensure quality by expanding prompts”, “add a validation step in the LLM”, or “bypass validate for speed”. GSD plan/execute follows the skill and fights AGENTS.md (no agent frameworks, LLM not source of truth, validator testable without API, max 1–2 retries). Ownership of `validate_exercise_batch` / `math_check` / `verify_plan_echo` blurs — agents move plan-echo into the prompt or into a second LLM judge.

**Why it happens:**
Generic python-ai-engineering skill is provider/architecture oriented; a domain skill drafted from ChatGPT “agent best practices” imports multi-agent validation. Authors forget the lab’s explicit exclusions.

**How to avoid:**
Skill must **point at** AGENTS.md / PROJECT constraints as authoritative: pipeline order `prompt → LLM → validate → math_check → verify_plan_echo → RELY`; no LangChain; bounded retries; offline pytest. Domain skill adds persona/tone/scope — it does **not** reassign validation. Review checklist: skill text vs AGENTS.md for contradictions before merge. Prefer “agents must not invent a validator agent” as a hard rule.

**Warning signs:**
- Skill recommends multi-agent critique or “LLM-as-judge” for format.
- Plan proposes moving `verify_plan_echo` into prompt-only instructions.
- Rule file duplicates AI engineering advice that conflicts with “no agent frameworks in MVP/lab”.

**Phase to address:** SEED-007 Slice A/B (skill + rules) with explicit AGENTS.md alignment gate; verify in code-review of the skill PR.

---

### Pitfall 6: Injection via raw `materia` / `topico` interpolation

**What goes wrong:**
`USER_PROMPT_TEMPLATE.format(materia=…, topico=…)` inserts operator/host strings unchanged (today’s `prompts.py`). Hostile or accidental input — “Ignore previous instructions…”, markdown fences, huge blobs — hijacks content, wastes tokens, or pushes the model to emit non-math / exfiltrate style text inside schema fields. Schema still validates structurally; pedagogical and safety goals fail. Contract work that lengthens the system prompt without bounding user fields **increases** relative power of injected user text.

**Why it happens:**
Lab trust model assumed local CLI operators. Embed hosts (v2.0) and demo forms now pass strings from outside. SEED-008 Slice C calls this out; easy to defer “until HTTP product”.

**How to avoid:**
In hygiene phase: length caps, strip/control-char sanitize, reject empty/whitespace after strip; keep topic as data in a delimited section (“Parâmetros:”) not as free-running instructions. Do not `eval` or concatenate untrusted text into SYSTEM_PROMPT. Enum/allowlist for future pedagogical types. Cap remains at service boundary (N≤40) — also cap string sizes. Log sanitization must not print secrets (existing LOG-02).

**Warning signs:**
- No max length on `materia`/`topico` at Pydantic boundary.
- Prompt unit tests only check happy-path topics.
- Demo/host accepts arbitrary textarea length into `GenerationRequest`.

**Phase to address:** SEED-008 Slice C (prompt hygiene) — same milestone as stripping field prose; do not ship persona-only without bounds if touch `build_prompts`.

---

### Pitfall 7: Breaking Phase 14 slot list while stripping field prose

**What goes wrong:**
Rewrite for SEED-008 removes “field contract” lines and accidentally deletes or special-cases the **numbered slot list** (`itens_ordenados` → `1. fácil (facil)` …). Uniform batches lose always-enumerate (D-02); hybrid labels (D-04) become enum-only or PT-only; cue about batch `dificuldades` as distinct-band summary disappears. `verify_plan_echo` still runs, but the model no longer sees per-slot difficulty — silent plan mismatch / RELY burn. Milestone “strips prose” while regressing PROMPT-01.

**Why it happens:**
Field-list bullets and slot-list lines look similar to a hasty editor (“lists in the prompt”). SYSTEM_PROMPT cleanup copy-pasted over `USER_PROMPT_TEMPLATE`. Tests assert “no enunciado/resposta/explicacao dump” but forget positive assertions for slot lines.

**How to avoid:**
Strip **only** response-field contract prose (D-03 / SEED-008). Preserve: always-on numbered slot list, hybrid labels, quantidade↔slots requirements, short `dificuldades` summary cue. Golden/unit tests: (a) absence of field-schema dump, (b) presence of every slot line for mixed and uniform fixtures, (c) hybrid label substrings. Treat Phase 14 D-01..D-04 as **non-negotiable carry-forward**.

**Warning signs:**
- Prompt snapshot loses `slot_list` / `_format_slot_list`.
- Uniform path branches to a template without slots.
- RELY plan-echo failures spike after “prompt cleanup” with no schema change.

**Phase to address:** SEED-008 Slice E (align prompts) + Slice D (policy tests) — tests must lock both absences and Phase 14 presences in one PR.

---

### Pitfall 8: schema ≠ prompt (carried forward — format vs plan vs content)

**What goes wrong:**
Team equates “Structured Outputs succeeded” with “contract done”. Schema guarantees keys/types; prompt hints content; **plan adherence** is `verify_plan_echo` + echo fields — not SYSTEM_PROMPT. New persona text does not fix wrong-difficulty slots. Classic schema≠prompt failure mode returns under a new name (“AI contract”).

**Why it happens:**
Documented since v1 research and SEED-008; each milestone rediscovers it when prompts get attention.

**How to avoid:**
Keep the authority table in the skill and response contract:

| Concern | Authority |
|---------|-----------|
| Format / shape | `Exercise` / `ExerciseBatch` + Structured Outputs |
| Plan / bands | `GenerationRequest.itens_ordenados` + `verify_plan_echo` |
| Content / tone | prompts (best-effort) |
| Math correctness | `math_check` (code) |
| Thinking cost | `reasoning_effort` (API, run-level) |

**Warning signs:**
- Demo of persona rewrite without running plan-echo / validator tests.
- Claims that longer prompts “enforce” JSON fields.

**Phase to address:** Cross-cutting — state in SEED-007 Slice C and SEED-008 Slice A; verify every prompt PR against this table.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Paste JSON Schema into SYSTEM_PROMPT | Feels “strict” | Dual source of truth; token waste; SEED-008 violation | Never |
| “Model, validate your output” paragraph | No code change | False confidence; AGENTS.md breach | Never as substitute for validator/RELY |
| Persona-only milestone (no policy tests) | Fast skill merge | Regressions on slot list / schema dump return next phase | Spike/discuss only — not v2.2 done |
| Reuse “reasoning” for pedagogy in skill docs | Less vocabulary | Cost + TIPO confusion forever | Never — distinct names |
| Skip `materia`/`topico` bounds (local CLI trust) | Less validation code | Embed/demo injection & cost DoS | Never once embed/demo exist |
| Delete all quality prose from SYSTEM_PROMPT in one swing | Clean SEED-008 | May drop useful tone/pedagogy without replacement skill | Prefer: strip field-contract only; move tone to skill + short persona lines |
| LLM-as-judge for plan adherence | Avoids echo fields | Non-deterministic, expensive, duplicates `verify_plan_echo` | Never in this lab |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `prompts.py` + Pydantic `.parse()` | Prompt redefines fields already in `response_format` | Content/slots only; schema owns shape |
| `validate_exercise_batch` / `math_check` | Skill implies LLM owns quality | Code owns; prompt must not claim otherwise |
| `verify_plan_echo` + RELY | Replace echo check with prompt “respeite o plano” only | Keep echo validation; prompt lists slots as hints |
| `reasoning.py` | Contract wires pedagogical tipo to effort kwargs | Effort stays run-level; tipo deferred/out of band |
| New `skills/exercise-generation` | Copy generic agent patterns | Align with AGENTS.md; point to pipeline modules |
| Hosts via `generate_batch` | Trust prompt for embed contract | Hosts trust models + error `kind`s + README response contract |
| Phase 14 slot list | Stripped during field-prose cleanup | Preserve D-01..D-04; test presence |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Huge persona + few-shot in every call | Latency/cost up; tail slots ignored | Keep SYSTEM_PROMPT short; put long policy in skill for *agents*, not every LLM call | Immediately at N→40 with high reasoning_effort |
| Schema dump + slot list | Context bloat, no quality gain | No schema dump (Pitfall 1) | Mixed lots with long topics |
| Unbounded `topico` text | Timeouts, truncation, RELY thrash | Length caps at request boundary | Hostile or paste-bomb inputs |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Raw interpolation of `materia`/`topico` | Prompt injection; off-policy content inside valid JSON | Caps, sanitize, delimit; never into SYSTEM_PROMPT builder from untrusted host without bounds |
| Skill tells agents to log full prompts/responses with keys | Key leakage | Keep LOG-02; skill must forbid logging secrets |
| Treating prompt as security boundary for format | Hosts assume shape from instructions | Schema + validator only; document for embed consumers |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Wizard labels API effort as “tipo de raciocínio” | Wrong mental model; surprise bills | Copy: esforço do modelo vs (future) tipo pedagógico |
| Operator believes longer persona = correct math | Trusts bad answers | Surface math_check/RELY failures; don’t market prompt as validator |
| Docs say “AI contract guarantees JSON fields” | Embed hosts skip reading models | Response-contract doc: what schema guarantees vs best-effort content |

## "Looks Done But Isn't" Checklist

- [ ] **Authority table:** Skill states format=schema, plan=echo/validator, content=prompt, thinking=API effort — verify written and reviewed against AGENTS.md
- [ ] **No schema dump:** Offline test asserts absence of full field-tree / JSON example in prompts — verify pytest
- [ ] **No self-validate prompt:** SYSTEM/USER lack “valide o JSON/schema” as substitute — verify grep + review
- [ ] **Phase 14 slots preserved:** Always-on numbered hybrid slot list + `dificuldades` cue — verify mixed *and* uniform prompt fixtures
- [ ] **Field prose stripped:** No re-list of enunciado/resposta/explicacao as API contract in USER template (D-03) — verify; quality tone may remain short
- [ ] **Injection hygiene:** `materia`/`topico` bounded/sanitized or explicitly scheduled — verify model validators or tracked follow-up
- [ ] **Naming:** Skill/docs do not alias pedagogical tipo ↔ `reasoning_effort` — verify glossary
- [ ] **Code ownership unchanged:** `validate_exercise_batch` / `math_check` / `verify_plan_echo` still authoritative — verify no “prompt replaces RELY” plan
- [ ] **Human contract:** Hosts/README (or RESPONSE-CONTRACT) document canonical fields — verify embed section
- [ ] **Over-harden check:** Diff is not prompt-only without policy tests — verify Slice D artifacts

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Schema dump in prompt | LOW | Revert dump; add absence test; point readers to models/README |
| Self-validate prompt culture | MEDIUM | Rewrite skill + SYSTEM_PROMPT; restore/ensure validator tests; re-assert AGENTS.md in review |
| Reasoning/tipo collision | MEDIUM | Rename docs/fields; audit `reasoning.py` call sites; defer TIPO-OPEN |
| Prompt-only “done” | MEDIUM | Stop ship; add contract doc + policy tests; minimal prompt diff |
| Skill vs AGENTS.md | MEDIUM | Edit skill in place; changelog for agents; reject conflicting plans |
| Injection via topic fields | MEDIUM | Add caps/sanitize; regenerate; treat as InvalidRequestError for oversize |
| Broken slot list | HIGH | Restore `_format_slot_list` + D-01..D-04; add presence tests; re-run plan-echo fixtures |
| schema≠prompt confusion | LOW | Re-publish authority table; train on SEED-008 |

## Pitfall-to-Phase Mapping

How v2.2 slices should prevent these (SEED-007 + SEED-008). Roadmap may assign Phase 16+.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| JSON schema duplicated into SYSTEM_PROMPT | SEED-008 A+B (contract + policy) | Absence tests; doc points to models |
| Model self-validation vs code | SEED-007 C + A/B (split + skill) | Skill forbids; prompts lack self-validate substitute |
| reasoning_effort vs pedagogical tipo | SEED-007 C (glossary) | Distinct names; no effort kwargs from “tipo” |
| Over-harden prompt / schema unchanged | SEED-008 A–D before E | Done = tests+doc+strip; not prompt length |
| Skill contradicts AGENTS.md / validators | SEED-007 A/B | Review gate vs AGENTS.md; pipeline order cited |
| Raw materia/topico injection | SEED-008 C | Caps/sanitize tests; hostile fixture |
| Break Phase 14 slot list while stripping | SEED-008 E + D | Presence tests for slots + absence of field dump |
| schema ≠ prompt (format vs plan vs content) | SEED-007 C + SEED-008 A | Authority table in skill + response contract |

**Suggested order:** SEED-007 A–C (skill + authority split, AGENTS.md lock) → SEED-008 A–B (human response contract + anti-prompt-as-schema) → SEED-008 C (hygiene/caps) → SEED-008 D+E together (policy tests + minimal prompt strip preserving slots) → SEED-007 E only if persona lines still needed after skill exists.

## Sources

- SEED-008 (`seeds/SEED-008-response-structure-over-prompt.md`) — schema-as-authority; prompt not safe for shape; injection via raw fields; Phase 14 alignment
- SEED-007 (`seeds/SEED-007-exercise-ai-persona-rules.md`) — domain skill; validation vs thinking vs response; no second validator agent
- Phase 14 CONTEXT D-01..D-04 / D-03 — slot list always-on; hybrid labels; no field-contract re-list
- Prior `.planning/research/PITFALLS.md` (v2.1) Pitfall 1 schema≠prompt; Pitfall 3 reasoning name collision — carried into contract work
- `exercise-ai/prompts.py` — SYSTEM_PROMPT field-quality prose; USER slot list; raw `{materia}`/`{topico}` `.format`
- `exercise-ai/models.py` / `validator.py` / `reliability.py` / `reasoning.py` — real ownership boundaries
- AGENTS.md / `.planning/PROJECT.md` — LLM not source of truth; no agent frameworks; bounded RELY
- OpenAI Structured Outputs — schema adherence ≠ instruction adherence

---
*Pitfalls research for: v2.2 AI generation contract + schema-as-authority on existing GeradorExercicios lab*
*Researched: 2026-09-23*
