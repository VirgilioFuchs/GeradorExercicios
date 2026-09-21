# Stack Research

**Domain:** LLM exercise generation / dynamic mixed-difficulty batches (per-item specs)
**Researched:** 2026-09-21
**Confidence:** HIGH

---

## Headline

**For v2.1 the correct stack addition is: nothing new in `requirements.txt`.** Mixed batches, per-item difficulty, pedagogical reasoning type, larger caps, and batch-plan CLI/wizard UX are all schema + prompt + validator + argparse/wizard work on the existing Pydantic v2 + Structured Outputs pipeline. Keep `openai`, `google-genai`, `pydantic`, `python-dotenv`, `pytest` unchanged; extend models and validation with nested list types already proven by the SDK and Context7 docs.

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.11+ (CI pin 3.11) | Runtime | Already validated through v2.0; nested typing + enums suffice for per-item specs. |
| pydantic | ≥2.0 (keep pin) | Request/response schemas + validators | Nested `list[ItemModel]`, `Field(min_length/max_length)`, `@model_validator`, and `str, Enum` map cleanly to OpenAI/Gemini JSON schema. Single source of truth for request plan + output echo fields. |
| openai | ≥1.50 (keep pin) | Structured Outputs via `chat.completions.parse(response_format=…)` | Nested `list[BaseModel]` is first-class (SDK helpers + cookbook). Same `ExerciseBatch` pattern; enrich item fields, do not change client stack. |
| google-genai | ≥1.0 (keep pin) | Gemini path: `response_json_schema=ExerciseBatch.model_json_schema()` | Schema still derived from the same Pydantic models; nested lists/enums continue to work without a second schema DSL. |
| python-dotenv | ≥1.0 (keep pin) | Env config | Unchanged; `LLM_REASONING_EFFORT` stays **run-level**, not per-item. |

**Nothing is added to `exercise-ai/requirements.txt` for this milestone.**

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `argparse` (stdlib) | stdlib | CLI flags for batch plan / uniform fallback | Extend existing `main.py` — e.g. `--plano "2f,3m,1d"` or repeated `--item` — without Click/Typer. |
| `re` / string split (stdlib) | stdlib | Parse compact batch-plan tokens | Wizard/CLI plan shorthand; keep parser tiny and unit-tested. |
| `enum.Enum` (stdlib) | stdlib | `DificuldadeEnum` + new pedagogical `TipoRaciocinio` (or similar) | Pedagogical taxonomy ≠ API `reasoning_effort`. Separate enums prevent conflating cost/model knobs with exercise pedagogy. |
| Existing `reasoning.py` | in-repo | Map `none\|low\|medium\|high` → OpenAI/Gemini | **Keep run-level only.** Providers do not expose reliable per-item `reasoning_effort` in this lab’s multi-provider setup. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| pytest ≥8.0 | Offline unit tests | Mock LLM; assert plan expansion, length-vs-spec, per-item field echo, backward-compatible uniform request. |
| GitHub Actions (existing) | CI without secrets | No new deps → CI install line unchanged. |

---

## Installation

```bash
# v2.1 adds nothing. Existing install remains the contract:
pip install -r exercise-ai/requirements.txt
```

---

## Integration Points (existing layout)

| Seam | v2.1 change (stack-neutral) |
|------|-----------------------------|
| `models.py` | Add nested **item spec** model(s); optional `itens`/`plano` on `GenerationRequest`; optionally echo `dificuldade` / pedagogical type on `Exercise` so the validator can align output to the plan. Keep `MAX_QUANTIDADE` as a single constant (raise carefully). |
| `prompts.py` | Render mixed plan (counts per level + per-item reasoning type) instead of one global dificuldade string. |
| `validator.py` | Beyond `len(exercicios) == quantidade`: check multiset of difficulties (and types) vs plan; reuse `Field`/`model_validator` where structural, keep semantic checks offline-testable. |
| `generator.py` / `generator_gemini.py` | Still `response_format=ExerciseBatch` / `model_json_schema()` — **no new client libs**. Larger payloads may need **sequential chunk orchestration** in service/generator (stdlib loops), not a batch SDK. |
| `reasoning.py` + CLI `--reasoning` | Remains global cost/quality knob. Document clearly vs pedagogical per-item field. |
| `main.py` / `wizard.py` | Batch-plan UX: compact string or interactive “N fáceis + M médios…”; expand to specs before `GenerationRequest`. |
| `service.generate_batch` | Same signature shape preferred: still `GenerationRequest` → `ExerciseBatch`. Enrich request model; do not widen return for OBS-01. |

---

## Schema Patterns (verified)

**Nested list Structured Outputs (OpenAI + Pydantic)** — Context7 `/openai/openai-python`: `chat.completions.parse(response_format=MathResponse)` where `MathResponse.steps: list[Step]` works today; same pattern as `ExerciseBatch.exercicios: list[Exercise]`.

**Parent–child validation** — Context7 `/pydantic/pydantic`: `@model_validator(mode='after')` on the parent can enforce cross-field rules (e.g. plan length ≡ `quantidade`, or forbidden mismatches). Prefer this over a new validation framework.

**List bounds** — `Field(min_length=…, max_length=…)` on `list[…]` maps to schema constraints; raise `MAX_QUANTIDADE` here and in CLI in lockstep.

**Enums in strict schema** — OpenAI Structured Outputs support `enum` / arrays / nested objects; use `str, Enum` for dificuldade and pedagogical reasoning type so Gemini `model_json_schema()` and OpenAI parse stay aligned.

**Recommended shape (conceptual — not prescribing final names):**

```text
GenerationRequest
  materia, topico
  dificuldade?          # uniform mode (backward compatible)
  quantidade            # = len(specs) when mixed
  itens: list[ExerciseSpec]?   # mixed mode: dificuldade + optional tipo_raciocinio

Exercise  (output)
  enunciado, resposta, explicacao
  dificuldade? / tipo_raciocinio?   # echo for validator alignment (discuss-phase)

ExerciseSpec
  dificuldade: DificuldadeEnum
  tipo_raciocinio?: PedagogicalEnum   # NOT API reasoning_effort
```

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Nested Pydantic models on existing `ExerciseBatch` | Separate LLM call per difficulty group | Only if a single call truncates or fails schema at higher caps; implement as **sequential chunks** in-process, still same stack. |
| Compact `--plano` string + wizard prompts | Click / Typer / Rich TUI | Never for this lab — argparse + existing `gerar` wizard already ship; richer TUI is YAGNI. |
| Pedagogical enum on request/output | Overloading `LLM_REASONING_EFFORT` / `--reasoning` per item | Only if discuss-phase proves providers gain true per-item effort **and** all three providers support it; today they do not uniformly — keep effort run-level. |
| Raise `MAX_QUANTIDADE` + one-shot generate | OpenAI Batch API / async job queue | Out of scope; sequential sync contract is a project constraint. |
| Hand-written JSON Schema dicts | Keep Pydantic as schema source | Only if a provider rejects a Pydantic-generated construct; fix the model, don’t fork a second schema. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| LangChain / CrewAI / AutoGen / PydanticAI | Agent frameworks hide the lab’s learning goals; forbidden by PROJECT.md | Plain SDK + modules |
| `instructor` / extra structured-output wrappers | Duplicates `openai` `.parse()` + Gemini schema path | Existing dual-provider generators |
| Click, Typer, questionary, Rich | New UX deps for a small plan parser | `argparse` + `wizard.py` |
| Packaging / `pyproject.toml` (PKG-01) | Explicitly parked until after v2.1 | Current `exercise-ai/` layout |
| OBS-01 usage in return / LOG-01 print→logging | Out of milestone scope | Existing `[USAGE]` NDJSON / stderr prints |
| Images, BNCC, FastAPI/Flask/Streamlit | Out of scope seeds / product HTTP | Embed + throwaway demo already shipped |
| Concurrent/async chunk pools | Contract is sequential; complexity without requirement | Optional **sequential** chunk loop if cap forces it |
| Per-item API `reasoning_effort` as the “tipo de raciocínio” field | Conflates pedagogy with provider cost knobs; multi-provider mismatch | Separate pedagogical enum; keep `reasoning.py` global |

---

## Stack Patterns by Variant

**If request is uniform (legacy CLI: one dificuldade + quantidade):**
- Keep current `GenerationRequest` fields as the default path.
- Internally expand to N identical specs **or** leave prompt as today — discuss-phase chooses; either way, no new library.

**If request is mixed (batch plan):**
- Represent plan as `list[ExerciseSpec]` (or counts expanded to specs).
- Prompt lists the required multiset; validator checks length + per-index or multiset match.
- Output should carry enough echoed fields for offline validation without re-calling the LLM.

**If quantidade grows beyond reliable one-shot context/schema:**
- Prefer raising cap modestly first (e.g. toward exams-sized sets) with measurements via existing token NDJSON.
- If failures appear: **chunk by contiguous specs**, concatenate `ExerciseBatch.exercicios`, validate the merged batch against the full plan — still stdlib orchestration, same providers.

**If “tipo de raciocínio” is pedagogical only (expected default):**
- New enum on specs/exercícios; do not plumb into `openai_compatible_effort_kwargs` / Gemini `thinking_level`.
- Keep `--reasoning` / env as the single run-level effort control.

**If discuss-phase demands both pedagogy and API effort per item:**
- Still avoid new deps; effort would need provider capability matrix and likely **chunk-by-effort** sequential calls. Treat as stretch; default stack research says **do not**.

---

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| openai ≥1.50 | pydantic ≥2.0 | `.parse(response_format=Model)` requires this pairing; nested lists already used by this repo. |
| google-genai ≥1.0 | pydantic ≥2.0 `model_json_schema()` | Nested enums/lists must stay JSON-Schema-subset friendly (no exotic Pydantic constraints that break Gemini). Prefer `str, Enum` + required fields. |
| Structured Outputs (strict) | Nested objects, arrays, enums | Supported types include Object, Array, Enum; avoid unsupported JSON Schema features when enriching `Exercise`. |
| pytest ≥8 | No LLM live | Plan parser + validator tests stay offline. |

---

## Sources

- Context7 `/pydantic/pydantic` — nested `list[Model]`, `@model_validator(mode='after')`, `Field(min_length/max_length)` on lists, `Annotated` inner constraints, `TypeAdapter(list[Item])`
- Context7 `/openai/openai-python` — `chat.completions.parse(response_format=…)` with nested `List[Step]` Pydantic models
- Context7 `/openai/openai-cookbook` — structured batch-style list responses; nested company/list schemas
- Context7 `/websites/developers_openai_api` — Structured Outputs supported types (Object, Array, Enum); strict schema nested arrays
- Repo: `exercise-ai/models.py`, `validator.py`, `reasoning.py`, `prompts.py`, `requirements.txt`, SEED-006, PROJECT.md v2.1 scope
- Prior research: `.planning/research/STACK.md` (v2.0) — “add nothing” precedent for schema-only milestones

---

*Stack research for: LLM exercise generation / dynamic mixed-difficulty batches*
*Researched: 2026-09-21*
*Milestone: v2.1 Lotes dinâmicos (SEED-006)*
`)