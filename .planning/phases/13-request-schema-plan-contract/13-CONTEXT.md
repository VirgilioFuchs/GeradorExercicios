# Phase 13: Request schema & plan contract - Context

**Gathered:** 2026-09-21  
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver typed request/response contract for mixed (and uniform) batches: `plano` and/or `itens`, `dificuldades` band summary, count invariants, required `dificuldade` echo on each `Exercise` and `dificuldades` on `ExerciseBatch` — without changing `generate_batch(...) -> ExerciseBatch` return type. Cap stays 40. Pedagogical “tipo de raciocínio” stays **TIPO-OPEN** (out of this phase).

</domain>

<decisions>
## Implementation Decisions

### Forma do plano
- **D-01:** Support **both** `plano` (band counts) and `itens` (explicit ordered specs). `plano` expands internally to ordered `itens`. — **Reversibility:** costly — shapes CLI, wizard, host, and validators
- **D-02:** Expansion order from `plano`: **fácil → médio → difícil** (all of band A, then B, then C)
- **D-03:** If both `plano` and `itens` are present → **validation error** (XOR of sources)
- **D-04:** Request carries **`dificuldades`** (plural): the list of bands actually used (length 1, 2, or 3). Uniform / single-band → e.g. `["medio"]`; two bands → both; three → all three. Order fácil→médio→difícil among those present

### Precedência uniforme × misto
- **D-05:** Mode detection: presence of `plano` or `itens` → **mixed**; otherwise → **uniform**
- **D-06:** Legacy scalar `"dificuldade": "medio"` (no plano/itens) → **accept**; normalize internally to `dificuldades: ["medio"]` (compat)
- **D-07:** If `dificuldades` has **2+** bands but neither `plano` nor `itens` → **split `quantidade` equally** across those bands (heuristic plan)
- **D-08:** Remainder after equal split goes to the **last** band in fácil→médio→difícil order (e.g. qty 5, bands facil+medio → 2 fáceis + 3 médios)

### Echo em Exercise / Batch
- **D-09:** Every `Exercise` **must** include `dificuldade` (uniform and mixed)
- **D-10:** `ExerciseBatch` **must** echo `dificuldades` (same summary shape as request)
- **D-11:** Slot vs echoed `dificuldade` mismatch → **validation failure** (do not silently correct). Pipeline uses **bounded RELY**; surface as **typed error to the host**; write **postmortem on final fail** (operator transparency). Interactive “ask before RELY” rejected. — **Reversibility:** costly — locks Phase 14 validator/RELY behavior; postmortem detail may lean on SEED-005

### the agent's Discretion
- Exact Pydantic field names / model class names (`ExerciseSpec` vs `ItemSpec`) — planner/researcher may choose consistent PT/EN with existing `dificuldade` enum style
- Whether expansion lives as a pure function on the request model vs a small helper module

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — BATCH-01..04, CAP-01 (Phase 13); PROMPT/VAL for Phase 14
- `.planning/ROADMAP.md` — Phase 13 goal & success criteria
- `.planning/PROJECT.md` — v2.1 Current Milestone; embed contract
- `.planning/seeds/SEED-006-dynamic-batch-per-exercise.md` — original product intent
- `.planning/research/SUMMARY.md` — schema-first implications; pitfalls (quantidade drift, schema≠prompt)

### Code
- `exercise-ai/models.py` — `GenerationRequest`, `Exercise`, `ExerciseBatch`, `MAX_QUANTIDADE`, `DificuldadeEnum`
- `exercise-ai/service.py` — `generate_batch` seam (do not widen return)
- `exercise-ai/validator.py` — length checks today; Phase 14 extends adherence
- `exercise-ai/reliability.py` — bounded RELY; postmortem on final fail path

### Deferred (do not implement in Phase 13)
- `.planning/seeds/SEED-005-usable-postmortem.md` — richer postmortem UX (D-11 surfaces need; polish later)
- TIPO-OPEN in REQUIREMENTS.md — pedagogical tipo taxonomy

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `DificuldadeEnum` / `MAX_QUANTIDADE = 40` in `models.py`
- Pydantic `Field(ge/le)` and `@field_validator` patterns already on `GenerationRequest`

### Established Patterns
- Structured Outputs via `ExerciseBatch`; validators after LLM
- Embed contract: same models for host and CLI

### Integration Points
- Phase 15 CLI/wizard will author `plano` or expand to `itens`
- Phase 14 prompt/validator consume expanded ordered specs + echo fields

</code_context>

<deferred>
## Deferred Ideas

- **TIPO-OPEN** — pedagogical reasoning type per item (research later; not Phase 13 schema)
- **CAP-02** — raise quantity cap after v2.1
- Interactive wizard confirm before RELY — rejected for host path; may revisit for wizard-only UX later
- Full catalog model picker already shipped in demo (unrelated to batch schema)

</deferred>
