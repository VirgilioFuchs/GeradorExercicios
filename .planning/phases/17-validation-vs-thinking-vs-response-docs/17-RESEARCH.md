# Phase 17: Validation vs thinking vs response docs - Research

**Researched:** 2026-09-25
**Domain:** Domain generation contract docs — triad validation ≠ thinking ≠ response (CONTRACT-02)
**Confidence:** HIGH (in-repo ownership + locked CONTEXT); MEDIUM (OpenAI API docs via Context7); LOW (industry blog patterns — corroborative only)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Onde mora a tríade
- **D-01:** Ship both `rules.py` and `TRIAD.md` under `exercise-ai/skills/generation/`. — **Reversibility:** costly — path becomes the documented home for CONTRACT-02.
- **D-02:** `TRIAD.md` is **authoritative**; `rules.py` summarizes and points to it (if they diverge, fix to match TRIAD.md). — **Reversibility:** costly — establishes doc-over-code for this contract text.
- **D-03:** `rules.py` exposes `TRIAD_DOC = Path(__file__).with_name("TRIAD.md")` plus a docstring that directs readers to that file.
- **D-04:** Filename is `TRIAD.md` (English technical name).

#### Profundidade do texto
- **D-05:** `TRIAD.md` = short section per leg (validation / thinking / response) **plus code-path pointers** (e.g. `validator.py`, `math_check.py`, plan-echo / RELY, `reasoning.py`, `models.Exercise`) — not a long FAQ/examples guide.
- **D-06:** Body language **PT-BR**; technical identifiers remain English (`reasoning_effort`, `Exercise`, module paths).
- **D-07:** Explicit **callout**: `reasoning_effort` is a run-level API knob — **not** pedagogical `tipo_raciocinio` (out of v2.2 product scope).
- **D-08:** Include **one-line pipeline** `prompt → LLM → validate → math_check → verify_plan_echo → RELY` and point at `AGENTS.md` / project constraints.

#### Público-alvo
- **D-09:** Audience is **runtime / API package** readers (lab/host developers consuming `skills.generation`) — **not** a GSD/Cursor agent skill. — Carries Phase 16 D-01/D-02.
- **D-10:** Do **not** re-export `TRIAD_DOC` from `skills.generation.__init__` — keep `__all__` as `get_persona_system` only.
- **D-11:** Do **not** modify `persona.py` in Phase 17.
- **D-12:** No new offline pytest for TRIAD this phase — policy/offline tests remain Phases 24–25.

#### Nunca faça / fora de escopo
- **D-13:** Phase 17 delivers **triad docs only**; detailed never-do list content waits for Phase 18 (with authority map / CONTRACT-03).
- **D-14:** Keep existing `# TODO` never-do bullets in `rules.py`, retargeted: never-do → Phase 18; triad → `TRIAD.md` / `TRIAD_DOC`.
- **D-15:** `TRIAD.md` includes a short **“Fora desta fase”** block (2–3 lines) pointing never-do detail + authority map to Phase 18.

### Claude's Discretion
- Exact PT-BR wording of triad sections and callout (must match D-05–D-08 substance).
- Exact set of code paths listed as pointers (must cover validation vs thinking vs response legs).
- Exact TODO comment rewording in `rules.py` while preserving foreshadow bullets.

### Deferred Ideas (OUT OF SCOPE)
- **DEF-01:** Future rules-file architecture (load specific rules from `.md`/`.yaml`/`.json` via pointers) — not Phase 17.
- Detailed **nunca faça** catalog — Phase 18 (CONTRACT-03 / authority map companions).
- Authority map format → schema · plan → echo · content → prompts — Phase 18.
- Prompt persona wiring — Phase 19+.
- Offline policy tests asserting triad/never-do — Phases 24–25.
- Re-exporting `TRIAD_DOC` or expanding `__all__` — revisit only if a host needs it.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CONTRACT-02 | Docs/rules separate **validation** (deterministic code) vs **thinking** (API `reasoning_effort`) vs **response** (`Exercise` fields) | Authoritative `TRIAD.md` + thin `rules.py` pointer; recommended outline, code citations, pitfalls, and Nyquist manual-check map below |
</phase_requirements>

## Summary

Phase 17 is a **documentation-only** slice of CONTRACT-02 on the API skill package started in Phase 16. Deliver `exercise-ai/skills/generation/TRIAD.md` as the source of truth for the three-way split, and thin `rules.py` so readers find `TRIAD_DOC` without expanding the public `__all__`. No prompt wiring, no persona edits, no new pytest, no external rule loaders.

Industry and vendor docs reinforce the same split the lab already encoded in code: provider Structured Outputs enforce **shape**; **semantic** correctness stays in application validators; **reasoning effort** is a request-level API control, not a response field. Project PITFALLS warn that agents misread the triad as three *prompt* sections or invent LLM self-check — TRIAD.md must state the opposite in plain PT-BR with module pointers.

**Primary recommendation:** Ship a short PT-BR `TRIAD.md` (pipeline one-liner + three legs + pedagogy callout + “Fora desta fase”) and retarget `rules.py` to `TRIAD_DOC` + Phase-18 TODOs — zero new dependencies.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Triad contract text (CONTRACT-02) | API / Backend (docs in package) | — | Lives next to runtime skill modules; audience is hosts/lab consumers of `skills.generation` (D-09), not browser/CDN |
| Validation ownership statement | API / Backend | — | Points at existing deterministic modules after LLM return |
| Thinking / `reasoning_effort` statement | API / Backend | — | Documents run-level knob in `reasoning.py`; not an Exercise field |
| Response field ownership statement | API / Backend | — | Points at `models.Exercise` + Structured Outputs |
| Never-do / authority map | Deferred (Phase 18) | — | D-13/D-15 — only a 2–3 line forward pointer this phase |
| Offline policy tests for triad text | Deferred (Phases 24–25) | — | D-12 forbids new pytest here |

## Project Constraints (from .cursor/rules/)

Actionable directives relevant to this phase:

| Rule | Directive | Phase 17 implication |
|------|-----------|----------------------|
| `10-python.mdc` | Smallest correct change; YAGNI; search before new abstractions; prefer `pathlib` | `TRIAD_DOC = Path(__file__).with_name("TRIAD.md")` — no new abstractions |
| `10-python.mdc` | Verify with targeted tests before claiming done | Run existing `pytest exercise-ai/tests/test_skills_generation.py` only — no new suite (D-12) |
| `20-ai-engineering.mdc` | Do not introduce an agent when deterministic code is sufficient | TRIAD must forbid inventing a validation agent / prompt self-check |
| `20-ai-engineering.mdc` | LLM output is not evidence of correctness; use deterministic checks | Aligns with validation leg = code only |
| `20-ai-engineering.mdc` | Prefer structured outputs + schema validation | Response leg = `Exercise` / Structured Outputs, not prompt-as-schema |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| *(none new)* | — | Phase is docs + Path constant | CONTRACT-02 is contract text; stack already ships openai/pydantic/pytest |
| Python stdlib `pathlib.Path` | 3.11+ | `TRIAD_DOC` constant | Matches D-03 and `10-python.mdc` pathlib preference `[VERIFIED: exercise-ai/skills/generation/rules.py` current stub has no Path yet — add in plan`]` |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 9.0.3 (env) | Regression smoke only | Existing `test_skills_generation.py` — do **not** add TRIAD asserts `[VERIFIED: shell pytest.__version__]` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `TRIAD.md` next to `rules.py` | `.cursor/rules/30-….mdc` | Rejected — Phase 16 D-01/D-02 + Phase 17 D-09: API package, not agent skill |
| Docstring-only in `rules.py` | No markdown file | Rejected — D-02 doc-over-code; D-01/D-04 require `TRIAD.md` |
| Re-export `TRIAD_DOC` from `__init__` | Narrow `__all__` | Rejected — D-10 |
| External `.md`/`.yaml` loaders | Static `TRIAD.md` | Deferred DEF-01 |

**Installation:** none.

**Version verification:** No new packages. Existing pytest probed: `9.0.3`.

## Package Legitimacy Audit

> No external packages installed this phase.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| — | — | — | — | — | N/A | No installs |

**Packages removed due to [SLOP] verdict:** none  
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
Host / lab developer (reads package docs)
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│  exercise-ai/skills/generation/                           │
│    TRIAD.md  ◄── authoritative CONTRACT-02 text (D-02)    │
│    rules.py  ── TRIAD_DOC Path + short summary (D-03)     │
│    persona.py ── UNCHANGED (D-11)                         │
│    __init__.py ── __all__ = get_persona_system only (D-10)│
└───────────────────────────────────────────────────────────┘
        │ documents (does not execute)
        ▼
┌───────────────────────────────────────────────────────────┐
│  RUNTIME PIPELINE (unchanged ownership)                   │
│                                                           │
│  prompt → LLM (Structured Outputs) → validate             │
│       → math_check → verify_plan_echo → RELY              │
│                                                           │
│  thinking: resolve_reasoning_effort() ── run-level API    │
│  response: Exercise fields only                           │
└───────────────────────────────────────────────────────────┘
```

### Recommended Project Structure

```
exercise-ai/skills/generation/
├── __init__.py      # UNCHANGED — get_persona_system only
├── persona.py       # UNCHANGED
├── rules.py         # MODIFIED — TRIAD_DOC + docstring + retargeted TODO
└── TRIAD.md         # NEW — authoritative triad (PT-BR)
```

### Pattern 1: Doc-as-source-of-truth + thin code pointer

**What:** Markdown owns prose; Python exposes `Path` for discovery.  
**When to use:** CONTRACT-02 (locked D-02/D-03).  
**Example (planner/executor target):**

```python
# exercise-ai/skills/generation/rules.py
"""Ponte para a tríade de geração.

Texto autoritativo: TRIAD.md (mesmo diretório).
Se rules.py e TRIAD.md divergirem, corrija para bater com TRIAD.md.
"""
from __future__ import annotations

from pathlib import Path

TRIAD_DOC = Path(__file__).with_name("TRIAD.md")

# TODO (Phase 18 — never-do / authority map):
# - nunca pedir auto-checagem da LLM como substituto de validação determinística
# - nunca tratar schema-in-prompt como contrato de formato (schema/Pydantic é autoridade)
# - nunca misturar regras pedagógicas com prompts.py até a fase de wiring (PROMPT-02+)
# Tríade (validation / thinking / response): ver TRIAD.md / TRIAD_DOC
```

### Pattern 2: Three short legs + code pointers (not FAQ)

**What:** One H2 per concern; 3–8 lines each; relative module paths as pointers.  
**When to use:** D-05 locked.  
**Recommended `TRIAD.md` outline (discretionary PT-BR wording):**

1. **Título** — Tríade de geração (validation / thinking / response)
2. **Pipeline** — one line `prompt → LLM → validate → math_check → verify_plan_echo → RELY` + pointer to `AGENTS.md` (LLM não é fonte de verdade)
3. **Validação** — código determinístico após o LLM; pointers below
4. **Pensamento** — `reasoning_effort` via `reasoning.py`; **callout** ≠ `tipo_raciocinio`
5. **Resposta** — apenas campos Structured Outputs / `Exercise`
6. **Fora desta fase** — never-do detalhado + mapa de autoridade → Phase 18 (D-15)

### Pattern 3: Industry split mirrors lab (corroboration)

**What:** External sources separate (a) schema/shape enforcement, (b) post-parse semantic validation in code, (c) reasoning as API/internal — not as prompt self-check.  
**When to use:** Justify TRIAD wording; do not import vendor product names into TRIAD.md.  
**Sources:** OpenAI Structured Outputs + reasoning guides `[CITED: developers.openai.com/api/docs/guides/structured-outputs]` `[CITED: developers.openai.com/api/docs/guides/reasoning]`; MLflow “Enforce, Validate, Observe” `[CITED: mlflow.org/articles/structured-outputs-llm/]`; DeepInspect structure vs policy `[CITED: deepinspect.ai/blog/llm-response-schema-validation]` — web tier confidence LOW for blogs.

### Anti-Patterns to Avoid

- **Triad as three prompt sections:** PITFALLS Pitfall 2 — write “validação = código”, not “seção de validação no SYSTEM”.
- **Equating thinking with pedagogy:** PITFALLS Pitfall 3 — mandatory D-07 callout.
- **Expanding `__all__` or editing `persona.py`:** D-10/D-11.
- **Stubbing YAML/JSON loaders “for later”:** DEF-01 out of scope.
- **New pytest asserting TRIAD text:** D-12 — Phases 24–25.
- **Authority map / full never-do catalog in TRIAD.md:** D-13/D-15 — only forward pointer.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Discoverability of triad | Custom registry / dataclass `GenerationSkill` | `TRIAD_DOC` Path + markdown | YAGNI; Phase 16 deferred dataclass |
| Keep docs in sync with code | Runtime loader of `.md` into validators | Static pointers to modules | Loaders deferred DEF-01; docs guide humans |
| Prove CONTRACT-02 in CI this phase | New offline policy suite | Manual checklist + existing smoke import test | D-12 |
| Explain OpenAI APIs in TRIAD | Long vendor FAQ | One sentence + `reasoning.py` / `models.py` pointers | D-05 short sections |

**Key insight:** Hand-rolling a second validation path or prompt self-check is the failure mode this phase exists to prevent — document ownership, do not reimplement it.

## Common Pitfalls

### Pitfall 1: Prompt-side “validation” invented from the triad
**What goes wrong:** Readers treat TRIAD as three SYSTEM blocks including “valide o JSON”.  
**Why it happens:** SEED-007 wording + generic agent skills. `[VERIFIED: .planning/research/PITFALLS.md Pitfall 2]`  
**How to avoid:** First sentence of Validação: “Validação = código determinístico apenas (`validator`, `math_check`, `verify_plan_echo`, RELY).”  
**Warning signs:** Phrases like “peça ao modelo para validar” in TRIAD.md draft.

### Pitfall 2: `reasoning_effort` ≈ `tipo_raciocinio`
**What goes wrong:** Docs/UI map pedagogy to API cost knobs.  
**Why it happens:** “Pensamento” sounds pedagogical. `[VERIFIED: .planning/research/PITFALLS.md Pitfall 3]`  
**How to avoid:** Explicit callout (D-07); name both identifiers.  
**Warning signs:** TRIAD lists effort values as exercise types.

### Pitfall 3: Schema dump / field contract in triad “Response” section
**What goes wrong:** Response leg pastes full JSON Schema or instructs prompts to list keys as API contract.  
**Why it happens:** Habit from free-form JSON eras. `[VERIFIED: .planning/research/PITFALLS.md Pitfall 1]`  
**How to avoid:** Point to `models.Exercise` fields by name + “Structured Outputs”; do not dump JSON Schema or tell prompts to redefine format (authority map is Phase 18).  
**Warning signs:** Fenced JSON of `ExerciseBatch` inside TRIAD.md.

### Pitfall 4: Drift between `rules.py` prose and `TRIAD.md`
**What goes wrong:** Two summaries diverge.  
**Why it happens:** Dual files (D-01).  
**How to avoid:** D-02 rule in both docstring and TRIAD header: TRIAD wins. Keep `rules.py` body empty/`pass` or minimal.  
**Warning signs:** Long Portuguese paragraphs in `rules.py`.

### Pitfall 5: Accidental scope creep into Phase 18/19
**What goes wrong:** Never-do catalog, authority map, or `prompts.py` wiring lands in the same PR.  
**Why it happens:** SEED-007 bundled slices.  
**How to avoid:** Honor D-11–D-15 and deferred list; “Fora desta fase” only.  
**Warning signs:** Diff touches `prompts.py` / `persona.py` / `__init__.py` exports.

## Code Examples

### Canonical response fields (cite in TRIAD Response leg)

```191:199:exercise-ai/models.py
class Exercise(BaseModel):
    """Estrutura de um exercício individual."""

    enunciado: str = Field(..., description="Texto do enunciado do exercício")
    resposta: str = Field(..., description="Resposta correta ou solução direta")
    explicacao: str = Field(..., description="Explicação passo a passo da resolução")
    dificuldade: DificuldadeEnum = Field(
        ..., description="Faixa de dificuldade ecoada (D-09)"
    )
```

`[VERIFIED: exercise-ai/models.py:191-199]` Quote: `enunciado`, `resposta`, `explicacao`, `dificuldade` on `Exercise`.

### Thinking levels / resolver (cite in TRIAD Thinking leg)

```17:43:exercise-ai/reasoning.py
ReasoningLevel = Literal["none", "low", "medium", "high", "xhigh", "max"]

# Shared by Gemini / Grok / non-extended surfaces.
REASONING_LEVELS: tuple[ReasoningLevel, ...] = ("none", "low", "medium", "high")
# ...
def resolve_reasoning_effort(explicit: str | None = None) -> ReasoningLevel:
```

`[VERIFIED: exercise-ai/reasoning.py:17-43]` Quote: `ReasoningLevel = Literal["none", "low", "medium", "high", "xhigh", "max"]`; `resolve_reasoning_effort`.

### Validation + plan-echo order inside RELY (cite in TRIAD Validation + pipeline)

```116:119:exercise-ai/reliability.py
            print("Validando…", file=sys.stderr)
            try:
                validated = validate_exercise_batch(batch, request)
                verify_plan_echo(validated, request)
```

`[VERIFIED: exercise-ai/reliability.py:116-119]` Quote: `validate_exercise_batch` then `verify_plan_echo`.

Note: `validate_exercise_batch` calls `check_math_batch(batch)` before return `[VERIFIED: exercise-ai/validator.py:79]` Quote: `check_math_batch(batch)`. Pipeline one-liner still lists `math_check` as its own stage (D-08 / AGENTS.md) — accurate for readers even though the call is nested inside the validator today.

### Public export must stay narrow

```7:9:exercise-ai/skills/generation/__init__.py
__all__ = [
    "get_persona_system",
]
```

`[VERIFIED: exercise-ai/skills/generation/__init__.py:7-9]` Quote: `__all__ = ["get_persona_system"]`.

### Current `rules.py` stub to retarget

```1:13:exercise-ai/skills/generation/rules.py
"""Regras de geração (esqueleto).

Conteúdo real nas Phases 17–18 (tríade, autoridade, nunca-faça).
"""

from __future__ import annotations

# TODO (Phases 17–18):
# - nunca pedir auto-checagem da LLM como substituto de validação determinística
# - nunca tratar schema-in-prompt como contrato de formato (schema/Pydantic é autoridade)
# - nunca misturar regras pedagógicas com prompts.py até a fase de wiring (PROMPT-02+)

pass
```

`[VERIFIED: exercise-ai/skills/generation/rules.py:1-13]`

### Recommended TRIAD code-path pointer set (discretion — must cover three legs)

| Leg | Modules / symbols to cite |
|-----|---------------------------|
| Validação | `validator.validate_exercise_batch`, `math_check.check_math_batch`, `models.verify_plan_echo`, `reliability` RELY loop |
| Pensamento | `reasoning.resolve_reasoning_effort`, env `LLM_REASONING_EFFORT`, CLI `--reasoning` (as documented in `reasoning.py` module docstring) |
| Resposta | `models.Exercise` / `ExerciseBatch`, generators’ Structured Outputs `response_format` (name only — do not edit generators) |
| Constraints | `AGENTS.md` — LLM não é fonte de verdade; retries limitados |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Format rules in SYSTEM_PROMPT | Schema + Structured Outputs + code validators | v1→v2.2 policy | TRIAD must not reintroduce prompt-as-schema |
| Thinking conflated with pedagogy | `reasoning_effort` run-level only; TIPO-OPEN deferred | v2.1/v2.2 PITFALLS | D-07 callout mandatory |
| Cursor skill as CONTRACT home | `exercise-ai/skills/generation/` API package | Phase 16 discuss | TRIAD under generation/, not `.cursor` |
| Enforce / Validate / Observe (industry) | Same split: provider enforce shape → app validate → observe | Industry 2025–2026 | Corroborates lab; do not add MLflow |

**Deprecated/outdated:**
- Agent-facing `.cursor/rules/30-exercise-generation.mdc` as Phase 17 vehicle — superseded by Phase 16 D-01/D-02.
- Treating RESEARCH ARCHITECTURE suggested order “16 skill → 17 prompts” literally — roadmap renumbered; Phase 17 is triad docs, prompts are 19+.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Listing `dificuldade` on `Exercise` in the Response leg is helpful and does not violate “response = Structured Outputs fields only” | Code Examples / TRIAD outline | If discuss wanted only enunciado/resposta/explicacao, trim `dificuldade` from Response section — still a real Exercise field |
| A2 | Nested `check_math_batch` inside validator is fine to still spell as a separate pipeline stage in the one-liner | Architecture / Pipeline | Wording nit only; ownership unchanged |
| A3 | Industry blogs (MLflow, DeepInspect) are supportive color, not normative for TRIAD wording | State of the Art | Ignore if planner wants zero external narrative |

**If this table is empty:** N/A — three low-risk assumptions above.

## Open Questions (RESOLVED)

1. **How much to mention `dificuldade` / plan-echo in Response vs Validation?**
   - **RESOLVED:** One short clause under Validação (“adesão ao plano: `verify_plan_echo`”); list `dificuldade` among Response fields without expanding authority map (Phase 18). Matches plan Task 1.

2. **Should `rules.py` keep `pass` after adding `TRIAD_DOC`?**
   - **RESOLVED:** Keep `pass` (or equivalent no-op body) after `TRIAD_DOC` + TODO — module stays importable; YAGNI. Matches plan Task 2.

## Environment Availability

Step 2.6: SKIPPED for external services (docs-only). Local probes for executor convenience:

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python + pytest | Smoke regression | ✓ | pytest 9.0.3 | — |
| New PyPI packages | — | N/A | — | None required |
| Live LLM | — | N/A | — | Not used this phase |

**Missing dependencies with no fallback:** none  
**Missing dependencies with fallback:** none

## Validation Architecture

> `workflow.nyquist_validation` is `true` in `.planning/config.json`. Phase is docs-only with **D-12: no new pytest** — Nyquist sampling is regression + manual CONTRACT-02 checklist.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 (existing) |
| Config file | none project-wide — discovery via `pytest exercise-ai` |
| Quick run command | `pytest exercise-ai/tests/test_skills_generation.py -q` |
| Full suite command | `pytest exercise-ai -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CONTRACT-02 | `TRIAD.md` exists beside `rules.py` and states validation=code, thinking=`reasoning_effort`, response=`Exercise` fields | manual checklist | Read `exercise-ai/skills/generation/TRIAD.md` | ❌ Wave 0 create file |
| CONTRACT-02 | `rules.py` exposes `TRIAD_DOC` Path + docstring pointing to TRIAD | manual / import smoke | `python -c "from skills.generation.rules import TRIAD_DOC; assert TRIAD_DOC.name=='TRIAD.md'"` (from `exercise-ai` cwd) | ❌ after edit |
| CONTRACT-02 | `__all__` unchanged; persona untouched | regression | `pytest exercise-ai/tests/test_skills_generation.py -q` | ✅ |
| CONTRACT-02 | No new offline policy asserts | N/A (deferred 24–25) | — | N/A by design |

### Sampling Rate

- **Per task commit:** `pytest exercise-ai/tests/test_skills_generation.py -q`
- **Per wave merge:** `pytest exercise-ai -q`
- **Phase gate:** Full suite green + manual triad checklist before `/gsd-verify-work`

### Manual CONTRACT-02 checklist (planner → VALIDATION.md)

- [ ] `TRIAD.md` present at `exercise-ai/skills/generation/TRIAD.md`
- [ ] Sections cover Validação / Pensamento / Resposta (PT-BR)
- [ ] Pipeline one-liner present; points to `AGENTS.md`
- [ ] Callout: `reasoning_effort` ≠ `tipo_raciocinio`
- [ ] Code pointers cover validator, math_check, verify_plan_echo/RELY, reasoning, Exercise
- [ ] “Fora desta fase” → Phase 18 never-do + authority map
- [ ] `TRIAD_DOC` in `rules.py`; TODO retargeted; no `__init__` / `persona.py` / `prompts.py` edits

### Wave 0 Gaps

- [ ] Create `TRIAD.md` (implementation artifact — not a test file)
- [ ] None for automated test scaffolding — **by D-12 design**; do not add `test_triad.py` this phase

*(No Wave 0 pytest gaps. Manual verification substitutes for Nyquist automation on CONTRACT-02 text.)*

## Security Domain

> Docs-only phase; `security_enforcement` not disabled.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | tangential | TRIAD must not recommend trusting LLM self-check; keep pointing at code validators |
| V6 Cryptography | no | — |

### Known Threat Patterns for this docs slice

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Prompt injection theater via “validate yourself” instructions | Spoofing / Tampering | Document validation = code only (Pitfall 2) |
| Secret logging advice in never-do foreshadow | Information Disclosure | Keep existing TODO bullet; expand in Phase 18 without logging keys |
| Dual-source drift enabling agents to invent validators | Elevation of Privilege (process) | TRIAD.md authoritative (D-02) |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/17-validation-vs-thinking-vs-response-docs/17-CONTEXT.md` — D-01..D-15
- `.planning/REQUIREMENTS.md` — CONTRACT-02
- `.planning/ROADMAP.md` — Phase 17 success criteria
- `.planning/research/PITFALLS.md` — thinking≠pedagogy; no LLM self-check
- `.planning/research/ARCHITECTURE.md` — pipeline layers (API path per Phase 16)
- `exercise-ai/skills/generation/rules.py`, `__init__.py`, `persona.py`
- `exercise-ai/models.py`, `validator.py`, `math_check.py`, `reliability.py`, `reasoning.py`
- `AGENTS.md` — LLM not source of truth; validator testable offline
- `.cursor/rules/10-python.mdc`, `20-ai-engineering.mdc`

### Secondary (MEDIUM confidence)

- Context7 `/websites/developers_openai_api` — Structured Outputs with `response_format` / `reasoning_effort` coexistence; reasoning effort guide
- OpenAI Structured Outputs guide — schema adherence; simpler prompting `[CITED: https://developers.openai.com/api/docs/guides/structured-outputs]`
- OpenAI Reasoning guide — `reasoning.effort` run-level `[CITED: https://developers.openai.com/api/docs/guides/reasoning]`

### Tertiary (LOW confidence)

- MLflow Enforce / Validate / Observe `[CITED: https://mlflow.org/articles/structured-outputs-llm/]`
- DeepInspect schema vs policy validation `[CITED: https://www.deepinspect.ai/blog/llm-response-schema-validation]`
- OrderBench / semantic reliability of schema-only `[CITED: https://arxiv.org/html/2607.18261v1]`

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new deps; pathlib already project convention
- Architecture: HIGH — locked CONTEXT + verified module ownership
- Pitfalls: HIGH — project PITFALLS + AGENTS.md; vendor docs corroborate

**Research date:** 2026-09-25  
**Valid until:** 2026-10-25 (stable docs phase; revisit if Phase 18 moves triad home)

## RESEARCH COMPLETE
