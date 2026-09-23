# Stack Research

**Domain:** Domain AI generation contract + prompt hygiene (schema-as-authority)
**Researched:** 2026-09-23
**Confidence:** HIGH

---

## Headline

**For v2.2 the correct stack addition is: nothing new in `exercise-ai/requirements.txt`.** The milestone is markdown contracts (Cursor skill + `.cursor` rules), a `prompts.py` rewrite that stops duplicating field shape in prose, and light offline policy/validation hooks on the existing Pydantic + Structured Outputs + `validator` / `verify_plan_echo` pipeline. Keep `openai`, `google-genai`, `pydantic`, `python-dotenv`, `pytest` unchanged. Do not introduce prompt-guard libraries, agent frameworks, or packaging.

**Baseline already shipped (do not re-select):** Python 3.11+, openai Structured Outputs + Pydantic v2, google-genai, pytest, `service.generate_batch`, `verify_plan_echo`, `plan_ux`.

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| *(unchanged)* Pydantic models + Structured Outputs | existing pins | **Format authority** | `Exercise` / `ExerciseBatch` + `.parse()` / `model_json_schema()` already own shape. Field `description=` metadata flows into JSON schema (Context7 `/pydantic/pydantic`) — that is where field semantics live, not SYSTEM_PROMPT prose. |
| *(unchanged)* `validator.py` + `verify_plan_echo` + math_check + RELY | in-repo | **Code-owned adherence** | Validation / plan echo / math stay deterministic; skill must tell agents not to invent a second “LLM validates itself” layer. |
| Cursor / repo markdown contracts | n/a (files) | Domain skill + rules | Same pattern as `skills/python-ai-engineering/SKILL.md` → `.cursor/rules/*.mdc`: index skill points at authoritative rules; GSD agents load them on plan/execute/review. |

**Nothing is added to `exercise-ai/requirements.txt` for this milestone.**

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| stdlib `str` / `re` (optional) | stdlib | Prompt hygiene helpers | Bound/strip control chars on interpolated `materia`/`topico` if discuss-phase wants SEED-008 slice C; keep tiny and unit-tested — no `bleach` / `validators` package. |
| Existing `prompts.build_prompts` | in-repo | Persona + pedagogical content only | Rewrite strings: keep professor tone, slot list, PT-BR, topic fidelity; **remove** field-contract sentences that list `enunciado` / `resposta` / `explicacao` or “retorne no formato solicitado” as if prompt owned the schema. |
| Existing `tests/test_prompts.py` | in-repo | Offline prompt-policy asserts | Extend absence-of-field-contract checks to SYSTEM_PROMPT; optional marker for filtering — still pytest only. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| pytest ≥8.0 (existing) | Offline policy + validator tests | Assert SYSTEM/USER prompts lack field-schema dumps; assert contract docs/rules exist if desired via path checks. No live LLM. |
| Optional `@pytest.mark.prompt_policy` | Group SEED-008 tests | Register via `pytest.ini` / `conftest.pytest_configure` or a one-line marker list — Context7 `/pytest-dev/pytest` (custom markers). Prefer **no** new config file unless markers proliferate; plain asserts in `test_prompts.py` already work. |
| Cursor rules frontmatter | Agent scoping | Mirror `20-ai-engineering.mdc`: `description` + `alwaysApply: false` (or globs for `prompts.py` / generation paths) so the domain rule loads when editing generation contract code. |

---

## Installation

```bash
# v2.2 adds nothing to the Python install contract:
pip install -r exercise-ai/requirements.txt

# Artifact layout (files only — not pip packages):
#   skills/exercise-generation/SKILL.md          # index (mirror python-ai-engineering)
#   .cursor/rules/30-exercise-generation.mdc    # authoritative domain contract
#   optional: short docs pointer in README Embed / RESPONSE-CONTRACT section
```

---

## Integration Points (NEW only)

| Seam | v2.2 change (stack-neutral) |
|------|-----------------------------|
| `skills/exercise-generation/SKILL.md` | Thin index like `python-ai-engineering`: point at `.cursor/rules/30-exercise-generation.mdc` (+ maybe existing `20-ai-engineering.mdc`). Define when GSD applies it (plan/execute/review touching generation). |
| `.cursor/rules/30-exercise-generation.mdc` | Persona, capabilities, pipeline order, **split**: Thinking (`reasoning.py` run-level) vs Response (`Exercise` fields via schema) vs Validation (code). Explicit: do not duplicate JSON schema in prompts; do not ask the model to self-validate as substitute for `validate_exercise_batch`. |
| `prompts.py` | Strip field-contract prose from `SYSTEM_PROMPT` (today lines that mandate enunciado/resposta/explicação + “formato solicitado”). Keep pedagogical requirements + slot enumeration. User prompt may keep the one-line `dificuldades` **resumo** cue (plan semantics), not a field-API dump. |
| `validator.py` / RELY | **Light** hooks only: extend existing offline checks if needed (e.g. empty fields already covered). Do **not** add a new validation framework. Plan adherence remains `verify_plan_echo`. |
| `tests/test_prompts.py` | Policy tests: SYSTEM must not restate field contracts; USER must not invent `enunciado:`/`resposta:`/`explicacao:` API lines (already asserted for user). |
| Generators / providers | **No change** — still `response_format=ExerciseBatch` / Gemini schema from Pydantic. |

---

## Schema-as-Authority Pattern (verified)

**Authority split (SEED-008):**

```text
FORMAT  → models.py + Structured Outputs / model_json_schema()
PLAN    → GenerationRequest.itens_ordenados + verify_plan_echo / validator
CONTENT → prompts (topic, slot difficulty, tone) — best-effort
```

**Pydantic Field descriptions** already place semantic field docs in the schema sent to providers (`Field(description=...)` → `model_json_schema()` properties). Context7 `/pydantic/pydantic` confirms `description` is JSON-schema metadata, not a reason to paste field lists into the system prompt.

**Prompt rewrite rule of thumb:** if deleting a sentence would not change pedagogical intent and the information already exists on `Exercise` / `ExerciseBatch`, delete it from the prompt.

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| `skills/…/SKILL.md` + `.cursor/rules/30-….mdc` (mirror python-ai-engineering) | Only a `docs/EXERCISE-AI-CONTRACT.md` | Docs-only if agents never need auto-load; weaker for GSD — prefer skill→rules like existing engineering contract. |
| Repo `skills/exercise-generation/` | `.cursor/skills/exercise-generation/` | Cursor-native discovery prefers `.cursor/skills/`; this repo already uses `skills/` for `python-ai-engineering` — **stay consistent** unless discuss-phase wants dual symlink/copy. |
| Extend `test_prompts.py` string asserts | New package (`promptfoo`, `guardrails-ai`, `llm-guard`) | Never for MVP lab — YAGNI, live/eval deps, hides ownership in code. |
| Soften SYSTEM_PROMPT only | Dump full JSON schema into system message | Explicitly forbidden by SEED-008; schema already enforced by API. |
| Light stdlib sanitize of `materia`/`topico` | New sanitization library | Only if discuss locks injection hygiene; stdlib length cap + control-char strip is enough. |
| pytest marker `prompt_policy` | Separate test package / tox env | Overkill; one marker or none. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| LangChain / CrewAI / AutoGen / PydanticAI “agents that validate” | Violates lab constraints; duplicates RELY in prompt-land | Skill that documents existing pipeline order |
| `instructor`, Outlines, Guidance, Guardrails | Extra structured-output / policy layers on top of `.parse()` | Existing generators + Pydantic |
| Packaging / `pyproject.toml` (PKG-01) | Explicitly out of v2.2 | Current `exercise-ai/` layout |
| BNCC (SEED-001/009), new LLM providers | Out of milestone | Existing OpenAI / Gemini / Grok path |
| Putting JSON Schema or field API lists in prompts | Prompt is not format authority; invites drift vs models | Schema + validator + Field descriptions |
| “Ask the model to validate its own JSON” in SYSTEM_PROMPT | Undermines code-owned validation | `validate_exercise_batch` + RELY |
| New runtime deps for markers/docs | Markers and skills are files | pytest + markdown |

---

## Stack Patterns by Variant

**If skill is index-only (expected default):**
- `SKILL.md` lists authoritative files and the validation/thinking/response table.
- Behavioral detail lives in `.cursor/rules/30-exercise-generation.mdc`.
- No Python import of the skill at runtime.

**If prompts still mention pedagogical quality of “enunciado claro” without naming schema fields:**
- Prefer content adjectives without listing the three field names as a contract.
- Safer: “exercícios claros, com resolução passo a passo” without inventing an API.

**If light validation hooks are needed beyond existing validator:**
- Prefer assertions in tests + tiny pure functions next to `prompts.py` or `validator.py` (e.g. `assert_prompt_policy(system, user)` used by tests, optionally called in debug builds).
- Do not call LLM-as-judge for format.

**If AGENTS.md / GSD skills scan should surface the new skill:**
- Place under `skills/exercise-generation/` so it matches the existing `skills/` discovery path already used by `python-ai-engineering`.

---

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Existing openai + pydantic | Field `description` in schema | No upgrade required for schema-as-authority; descriptions already on `Exercise` fields. |
| Existing pytest | Custom markers (optional) | Register markers if used; otherwise skip — avoids UnknownMarkWarning. |
| Cursor rules `.mdc` | Skill `SKILL.md` frontmatter | Skill `name` / `description` for discovery; rule `description` for requestable load — no version pin. |

---

## Sources

- Context7 `/pydantic/pydantic` — `Field(description=…)` → `model_json_schema()` property descriptions (format metadata lives in schema, not prompt)
- Context7 `/pytest-dev/pytest` — optional custom marker registration (`markers`, `pytest_configure`)
- Repo: `skills/python-ai-engineering/SKILL.md`, `.cursor/rules/10-python.mdc`, `.cursor/rules/20-ai-engineering.mdc`, `exercise-ai/prompts.py`, `tests/test_prompts.py`, SEED-007, SEED-008, PROJECT.md v2.2
- Prior research: `.planning/research/STACK.md` (v2.1) — “add nothing” precedent for schema/docs milestones

---

*Stack research for: Domain AI generation contract + prompt hygiene (schema-as-authority)*
*Researched: 2026-09-23*
*Milestone: v2.2 Contrato de geração (SEED-007 + SEED-008)*
