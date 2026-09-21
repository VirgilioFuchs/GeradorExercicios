# Architecture Research

**Domain:** Python LLM pipeline — per-item dynamic batch specs on an existing embed seam
**Researched:** 2026-09-21
**Confidence:** HIGH

> Scope note: subsequent milestone (v2.1 / SEED-006). Integrate lotes dinâmicos into the
> **shipped** v2.0 architecture. Do not redesign the pipeline or widen the embed return type.
> Preserve `service.generate_batch(GenerationRequest) → ExerciseBatch` and the existing error
> kinds. Prefer extending models / prompts / validator / CLI over new services.

## Standard Architecture

### System Overview

v2.0 already established **library core + thin adapters**. v2.1 only deepens the **request
schema and the prompt/validator pair** so one call can describe a mixed batch. The seam,
failover envelope, RELY loop, and provider SDKs stay where they are.

```
┌──────────────────────────────────────────────────────────────────────┐
│                      PRESENTATION / ADAPTERS                          │
│                                                                       │
│  ┌──────────────┐   ┌──────────────┐          ┌───────────────────┐  │
│  │ main.main()  │   │  wizard.py   │          │ demo/ (optional)  │  │
│  │ + plan UX    │   │ + plan UX    │          │ form may stay     │  │
│  └──────┬───────┘   └──────┬───────┘          │ uniform in v2.1   │  │
│         │                  │                  └─────────┬─────────┘  │
│         └────────┬─────────┘                            │            │
│                  ▼                                      │            │
│         ┌──────────────────┐                            │            │
│         │   main.run()     │                            │            │
│         └────────┬─────────┘                            │            │
└──────────────────┼──────────────────────────────────────┼────────────┘
                   │                                      │
═══════════════════▼══════════════════════════════════════▼════════════  ← UNCHANGED SEAM
┌──────────────────────────────────────────────────────────────────────┐
│  service.generate_batch(GenerationRequest) → ExerciseBatch            │
│  ConfigError | InvalidRequestError | GenerationFailedError            │
│  owns: scoped env, begin_run/flush — signature unchanged              │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│  PIPELINE (same call graph; richer GenerationRequest payload)         │
│                                                                       │
│  failover.generate_with_failover                                      │
│       └─ reliability.generate_validated_batch  (RELY; same request)   │
│             ├─ generator / generator_gemini  (Structured Outputs)     │
│             │     └─ prompts.build_prompts(request)  ← MODIFIED       │
│             └─ validator.validate_exercise_batch     ← MODIFIED       │
│                   └─ math_check (unchanged semantics)                 │
│                                                                       │
│  models: GenerationRequest + optional per-item specs  ← MODIFIED      │
│  reasoning_effort: still run-level (env / --reasoning)                │
└──────────────────────────────────────────────────────────────────────┘
```

**Invariant (do not break):**

```
demo | main.run ──► service.generate_batch(request) ──► ExerciseBatch
Anything at/below service must not import main or wizard.
```

Hosts that build a uniform `GenerationRequest(dificuldade=…, quantidade=N)` keep working.
Hosts that pass an itemized plan use the same function and still receive `ExerciseBatch`.

### Component Responsibilities

| Component | Responsibility | v2.1 change |
|-----------|----------------|-------------|
| `models.py` | Request + response schemas; quantity bound | **MODIFIED** — add per-item spec; keep uniform path |
| `prompts.py` | System/user prompt from request | **MODIFIED** — mixed-plan branch |
| `validator.py` | Count + non-empty fields + math gate | **MODIFIED** — enforce plan length / per-item fields |
| `service.py` | Embed seam | **UNCHANGED** signature |
| `failover.py` / `reliability.py` | Failover + RELY | **UNCHANGED** (same `request` object) |
| `generator*.py` | Structured Outputs → `ExerciseBatch` | **UNCHANGED** call shape; may pick up new Exercise fields via schema |
| `reasoning.py` | API `reasoning_effort` (run-level) | **UNCHANGED** — not per exercise |
| `main.py` / `wizard.py` | Build `GenerationRequest`; present results | **MODIFIED** — plan UX → item list |
| `demo/` | Throwaway host | **OPTIONAL** — uniform form still valid; extend only if discuss asks |

## Recommended Project Structure

No new packages or services. Flat `exercise-ai/` stays.

```
exercise-ai/
├── models.py           # MODIFIED — ExerciseSpec (+ optional Exercise metadata)
├── prompts.py          # MODIFIED — uniform vs itemized user prompt
├── validator.py        # MODIFIED — plan-aware checks
├── service.py          # UNCHANGED public API
├── failover.py         # UNCHANGED
├── reliability.py      # UNCHANGED
├── generator.py        # UNCHANGED (schema-driven)
├── generator_gemini.py # UNCHANGED
├── reasoning.py        # UNCHANGED (API effort stays run-level)
├── main.py             # MODIFIED — plan / cap UX
├── wizard.py           # MODIFIED — batch plan step
└── tests/              # MODIFIED — models, prompts, validator, CLI/wizard
```

### Structure Rationale

- **Extend at the schema boundary.** Per-item control is request data. Putting it in
  `GenerationRequest` keeps `generate_batch` stable and avoids a second entry point
  (`generate_dynamic_batch`, planner service, etc.).
- **Prompt and validator are the only pipeline leaves that must “understand” the plan.**
  Generators already pass `request` into `build_prompts` and `response_format=ExerciseBatch`;
  RELY already retries with the **same** request. Mixed batches inherit failover/RELY for free.
- **CLI/wizard stay adapters.** They expand a human plan (“2 fáceis + 3 médios”) into
  `itens` / derived `quantidade`, then call the same seam.
- **No chunking module in v2.1.** Cap review may raise `MAX_QUANTIDADE`; multi-call chunking is
  YAGNI until context/cost forces it (SEED-006 Slice D as discuss, not a new service by default).

## Architectural Patterns

### Pattern 1: Optional itemized plan on the same request (backward-compatible)

**What:** Keep the uniform fields (`dificuldade`, `quantidade`) and add an optional list of
per-exercise specs. When the list is absent/empty, behaviour equals v2.0. When present, the
list is the source of truth for length and per-item difficulty (and optional pedagogical
reasoning type).

**When to use:** product needs mixed batches without breaking existing hosts/tests.

**Trade-offs:** one model carries two modes — must enforce mutual consistency with a Pydantic
model validator. Cleaner than a parallel request type that would force hosts to branch on
function choice.

**Example (sketch — names finalize in discuss/plan):**

```python
# models.py — extend, do not replace GenerationRequest

class ExerciseSpec(BaseModel):
    dificuldade: DificuldadeEnum
    tipo_raciocinio: str | None = None  # pedagogical; optional until taxonomy locked

class GenerationRequest(BaseModel):
    materia: str = "Matemática"
    topico: str
    dificuldade: DificuldadeEnum          # required for uniform; default/fill when itens set
    quantidade: int = Field(..., ge=1, le=MAX_QUANTIDADE)
    itens: list[ExerciseSpec] | None = None

    @model_validator(mode="after")
    def _align_plan(self) -> Self:
        if self.itens:
            if len(self.itens) != self.quantidade:
                raise ValueError("quantidade deve igualar len(itens)")
            if len(self.itens) > MAX_QUANTIDADE:
                raise ValueError(...)
        return self
```

Uniform callers omit `itens`. Wizard/CLI set `itens` and set `quantidade = len(itens)`.

### Pattern 2: Dual-mode prompt builder (same function)

**What:** `build_prompts(request)` already is the single prompt gate. Branch inside it:
uniform template (today) vs an itemized plan that enumerates expected difficulty (and optional
tipo) per index.

**When to use:** LLM must emit N exercises matching a heterogeneous plan in one Structured
Outputs call.

**Trade-offs:** longer prompts and harder validation when N grows; still one API call and one
RELY loop — matches “IA poder trabalhar com mais quantidade” without a planner agent.

**Example:**

```python
def build_prompts(request: GenerationRequest) -> tuple[str, str]:
    if request.itens:
        plan_lines = "\n".join(
            f"  {i+1}. dificuldade={s.dificuldade.value}"
            + (f"; tipo_raciocinio={s.tipo_raciocinio}" if s.tipo_raciocinio else "")
            for i, s in enumerate(request.itens)
        )
        user = MIXED_USER_TEMPLATE.format(
            materia=request.materia,
            topico=request.topico,
            quantidade=request.quantidade,
            plan=plan_lines,
        )
        return SYSTEM_PROMPT_MIXED, user
    # existing uniform path
    ...
```

### Pattern 3: Validate against the request plan (not a second schema path)

**What:** After Structured Outputs parse, `validate_exercise_batch(batch, request)` already
compares `len(exercicios)` to `request.quantidade`. Extend that comparison: when `itens` is
set, also check per-index fields the model is required to echo (recommended: optional
`dificuldade` on `Exercise` so the schema forces alignment).

**When to use:** mixed batches where count-only checks would accept “5 mediums” for a
2+3 plan.

**Trade-offs:** adding fields to `Exercise` changes the Structured Outputs schema (providers
must accept the new properties). Prefer **additive optional/required fields on `Exercise`**
over a separate response type — keeps `response_format=ExerciseBatch` and the embed return
identical. If discuss rejects output metadata, validate only length + non-empty text and rely
on the prompt (weaker; document as risk).

**Example:**

```python
# validator — additive checks when request.itens is set
if request.itens:
    for i, (ex, spec) in enumerate(zip(batch.exercicios, request.itens, strict=True)):
        if getattr(ex, "dificuldade", None) != spec.dificuldade:
            errors.append(f"exercicios[{i}].dificuldade != plano")
```

Math check stays batch-wide; no per-item math policy in v2.1.

### Pattern 4: Separate pedagogical “tipo de raciocínio” from API `reasoning_effort`

**What:** SEED-006 Slice C. Operator “tipo de raciocínio” is a **content/pedagogy** hint in
the plan/prompt (and optionally on `Exercise`). Provider `reasoning_effort` / Gemini thinking
level remains **run-scoped** via `LLM_REASONING_EFFORT` / `--reasoning` / service env scope —
providers do not expose per-item effort in this stack.

**When to use:** always in v2.1 design discussions; do not invent per-item API effort.

**Trade-offs:** one API cost knob for the whole mixed batch (harder items get the same effort
as easy ones). Acceptable for MVP; revisit only if cost/quality data demands chunking by
difficulty (out of scope unless discuss promotes it).

## Data Flow

### Request flow (uniform — unchanged)

```
Host/CLI
  → GenerationRequest(dificuldade, quantidade, itens=None)
  → service.generate_batch
  → Prompt (uniform) → LLM → Failover → Validate(count) → math → RELY
  → ExerciseBatch
```

### Request flow (mixed — v2.1)

```
Operator plan UX ("2 facil + 3 medio" [+ tipos])
  → list[ExerciseSpec] + quantidade=len(itens)
  → GenerationRequest(..., itens=[...])
  → service.generate_batch          ← SAME SEAM
  → Prompt (itemized plan) → LLM Structured Outputs → ExerciseBatch
  → validate: len + per-item alignment (+ math)
  → RELY regenerates with SAME request/plan
  → ExerciseBatch | InvalidRequestError | …
```

### Key data flows

1. **Plan expansion (adapter-only):** wizard/CLI parse a compact plan into `itens`; domain
   rules (bounds, enum values) live in Pydantic, not argparse alone.
2. **Single-shot mixed generation:** one Structured Outputs call returns the full list; no
   N×`generate_batch` fan-out (would multiply failover/RELY and break “one batch” semantics).
3. **RELY identity:** regeneration must not drop or reshuffle the plan — pass the same
   `GenerationRequest` object (already true in `generate_validated_batch`).

### State management

No new process state. Token buffer, scoped env, and math postmortem ownership remain as in
v2.0 (`service` brackets begin/flush; adapters may flush again).

## Scaling Considerations

Not multi-tenant. Honest limits for larger/mixed lots:

| Pressure | What breaks | v2.1 stance |
|----------|-------------|-------------|
| Batch size / context | Truncation, weaker schema adherence | Review `MAX_QUANTIDADE` (40); raise modestly or keep; **no** chunking service by default |
| Cost / latency | Tokens scale with N and prompt plan length | Keep run-level reasoning; OBS-01 still parked |
| Validation strictness | More fields → more RELY exhaustions | Bounded retries unchanged (0–3); fail with `InvalidRequestError` |
| Concurrency | Still sequential at the seam | Unchanged |

### Scaling Priorities

1. **First bottleneck:** LLM context + schema adherence on large mixed plans → tighten prompt
   + validator; consider cap, not a new orchestrator.
2. **Second bottleneck:** cost of high run-level reasoning on mostly-easy batches → document;
   do not add per-item API effort in v2.1.

## Anti-Patterns

### Anti-Pattern 1: New `generate_dynamic_batch` / planner service

**What people do:** add a second public function or a “BatchPlanner” microservice.

**Why it's wrong:** splits the embed contract; hosts and demo must learn two paths; duplicates
failover/RELY ownership.

**Do this instead:** extend `GenerationRequest` + keep `generate_batch`.

### Anti-Pattern 2: N sequential LLM calls (one per difficulty)

**What people do:** loop `generate_batch` per group and concatenate.

**Why it's wrong:** multiplies RELY/failover, breaks atomic batch validation, complicates
usage attribution, and is not needed for Structured Outputs list schemas.

**Do this instead:** one call with an itemized prompt and list response.

### Anti-Pattern 3: Per-item `reasoning_effort` in the request

**What people do:** put API effort on `ExerciseSpec` and try to vary SDK kwargs mid-batch.

**Why it's wrong:** one completion = one effort parameter; fake per-item effort misleads
operators and requires chunking.

**Do this instead:** pedagogical `tipo_raciocinio` in the plan/prompt; keep API effort run-level.

### Anti-Pattern 4: Enforcing the plan only in the CLI

**What people do:** wizard builds mixed prompts as free text but `GenerationRequest` stays
uniform; library hosts cannot express the plan.

**Why it's wrong:** repeats the pre-v2.0 quantity-bound mistake (domain rule only on one path).

**Do this instead:** plan is first-class on `GenerationRequest`; CLI is just a builder.

### Anti-Pattern 5: Widening the embed return (`tuple[Batch, Plan, Usage]`)

**What people do:** change `generate_batch` return for observability or echoed specs.

**Why it's wrong:** breaks v2.0 hosts (EMBED-01). OBS-01 is parked.

**Do this instead:** keep `→ ExerciseBatch`; put echoed difficulty on `Exercise` fields if
needed for validation/UX.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| OpenAI / Grok / Gemini | Existing Structured Outputs / JSON schema via `ExerciseBatch` | Additive `Exercise` fields regenerate provider schemas automatically; pin models that support strict schema |
| Host embed | `generate_batch(GenerationRequest)` | Contract preserved; optional `itens` is additive |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Adapters → `service` | `GenerationRequest` in / `ExerciseBatch` out | Unchanged types at the seam |
| `service` → failover → RELY | same `request` | No signature change |
| RELY → generators | `build_prompts(request)` | Prompt must reflect `itens` |
| RELY → validator | `(batch, request)` | Validator must read `itens` when set |
| `reasoning.py` ↔ plan | none | Deliberate separation (API vs pedagogy) |

### New vs modified (explicit)

| Kind | Component | Role |
|------|-----------|------|
| **New type (in `models.py`)** | `ExerciseSpec` (name TBD) | Per-item dificuldade + optional tipo pedagógico |
| **Modified** | `GenerationRequest` | Optional `itens`; validators align `quantidade` |
| **Modified (recommended)** | `Exercise` | Echo `dificuldade` (and optional tipo) for schema+validator |
| **Modified** | `prompts.py` | Mixed-plan templates + branch in `build_prompts` |
| **Modified** | `validator.py` | Plan-aware checks |
| **Modified** | `main.py`, `wizard.py` | Plan UX; shared cap constant |
| **Modified** | tests for the above | Offline unit tests; no live LLM |
| **Unchanged** | `service.py` public signature, failover, RELY loop, generators’ call shape, `reasoning.py` | Preserve embed + ops contracts |
| **Optional** | `demo/` form | Uniform still valid; extend only if needed for acceptance |
| **Avoid** | New service modules, chunk orchestrator, second public generate API | YAGNI |

### Suggested build order

Dependency order (schema → prompt → validate → UX → cap):

```
1. models (ExerciseSpec + GenerationRequest.itens [+ Exercise echo fields])
        │
        ├─► 2. prompts.build_prompts mixed branch
        │         │
        │         └─► 3. validator plan checks (+ existing math)
        │                   │
        └───────────────────┴─► 4. CLI/wizard plan UX (builders only)
                                      │
                                      └─► 5. Cap review (MAX_QUANTIDADE) + regression suite
                                            (+ optional demo)
```

| # | Step | New / Modified | Depends on | Why this order |
|---|------|----------------|------------|----------------|
| 1 | Schema: `ExerciseSpec`, optional `itens`, align `quantidade`; optional `Exercise.dificuldade` | MOD `models.py` + model tests | — | Everything else reads the plan from the request/response types |
| 2 | Prompt: itemized user/system branch; keep uniform path bit-compatible | MOD `prompts.py` + prompt tests | 1 | Generators already call `build_prompts`; no generator edits required |
| 3 | Validator: length + per-item alignment when `itens` set; RELY still works | MOD `validator.py` + validator tests | 1 (2 for e2e realism) | Fail closed on mixed lots before UX invents plans |
| 4 | CLI/wizard: plan shorthand → `itens`; argparse/wizard stay adapters | MOD `main.py`, `wizard.py` + tests | 1–3 | Presentation last so domain rules are already enforced in-library |
| 5 | Cap / docs: revisit `MAX_QUANTIDADE`; README embed note that `itens` is additive | MOD models/main/wizard constants | 1–4 | Avoid raising cap before prompt/validator prove mixed lots |

**Preserve embed contract checklist:** same function name; same return type; uniform requests
without `itens` behave as v2.0; errors remain `ConfigError` / `InvalidRequestError` /
`GenerationFailedError`; no `sys.exit` below `main.run`.

## Constraint Check

1. **YAGNI:** no agent, no RAG, no FastAPI, no chunk service unless discuss proves a hard
   context limit.
2. **LLM is not source of truth:** mixed plan must be checked in `validator.py`, not only
   prompted.
3. **Testability:** plan expansion and validator tests stay offline (fixtures with fake
   batches).
4. **Discuss still open:** exact name/taxonomy of “tipo de raciocínio”; whether `Exercise`
   must echo difficulty; final cap number — architecture allows all three without seam changes.

## Confidence Summary

| Finding | Confidence | Basis |
|---------|-----------|-------|
| Keep `generate_batch` → `ExerciseBatch` | HIGH | PROJECT.md Key Decisions; shipped v2.0 |
| Optional `itens` on `GenerationRequest` is smallest integration | HIGH | SEED-006 Slice A; current models/prompts/validator touchpoints |
| Prompt + validator are the only required pipeline edits | HIGH | `build_prompts` + `validate_exercise_batch` are the sole request-aware leaves |
| API reasoning stays run-level | HIGH | `reasoning.py` / service scoped env; SEED-006 Slice C |
| Avoid N-call fan-out and new services | HIGH | YAGNI + existing RELY/failover design |
| Echo difficulty on `Exercise` for validation | MEDIUM | Strongest check; discuss may prefer prompt-only |
| Cap raise without chunking | MEDIUM | Product ask vs context risk — finalize in discuss |

## Sources

- `.planning/PROJECT.md` — v2.1 goal, pipeline diagram, embed contract decisions
- `.planning/seeds/SEED-006-dynamic-batch-per-exercise.md` — slices A–E, breadcrumbs
- `exercise-ai/models.py`, `service.py`, `prompts.py`, `validator.py`, `failover.py`, `reliability.py`
- Prior research `.planning/research/ARCHITECTURE.md` (v2.0 embed, 2026-09-16) — seam invariants reused
- AGENTS.md / STACK — Structured Outputs + Pydantic, no agent frameworks

---
*Architecture research for: dynamic per-item exercise batches on existing GenerationRequest → ExerciseBatch pipeline*
*Researched: 2026-09-21*
