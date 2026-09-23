# Architecture Research

**Domain:** Python LLM pipeline — domain AI generation contract (persona / authority split) on shipped embed seam
**Researched:** 2026-09-23
**Confidence:** HIGH

> Scope note: milestone **v2.2 Contrato de geração** (SEED-007 + SEED-008). Layer an
> **agent-facing skill/rules contract** and a **prompt content layer** onto the shipped v2.1
> pipeline. Do **not** redesign RELY, failover, the embed seam, or `math_check`. Do **not**
> introduce a second validation agent. Prefer new docs/skills/rules + prompt edits + thin
> offline assert helpers over new services.

## Standard Architecture

### System Overview

v2.1 already ships **library core + thin adapters** with mixed/uniform plans, slot prompts,
`verify_plan_echo`, and bounded RELY. v2.2 adds two **orthogonal** surfaces:

1. **Agent-facing contract** — skill + Cursor rules so GSD/agents respect authority and pipeline order.
2. **Prompt content layer** — persona/pedagogy/topic guidance only; format and plan stay code-owned.

Runtime call graph below `service.generate_batch` stays the same.

```
┌──────────────────────────────────────────────────────────────────────────┐
│              AGENT / DEV CONTRACT (NEW — not on the hot path)             │
│  skills/exercise-generation/SKILL.md  →  .cursor/rules/*-exercise*.mdc   │
│  Authority map: FORMAT | PLAN | CONTENT | THINKING                       │
│  “Follow pipeline order; do not invent a validation agent”               │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │ guides humans/agents editing prompts/code
                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      PRESENTATION / ADAPTERS (unchanged)                  │
│  main / wizard / demo  →  GenerationRequest (uniforme | plano | itens)   │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
═════════════════════════════════▼═════════════════════════════════════════  ← UNCHANGED SEAM
┌──────────────────────────────────────────────────────────────────────────┐
│  service.generate_batch(GenerationRequest) → ExerciseBatch                │
│  ConfigError | InvalidRequestError | GenerationFailedError                │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────────────────┐
│  PIPELINE (same call graph; prompt text + tests change)                   │
│                                                                           │
│  failover → reliability.generate_validated_batch  (RELY — UNCHANGED)      │
│       ├─ generator*  (Structured Outputs → ExerciseBatch)  ← FORMAT       │
│       │     └─ prompts.build_prompts(request)  ← CONTENT (MODIFIED text)  │
│       └─ validate_exercise_batch (+ math_check) → verify_plan_echo        │
│             └─ PLAN authority (code) — UNCHANGED ownership                │
│                                                                           │
│  reasoning_effort / thinking level  ← THINKING (API knob, run-level)      │
└──────────────────────────────────────────────────────────────────────────┘
```

**Invariant (do not break):**

```
demo | main.run ──► service.generate_batch(request) ──► ExerciseBatch
Anything at/below service must not import main or wizard.
Skills/rules must not become a second runtime validation path.
```

### Authority map (v2.2 core)

| Concern | Authority | Lives in | Prompt role |
|---------|-----------|----------|-------------|
| **FORMAT** | Schema + Structured Outputs | `models.py` (`Exercise` / `ExerciseBatch`) + `generator*.py` `response_format` | Must **not** redefine field trees or invent JSON keys |
| **PLAN** | Ordered slots + echo check | `GenerationRequest.itens_ordenados` + `verify_plan_echo` (+ count in validator) | May cue slot difficulty / band summary; does **not** replace echo |
| **CONTENT** | Best-effort pedagogy | `prompts.py` (system persona + user topic/slots) | Tom PT-BR, tópico, dificuldade por slot — LLM may still drift |
| **THINKING** | Provider API knob | `reasoning.py` / env / `--reasoning` | Not an `Exercise` field; not “tipo pedagógico” |

Validation (structural emptiness, math_check, plan echo) remains **deterministic code** after the LLM returns. RELY regenerates with the **same** `GenerationRequest`; it is not redesigned.

### Component Responsibilities

| Component | Responsibility | v2.2 change |
|-----------|----------------|-------------|
| `skills/exercise-generation/SKILL.md` (or similar) | Agent index: persona, capabilities, pipeline order, pointers to rules | **NEW** |
| `.cursor/rules/*-exercise-generation*.mdc` | Authoritative domain rules (validation ≠ thinking ≠ response) | **NEW** |
| `prompts.py` | CONTENT only: persona + topic/slot cues | **MODIFIED** — strip field-contract prose; align to skill |
| `models.py` | FORMAT + PLAN types; `verify_plan_echo` | **UNCHANGED** ownership (docs may reference) |
| `validator.py` / `math_check.py` | Code-owned checks | **UNCHANGED** ownership; optional thin test helpers only |
| `reliability.py` | RELY loop order: generate → validate → echo | **UNCHANGED** |
| `reasoning.py` | THINKING / API effort | **UNCHANGED** — keep out of Exercise schema |
| `service.py` / failover / generators | Embed seam + providers | **UNCHANGED** |
| `tests/test_prompts.py` (+ optional helpers) | Offline policy: no field-schema dump; persona markers | **MODIFIED** / light **NEW** asserts |
| `main` / `wizard` / `demo` | Adapters | **UNCHANGED** for v2.2 default scope |

## Recommended Project Structure

No new runtime packages. Flat `exercise-ai/` stays; contract artifacts live beside existing engineering skill/rules.

```
skills/
├── python-ai-engineering/SKILL.md   # UNCHANGED — generic Python/AI engineering
└── exercise-generation/SKILL.md     # NEW — domain generation contract (index)

.cursor/rules/
├── 10-python.mdc                    # UNCHANGED
├── 20-ai-engineering.mdc            # UNCHANGED
└── 30-exercise-generation.mdc       # NEW — domain authority + persona (name TBD)

exercise-ai/
├── prompts.py                       # MODIFIED — CONTENT layer only
├── models.py                        # UNCHANGED (FORMAT + PLAN)
├── validator.py                     # UNCHANGED (optional shared assert helpers for tests)
├── math_check.py                    # UNCHANGED — no overhaul
├── reliability.py                   # UNCHANGED — no RELY redesign
├── reasoning.py                     # UNCHANGED — THINKING
├── service.py / failover / generator*  # UNCHANGED
└── tests/
    ├── test_prompts.py              # MODIFIED — SEED-008 policy + persona markers
    └── (optional) test_contract_*.py  # thin offline asserts mirroring authority map

docs/                                # OPTIONAL — RESPONSE-CONTRACT.md only if discuss wants host-facing copy
```

### Structure Rationale

- **Skill mirrors `python-ai-engineering`.** Index file points at authoritative rules; GSD applies during plan/execute/review without running another agent at generation time.
- **Rules own the domain contract; prompts own CONTENT.** Avoid duplicating long rule text into `SYSTEM_PROMPT` — prompt stays short and pedagogical; agents read the rule file.
- **FORMAT/PLAN stay in code.** Phase 14 already removed `enunciado:` / `resposta:` / `explicacao:` from the **user** prompt; v2.2 finishes the job on **system** prose that still lists those fields as if they were a prompt contract.
- **Thin test helpers, not a second validator.** Shared string/marker asserts (e.g. “prompt must not contain field-schema dump”) keep policy testable offline without changing RELY or `math_check`.

## Architectural Patterns

### Pattern 1: Dual-audience contract (agents vs runtime)

**What:** Ship a skill + rule for **developers/agents**, and keep the **runtime** path as today: hosts → `generate_batch` → prompts → LLM → code validation.

**When to use:** always for SEED-007 — persona and “how the model should behave” must be discoverable by GSD without becoming a LangChain agent.

**Trade-offs:** two documents (skill + rule) can drift from `prompts.py`. Mitigate with offline tests that lock critical prompt markers and a skill section that says “runtime CONTENT source of truth is `prompts.py`.”

**Example:**

```markdown
# skills/exercise-generation/SKILL.md
Before changing exercise generation, read:
- `.cursor/rules/30-exercise-generation.mdc`
- `exercise-ai/prompts.py` (CONTENT)
- `exercise-ai/models.py` (FORMAT + PLAN echo)

Do not add a validation agent. Validation is code after the LLM.
```

### Pattern 2: Schema-as-format-authority (strip prompt field contracts)

**What:** `Exercise` / `ExerciseBatch` + Structured Outputs define shape. Prompts describe **what to write about** (tópico, faixa, tom), not the JSON tree.

**When to use:** any prompt edit (SEED-008); any future field (BNCC, images) — schema first, prompt second.

**Trade-offs:** shorter prompts may feel “less controlling”; adherence comes from schema + `verify_plan_echo` + RELY, which is the project constraint (*LLM is not source of truth*).

**Example (direction for SYSTEM_PROMPT):**

```python
# CONTENT — persona + pedagogy; no enunciado/resposta/explicacao field contract
SYSTEM_PROMPT = (
    "Você é um professor especialista em exercícios de matemática (Brasil). "
    "Gere exercícios didáticos, precisos e adequados às faixas de dificuldade do plano. "
    "Respeite estritamente o tópico. "
    "Não acrescente textos fora do formato estruturado solicitado pela API."
)
# Field names remain only on Exercise / response_format — not duplicated here.
```

### Pattern 3: Explicit concern split (validation / thinking / response)

**What:** Document and enforce naming so agents do not conflate:

- **Response** = `enunciado` / `resposta` / `explicacao` (+ echo `dificuldade`) on `Exercise`
- **Thinking** = `reasoning_effort` (run-level API)
- **Validation** = `validate_exercise_batch` + `math_check` + `verify_plan_echo` + RELY

**When to use:** skill/rules body; discuss locks single persona for v2.2 (multiple personas = YAGNI).

**Trade-offs:** one professor persona only until product asks for variants; pedagogical “tipo de raciocínio” stays deferred (TIPO-OPEN), separate from THINKING.

### Pattern 4: Light policy assertions (tests, not runtime agents)

**What:** Extend offline prompt tests (already assert absence of `enunciado:` etc. in user prompt) to cover system prompt and optional shared helpers.

**When to use:** after prompt rewrite; CI already runs without live LLM.

**Trade-offs:** marker tests are brittle if Portuguese copy changes often — keep asserts on **forbidden patterns** (field-schema dumps, “valide você mesmo”) more than on full golden strings.

**Example:**

```python
FORBIDDEN_FORMAT_MARKERS = ("enunciado:", "resposta:", "explicacao:", '"exercicios"')

def assert_prompt_is_content_not_schema(system: str, user: str) -> None:
    blob = f"{system}\n{user}".lower()
    for m in FORBIDDEN_FORMAT_MARKERS:
        assert m not in blob
```

Prefer putting helpers in `tests/` (or a tiny `prompts` test util) — **not** a new production validation stage.

## Data Flow

### Request flow (runtime — unchanged topology)

```
Host/CLI/wizard/demo
  → GenerationRequest (uniforme | plano | itens)
  → service.generate_batch
  → prompts.build_prompts          ← CONTENT (v2.2 text)
  → LLM Structured Outputs         ← FORMAT enforced by schema
  → failover
  → validate_exercise_batch (+ math_check)
  → verify_plan_echo               ← PLAN
  → RELY (same request) | ExerciseBatch | typed errors
```

`reasoning_effort` is applied at generation time via env/API kwargs (THINKING); it never appears as an Exercise field.

### Agent / edit flow (new — documentation path)

```
GSD plan/execute/review
  → skills/exercise-generation/SKILL.md
  → .cursor/rules/30-exercise-generation.mdc  (authority map)
  → edit prompts.py and/or models.py as map requires
  → offline pytest policy tests
```

### Key data flows

1. **CONTENT → LLM:** best-effort; failures caught by FORMAT/PLAN/math, not by asking the model to self-validate.
2. **FORMAT → host:** `ExerciseBatch` fields are the only trusted response shape.
3. **PLAN → RELY:** echo mismatch raises `ValueError` → same bounded regeneration as other validation failures (already wired in `generate_validated_batch`).
4. **THINKING → cost/quality:** run-scoped; mixed easy+hard lots share one effort (accepted; no per-item API effort).

### State management

No new process state. Token buffer, scoped env, postmortem ownership unchanged from v2.0/v2.1.

## Scaling Considerations

Not multi-tenant. v2.2 is documentation + prompt hygiene; it does not change batch caps or concurrency.

| Pressure | What breaks | v2.2 stance |
|----------|-------------|-------------|
| Prompt/rule drift | Agents “fix” format in prose again | Policy tests + skill “schema first” |
| Longer persona docs in system prompt | Token cost, weaker adherence | Keep runtime prompt short; put detail in rules |
| Temptation to “AI self-check” | Duplicate/fragile validation | Explicit anti-pattern in rules |
| Large mixed lots | Same as v2.1 (context/cost) | Out of scope — CAP-02 deferred |

### Scaling Priorities

1. **First bottleneck:** human/agent process drift (prompt-as-schema) → skill + tests.
2. **Second bottleneck:** none new at runtime; reuse v2.1 batch-size limits.

## Anti-Patterns

### Anti-Pattern 1: Second validation agent / tool loop

**What people do:** add an agent step “validate exercises” before/after `generate_batch`, or prompt the model to “confira se o JSON está correto.”

**Why it's wrong:** duplicates `validator` / `verify_plan_echo` / `math_check`; violates “LLM is not source of truth”; fights RELY ownership.

**Do this instead:** keep one pipeline; improve code checks or prompts (CONTENT only).

### Anti-Pattern 2: JSON schema dump in the system prompt

**What people do:** paste full field lists / example JSON into `SYSTEM_PROMPT` “to be safe.”

**Why it's wrong:** false security; drifts from Pydantic; Phase 14 already banned field-contract bullets in the user prompt (SEED-008).

**Do this instead:** `response_format=ExerciseBatch`; prompt stays CONTENT; tests forbid schema dumps.

### Anti-Pattern 3: RELY or math_check redesign “for the contract”

**What people do:** new retry policies, split loops, or generic math overhaul to “support” persona work.

**Why it's wrong:** out of milestone scope (SEED-009 waits on BNCC); high regression risk.

**Do this instead:** document existing order: validate → math → `verify_plan_echo` → RELY.

### Anti-Pattern 4: Putting `reasoning_effort` on Exercise / ExerciseSpec

**What people do:** treat THINKING as a response or plan field.

**Why it's wrong:** one completion = one API effort; confuses pedagogy with provider knobs.

**Do this instead:** keep `reasoning.py` run-level; defer pedagogical tipo (TIPO-OPEN).

### Anti-Pattern 5: Widening the embed return for “contract metadata”

**What people do:** return `(batch, contract_version, usage)` from `generate_batch`.

**Why it's wrong:** breaks EMBED-01; OBS-01 parked.

**Do this instead:** keep `→ ExerciseBatch`; contract version lives in docs/skill if needed.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| OpenAI / Gemini / Grok | Existing Structured Outputs / JSON schema | No provider changes for v2.2 |
| Cursor / GSD agents | Skill + rules discovery | Runtime generation does not load skills |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Skill/rules ↔ `prompts.py` | Human/agent edit discipline | Runtime does not import skills |
| `prompts` ↔ generators | `(system, user)` tuple | CONTENT only |
| Generators ↔ models | `response_format=ExerciseBatch` | FORMAT |
| RELY ↔ validator / `verify_plan_echo` | same `request` | PLAN + structure; unchanged |
| `reasoning.py` ↔ models | none | THINKING isolated |

### New vs modified (explicit)

| Kind | Component | Role |
|------|-----------|------|
| **New** | `skills/exercise-generation/SKILL.md` | Agent index for domain contract |
| **New** | `.cursor/rules/30-exercise-generation.mdc` (name TBD) | Authority map + persona + anti-patterns |
| **Modified** | `prompts.py` | Align persona; strip format-field prose |
| **Modified** | `tests/test_prompts.py` (+ optional helpers) | Policy + marker coverage for system+user |
| **Optional** | Short host doc (`docs/` or README Embed blurb) | “What hosts may assume” (SEED-008 A) |
| **Unchanged** | `service`, failover, RELY, generators’ call shape, `math_check`, adapters | Preserve embed + ops |
| **Avoid** | Second agent, RELY redesign, math_check overhaul, new generate API | YAGNI / milestone lock |

### Suggested build order (phases from 16)

Dependency order: **agent contract → prompt CONTENT → policy tests/hooks**.

```
16. Skill + domain rules (authority map, pipeline diagram, anti-patterns)
        │
        └─► 17. Prompt content alignment (SYSTEM/USER ↔ contract; strip field prose)
                  │
                  └─► 18. Offline policy tests + thin assert helpers
                            (+ optional host-facing response-contract blurb)
```

| # | Phase | Delivers | Depends on | Why this order |
|---|-------|----------|------------|----------------|
| **16** | Domain skill & rules | `skills/exercise-generation/SKILL.md`; `.cursor/rules/30-…mdc`; FORMAT/PLAN/CONTENT/THINKING table; “no second agent”; pointer to real pipeline | — | Agents need the contract before rewriting prompts; docs-first reduces thrash |
| **17** | Prompt CONTENT layer | Rewrite `SYSTEM_PROMPT` / tighten user cues to match skill; remove remaining field-contract prose; keep slot list + topic rules | 16 | Runtime behavior follows written authority; still no RELY/math changes |
| **18** | Policy tests & light hooks | Extend offline asserts (system+user); optional shared helpers; optional Embed/README “schema is format authority” note | 17 | Lock the policy in CI; helpers stay test-side unless discuss proves a tiny shared util |

**Preserve embed contract checklist:** same `generate_batch` signature and return; uniform/mixed requests unchanged; error kinds unchanged; no `sys.exit` below `main.run`; no live LLM in pytest.

## Constraint Check

1. **YAGNI:** no agent framework, no RAG, no FastAPI, no RELY/math redesign, no multi-persona taxonomy unless discuss promotes it.
2. **LLM is not source of truth:** FORMAT + PLAN + math stay in code; prompts are CONTENT best-effort.
3. **Testability:** contract policy verified offline (string/marker tests), same as Phase 14 prompt tests.
4. **Discuss still open:** exact rule filename; single vs named personas; whether a short `docs/RESPONSE-CONTRACT.md` is needed vs skill-only; how aggressive SYSTEM_PROMPT shortening should be.

## Confidence Summary

| Finding | Confidence | Basis |
|---------|-----------|-------|
| Keep seam + RELY + math_check ownership | HIGH | PROJECT.md Key Decisions; `generate_validated_batch` already validate → echo |
| Skill + rules is the right SEED-007 integration | HIGH | Mirrors `skills/python-ai-engineering`; seeds A–D |
| Strip format prose from prompts (esp. SYSTEM) | HIGH | SEED-008; user prompt already clean; SYSTEM still lists enunciado/resposta/explicação |
| Authority map FORMAT/PLAN/CONTENT/THINKING | HIGH | Operator brief + SEED-007/008 suggested policy |
| Thin test helpers only — no second validator | HIGH | Milestone A3/B2 scope; AI engineering rule “deterministic verification” |
| Phases 16 → 17 → 18 | HIGH | Docs/contract before prompt before tests |
| Optional host-facing response doc | MEDIUM | SEED-008 A; may fold into skill/README |
| Single professor persona for v2.2 | MEDIUM | Seed note; discuss may lock variants later |

## Sources

- `.planning/PROJECT.md` — v2.2 goal, pipeline diagram, promoted SEED-007/008
- `.planning/seeds/SEED-007-exercise-ai-persona-rules.md` — skill/rules/slices A–E
- `.planning/seeds/SEED-008-response-structure-over-prompt.md` — schema-as-authority policy
- `exercise-ai/prompts.py`, `models.py` (`verify_plan_echo`), `validator.py`, `reliability.py`, `reasoning.py`
- `skills/python-ai-engineering/SKILL.md` + `.cursor/rules/10-python.mdc` / `20-ai-engineering.mdc` — pattern to mirror
- Prior `.planning/research/ARCHITECTURE.md` (v2.1 lotes) — seam invariants reused
- Phase 14 verification — user prompt already omits field-contract bullets (partial SEED-008)

---
*Architecture research for: v2.2 AI generation contract (skill/rules + prompt CONTENT) on existing GenerationRequest → ExerciseBatch pipeline*
*Researched: 2026-09-23*
