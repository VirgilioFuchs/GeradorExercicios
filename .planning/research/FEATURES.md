# Feature Research

**Domain:** Exercise batch authoring / LLM math-exercise generators (mixed-difficulty lots)
**Researched:** 2026-09-21
**Confidence:** HIGH on table stakes (SEED-006 + shipped uniform `GenerationRequest` + industry quiz/worksheet generators); MEDIUM on differentiators (pedagogical “tipo de raciocínio” taxonomies vary by product); HIGH on anti-features that collide with current multi-provider `reasoning_effort` (run-level only today)

**Milestone:** v2.1 “Lotes dinâmicos” — SUBSEQUENT milestone. Uniform generation through v2.0 is EXISTING and must keep working. Scope is SEED-006 only: per-exercise difficulty, per-exercise pedagogical reasoning type, larger quantity, batch-plan UX. Out of scope: images, storytelling, BNCC, packaging, OBS/LOG, validation overhaul beyond mixed-batch needs.

---

## Feature Landscape

### Table Stakes (Operators Expect These)

Features an operator assembling a prova / sequência pedagógica assumes exist. Missing these = still “N cópias do mesmo nível.”

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Batch plan / difficulty distribution** (e.g. `2 fácil + 3 médio + 1 difícil`) | Quiz/worksheet tools expose “Mixed” or an explicit easy/medium/hard mix; teachers think in counts per band, not N identical flags | MEDIUM | Compact UX over raw item list. Wizard + argparse must accept a plan without N manual flags (SEED-006 slice E). Plan expands to ordered item specs before prompt |
| **Per-exercise difficulty in the request** | Domínio por atividade — core SEED-006 ask; uniform-only feels incomplete once mixed is promised | MEDIUM | Extend beyond single `GenerationRequest.dificuldade`. Prefer: optional `itens: list[ItemSpec]` **or** `plano: {facil, medio, dificil}` that expands; keep scalar `dificuldade` + `quantidade` for backward compat |
| **Prompt that instructs mixed levels item-by-item** | LLM otherwise averages difficulty or ignores the plan | MEDIUM | `prompts.build_prompts` must enumerate slot N → dificuldade (and tipo if present). Structured Outputs schema should echo metadata so validation can check adherence |
| **Validator: count + per-item plan adherence** | LLM is not source of truth; mixed batches without checks regress to “hope the model obeyed” | MEDIUM | Today `validate_exercise_batch` checks `len == request.quantidade`. Extend: expected N from plan; each exercise’s declared `dificuldade` matches slot; fail → RELY as today (bounded 1–2) |
| **Echo difficulty (and tipo) on each `Exercise` in JSON** | Host/CLI/demo need to show which item is easy vs hard; plan is useless if only in the request | LOW–MEDIUM | Add optional/required fields on `Exercise` (or parallel `meta`); keeps `enunciado`/`resposta`/`explicacao` intact |
| **Backward-compatible uniform mode** | Scripts, tests, embed hosts, wizard defaults all use scalar dificuldade + quantidade (1–40) | LOW | Uniform request remains valid; mixed is additive. Do not break `service.generate_batch` callers |
| **Raised but still finite quantity cap** | SEED-006: “mais quantidade”; industry caps ~20–50 per run; unbounded = cost/context bombs | MEDIUM | Revisit `MAX_QUANTIDADE = 40`. Raise with a hard ceiling (e.g. 60–80) **or** keep 40 single-shot + optional chunking later. Cap stays in domain model (`ge`/`le`), not only CLI |
| **CLI/wizard path to specify the plan without N flags** | Operator asked for dynamic lots; forcing `--item` × N defeats the UX | MEDIUM | Examples: wizard steps “quantos fáceis / médios / difíceis”; CLI `--plano 2,3,1` or `--facil 2 --medio 3`. Argparse stays scriptable; `gerar` stays interactive |

### Differentiators (Competitive Advantage)

Not required for “mixed lots work,” but align with lab Core Value (reliable structured batches) and SEED-006’s “tipo de raciocínio.”

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Pedagogical “tipo de raciocínio” per exercise** (content constraint in prompt + echoed field) | Differentiates from “Mixed = random mix of hard numbers”; supports sequences (cálculo → interpretação → prova) | MEDIUM | Small closed enum (e.g. cálculo direto, interpretação, resolução multi-passo, justifique) — **not** full Bloom UI. Clarify in discuss: this is **not** API `reasoning_effort` |
| **Plan → expanded ItemSpec list as single source of truth** | Host embed can pass explicit list; wizard only authors the plan; one schema for prompt + validator | LOW–MEDIUM | Service expands plan once; generators never see two competing shapes |
| **Modest quantity increase with honest cost behavior** | Larger provas without pretending one call is free | MEDIUM | Raise cap carefully; document token/`[USAGE]` growth. Chunking (multiple LLM calls) is a differentiator **only if** single-call quality collapses — prefer one call first |
| **Stable slot order matching the plan** | Operator expects exercise[0..1] easy, then medium, etc., for printing/ordering | LOW | Prompt + schema: `exercicios[i]` corresponds to `itens[i]`. Validator enforces order |
| **Embed-friendly mixed request on `generate_batch`** | v2.0 hosts reuse the same seam for dynamic lots | LOW | Same return `ExerciseBatch`; richer `GenerationRequest`. No new HTTP product surface |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Per-item API `reasoning_effort` / thinking level** | “Hard items should think harder” | OpenAI/Gemini/Grok effort is **run-level** today (`reasoning.py`, env/`--reasoning`); per-item would mean N API calls or unsupported kwargs; cost explodes; failover semantics unclear | Keep API effort **global per run**. Put pedagogical tipo on the **item content** (prompt + schema). Document the split in discuss |
| **Unbounded / “no max” quantidade** | “IA poder trabalhar com mais quantidade” misread as infinite | Context truncation, validation timeouts, RELY cost, host hangs; project already bound 1–40 in domain | Raise finite cap; if need >cap, sequential chunked plans (later) with explicit UX |
| **One LLM call per difficulty band (or per item) by default** | Seems easier to “guarantee” levels | Multiplies latency, failover, RELY, usage; breaks single-batch UX; contradicts sequential embed contract | One structured batch call with itemized prompt; chunk only if quality/context fails |
| **Full Bloom / BNCC / skill graph in v2.1** | “Tipo de raciocínio” sounds like standards alignment | SEED-001 BNCC dormant; taxonomy bikeshed blocks shipping | Small closed enum of pedagogical tipos; BNCC stays out of scope |
| **Adaptive mid-batch difficulty** (“if model fails hard, insert easy”) | Smart assessment narrative | Second control loop; conflicts with deterministic plan + validator; not YAGNI | Fixed plan in → validated plan out |
| **Overhaul math_check / semantic validation for every tipo** | “Hard items need deeper checks” | Explicitly out of scope; delays mixed UX | Keep existing math_check + structural plan adherence; deepen later |
| **Images / storytelling / multi-format MCQ packs** | Common quiz-generator feature parity | SEED-003 B/C parked; dilutes lotes dinâmicos | Stay open-response math JSON as today |
| **Silent reinterpretation of uniform `dificuldade` when plan present** | Convenience | Ambiguous which wins; breaks scripts | Explicit rules: plan/itens XOR scalar dificuldade, or plan overrides with warning — pick one in discuss, document, test |

## Expected Operator Behavior

How dynamic/mixed batches typically work end-to-end (and what v2.1 should feel like):

1. **Author a plan, not N clones** — Operator chooses topic (+ matéria) once, then specifies counts per difficulty (and optionally tipo per slot or per band).
2. **Expand → one request** — Plan becomes an ordered list of item specs; `quantidade` = sum of slots.
3. **Single generation** — Same pipeline: prompt → LLM structured batch → validate (count + per-slot fields) → math_check → RELY → `ExerciseBatch`.
4. **Inspect by band** — Output lists exercises with echoed dificuldade/tipo so CLI/`--out`/host UI can group or print in plan order.
5. **Uniform still available** — Shortcut: one dificuldade + quantidade (current behavior) for demos and regression.

## Feature Dependencies

```
Batch-plan UX (wizard/CLI)
    └──requires──> Plan / ItemSpec request model
                       └──requires──> Expanded ordered item list
                              ├──requires──> Mixed-aware prompt builder
                              └──requires──> Exercise schema echo (dificuldade [, tipo])
                                     └──requires──> Validator plan adherence
                                            └──enhances──> Existing RELY + math_check (unchanged loop)

Raised quantity cap
    └──requires──> Domain MAX_QUANTIDADE + CLI/wizard bounds aligned
    └──conflicts──> Unbounded quantity (anti-feature)

Pedagogical tipo de raciocínio (per item)
    └──requires──> ItemSpec + prompt + echo fields
    └──conflicts──> Per-item API reasoning_effort (anti-feature)

API reasoning_effort (global)
    └──enhances──> Whole-run quality/cost knob (existing)
    └──conflicts──> Treating “tipo de raciocínio” as API effort

service.generate_batch (v2.0)
    └──enhances──> Mixed GenerationRequest without new transport

Uniform GenerationRequest (legacy)
    └──conflicts──> Ambiguous dual specification (plan + scalar) without rules
```

### Dependency Notes

- **Batch-plan UX requires ItemSpec/plan model:** UI is sugar; domain must own the expanded list or validation and embed diverge.
- **Prompt + validator require echoed per-item fields:** Without schema fields, adherence checks are guesswork on free text.
- **RELY/math_check enhance, do not redesign:** Mixed failures still go through the same bounded regenerate loop; do not add a second retry architecture.
- **Raised cap requires domain + CLI alignment:** v2.0 already moved bound into Pydantic (`MAX_QUANTIDADE`); wizard/`argparse` must track the constant.
- **Pedagogical tipo conflicts with per-item API effort:** Different layers (content vs provider knob); conflating them is the main SEED-006 discuss trap.
- **Uniform vs plan:** Need an explicit precedence rule so hosts and CLI cannot send contradictory specs.

### Pipeline touchpoints (existing)

| Stage | Today (uniform) | v2.1 delta |
|-------|-----------------|------------|
| `models.py` | `dificuldade` + `quantidade` 1–40; `Exercise` = enunciado/resposta/explicacao | ItemSpec/plan; echo fields; maybe raise `MAX_QUANTIDADE` |
| `prompts.py` | Single difficulty instruction | Enumerated slots |
| generators + structured parse | One schema batch | Schema includes per-item meta |
| `validator.py` | `len == quantidade` | + plan adherence |
| `math_check` / RELY / failover | Unchanged contract | Reuse; no per-item effort routing |
| `reasoning.py` | Global effort | Stay global |
| `main.py` / `wizard.py` / `service.py` | Scalar flags / `generate_batch` | Plan UX + accept richer request |

## MVP Definition

### Launch With (v2.1 / SEED-006)

Minimum to stop being “uniform-only.”

- [ ] **Plan or ItemSpec on `GenerationRequest`** — essential: domínio por exercício
- [ ] **Mixed prompt + echoed dificuldade on each exercise** — essential: model can obey and we can check
- [ ] **Validator plan adherence (count + per-slot dificuldade)** — essential: reliability Core Value
- [ ] **Wizard/CLI batch-plan UX** — essential: operator ask #1 without N flags
- [ ] **Backward-compatible uniform requests** — essential: no embed/CLI regression
- [ ] **Discuss-resolved: tipo pedagógico vs API effort** — essential: avoid wrong API design; ship tipo enum only if confirmed pedagogical

### Add After Validation (v2.1.x / same milestone if capacity)

- [ ] **Pedagogical tipo per item (closed enum)** — trigger: discuss confirms content-level tipo
- [ ] **Modest raise of `MAX_QUANTIDADE`** — trigger: plan sums often exceed 40 for real provas; quality still holds
- [ ] **CLI compact plan syntax** (`--plano` / band counts) — trigger: wizard works; scripts need parity

### Future Consideration (post-v2.1)

- [ ] **Chunked generation for very large lots** — defer until single-call quality/context fails
- [ ] **OBS-01 usage on batch return** — parked; cost rises with mixed/large lots but not this milestone
- [ ] **BNCC / images / storytelling** — SEED-001 / SEED-003; out of scope
- [ ] **Per-band or per-item provider calls** — only if proven necessary
- [ ] **PKG-01 packaging** — parked

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Batch plan / distribution UX | HIGH | MEDIUM | P1 |
| Per-exercise difficulty (ItemSpec/plan) | HIGH | MEDIUM | P1 |
| Mixed prompt + schema echo | HIGH | MEDIUM | P1 |
| Validator plan adherence | HIGH | MEDIUM | P1 |
| Uniform backward compatibility | HIGH | LOW | P1 |
| Pedagogical tipo de raciocínio (enum) | HIGH | MEDIUM | P2 (P1 if discuss says must-have) |
| Raise finite quantity cap | MEDIUM | LOW–MEDIUM | P2 |
| Compact CLI `--plano` syntax | MEDIUM | LOW | P2 |
| Chunked multi-call large lots | MEDIUM | HIGH | P3 |
| Per-item API `reasoning_effort` | LOW (misframed) | HIGH | — Anti-feature |
| Unbounded quantity | LOW | LOW (trap) | — Anti-feature |
| BNCC / images / storytelling | — | — | Out of scope |

**Priority key:**
- P1: Must have for v2.1 launch
- P2: Should have when discuss/capacity allows
- P3: Nice to have / later milestone

## Competitor Feature Analysis

| Feature | Typical AI quiz/worksheet tools | CLI/lab generators (uniform) | Our approach (v2.1) |
|---------|--------------------------------|------------------------------|---------------------|
| Difficulty | Single level **or** “Mixed” / distribution counts | Often one `--difficulty` for whole batch | Explicit plan or ItemSpec; echo on each exercise |
| Question count | Caps ~5–50; “>50 = run twice” common | Small fixed caps | Raise finite cap; no unbounded; chunk later if needed |
| Reasoning / cognition | Bloom labels or “cognitive level” on content | Rare; or model temperature only | Pedagogical tipo enum on items; API `reasoning_effort` stays run-level |
| Output | HTML/worksheet + answer key | JSON or markdown | Keep structured `ExerciseBatch` JSON + validation |
| Authorship UX | Forms: counts per difficulty | Many flags / one shot | Wizard plan + argparse plan sugar |
| Standards (BNCC/CCSS) | Often marketed | Rare | Out of scope (SEED-001 dormant) |

## Sources

- SEED-006 (operator verbatim: dynamic lots, more quantity, per-exercise difficulty, tipo de raciocínio)
- `.planning/PROJECT.md` — v2.1 milestone goals and out-of-scope list
- Shipped code: `exercise-ai/models.py` (`GenerationRequest`, `MAX_QUANTIDADE=40`, `Exercise`), `validator.py` (count check), `reasoning.py` (global effort), `wizard.py` / `main.py` / `service.generate_batch`
- Industry patterns: AI quiz/worksheet generators exposing Mixed difficulty or easy/medium/hard distributions and finite per-run caps (e.g. SmartEduTools, LessonDraft, LogicBalls-style distribution prompts); CLI labs with uniform `--difficulty` (e.g. Quizard-style generators)
- Provider reality: OpenAI/Gemini/Grok reasoning/thinking knobs applied per request, not per item inside one structured completion — reinforces anti-feature AF on per-item API effort

---
*Feature research for: dynamic/mixed-difficulty exercise batch authoring (SEED-006 / v2.1)*
*Researched: 2026-09-21*
