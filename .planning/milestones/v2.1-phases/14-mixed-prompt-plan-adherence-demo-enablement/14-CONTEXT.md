# Phase 14: Mixed prompt + plan-adherence + demo enablement - Context

**Gathered:** 2026-09-22  
**Status:** Ready for planning

<domain>
## Phase Boundary

Mixed batches are instructed in the prompt, checked for plan adherence in the pipeline, and enabled in the local demo — same `GenerationRequest` contract from Phase 13. RELY and `math_check` are **not** redesigned. Requirements: PROMPT-01, VAL-01, VAL-02, DEMO-01. CLI/wizard compact plan UX stays Phase 15.

</domain>

<decisions>
## Implementation Decisions

### Prompt slot list (PROMPT-01)
- **D-01:** When a plan is present, the user prompt includes a **numbered slot list** derived from `request.itens_ordenados` (slot index → expected dificuldade).
- **D-02:** **Always enumerate** slots — including uniform / single-band batches (same shape; no special “scalar only” prompt branch that omits the list).
- **D-03:** **Do not** re-list response field contracts (`enunciado` / `resposta` / `explicacao`) in prompt prose — Structured Outputs + `ExerciseBatch` remain format authority (aligns with SEED-008).
- **D-04:** Difficulty labels in the slot list are **hybrid**: Portuguese display plus enum value, e.g. `fácil (facil)` / `médio (medio)` / `difícil (dificil)`.

### Validator / RELY hook (VAL-01, VAL-02)
- **D-05:** Call **`verify_plan_echo` from `reliability.py`**, not from `validate_exercise_batch`. Validator stays length/emptiness (+ existing math via validate); plan adherence is a separate RELY-owned check.
- **D-06:** Order: **`validate_exercise_batch` first**, then **`verify_plan_echo`** (structural/math OK before slot check).
- **D-07:** Fail on **per-slot echo mismatch and** on **batch-level `ExerciseBatch.dificuldades` ≠ request summary** (stricter than slots-only). Still fail-closed (no silent correct); same bounded RELY / typed host error / postmortem-on-final-fail behavior locked in Phase 13 D-11.
- **D-08:** Do **not** redesign RELY loop bounds, math_check, or failover — VAL-02.

### Demo band UX (DEMO-01)
- **D-09:** Form uses **three count inputs** (fácil / médio / difícil); remove the single `dificuldade` select.
- **D-10:** Keep **`quantidade` editable** beside the three counts (operator may desync; server/Pydantic is the hard gate).
- **D-11:** Client validation is **soft only** — warn in UI for sum=0 / sum>40 / qty≠sum; still allow POST; hard fail remains server-side.

### Demo payload shape (DEMO-01)
- **D-12:** Send **`plano` only when mixed** (2+ bands with count > 0). Uniform / single non-zero band keeps legacy `{ dificuldade, quantidade }` (no `plano`).
- **D-13:** Uniform path: **derive `dificuldade` from the sole non-zero band**.
- **D-14:** Uniform path: payload **`quantidade` = that band’s count** (prefer band count over the editable qty field when building the POST body).
- **D-15:** `demo/serve.py` must accept `plano` (and existing fields) into `GenerationRequest` so mixed POST is not dead schema.

### Claude's Discretion
- Exact prompt wording / template structure for the slot list (as long as D-01–D-04 hold)
- How to implement batch-summary check (extend `verify_plan_echo` vs small helper next to it)
- Soft-warn copy and placement in the demo UI
- Exact JSON field names already fixed by `PlanoDificuldade` / models — do not invent a parallel demo-only shape

</decisions>

<specifics>
## Specific Ideas

- Mid-discuss: operator planted **SEED-008** — response structure over prompt; Phase 14 must not “fix” Exercise fields via longer field-list prose.
- Hybrid label example locked as `fácil (facil)` style (accented PT + raw enum).

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — PROMPT-01, VAL-01, VAL-02, DEMO-01
- `.planning/ROADMAP.md` — Phase 14 goal & success criteria (incl. demo)
- `.planning/PROJECT.md` — v2.1 milestone; embed contract
- `.planning/phases/13-request-schema-plan-contract/13-CONTEXT.md` — D-01..D-11 plan/echo contract (carry-forward; do not re-litigate)
- `.planning/phases/13-request-schema-plan-contract/13-01-SUMMARY.md` — `itens_ordenados`, pure `verify_plan_echo`, Phase 14 wiring note
- `.planning/seeds/SEED-008-response-structure-over-prompt.md` — schema+validator as format authority; prompt hygiene
- `.planning/seeds/SEED-006-dynamic-batch-per-exercise.md` — original mixed-batch product intent
- `.planning/research/SUMMARY.md` / `.planning/research/PITFALLS.md` — schema≠prompt; RELY identity; length-only validation pitfall

### Code
- `exercise-ai/models.py` — `GenerationRequest`, `PlanoDificuldade`, `itens_ordenados`, `verify_plan_echo`, echo fields
- `exercise-ai/prompts.py` — current uniform `{dificuldade}` / `{quantidade}` template (PROMPT-01 target)
- `exercise-ai/validator.py` — length/emptiness + `check_math_batch` (keep; do not add plan echo here per D-05)
- `exercise-ai/reliability.py` — RELY loop; wire `verify_plan_echo` after validate (D-05/D-06)
- `demo/index.html`, `demo/app.js`, `demo/serve.py` — form + POST `/gerar` → `GenerationRequest` (DEMO-01)

### Deferred (do not implement in Phase 14)
- `.planning/REQUIREMENTS.md` UX-01/UX-02 — CLI/wizard (Phase 15)
- `.planning/seeds/SEED-005-usable-postmortem.md` — richer postmortem UX
- `.planning/seeds/SEED-007-exercise-ai-persona-rules.md` — domain persona contract (not this phase)
- TIPO-OPEN — pedagogical tipo taxonomy

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `request.itens_ordenados` — ordered specs after normalize (prompt + echo source of truth)
- Pure `verify_plan_echo(batch, request)` — raises `ValueError` on slot mismatch; not wired yet
- `PlanoDificuldade.expand()` — fácil→médio→difícil order (Phase 13 D-02)
- Demo tracer tests under `demo/tests/` — extend for `plano` POST paths

### Established Patterns
- RELY retries on `ValueError` from validation; keep plan failures on that path
- Demo builds JSON in `app.js` and constructs `GenerationRequest(...)` field-by-field in `serve.py` (must stop defaulting away `plano`)
- Structured Outputs `response_format=ExerciseBatch` — format authority (SEED-008)

### Integration Points
- `reliability.generate_validated_batch` — insert echo after `validate_exercise_batch`
- `prompts.build_prompts` — consume `itens_ordenados` for enumeration
- `demo/serve.py` POST `/gerar` — pass `plano` through to models
- Phase 15 CLI/wizard will reuse the same `plano` contract once demo proves it

</code_context>

<deferred>
## Deferred Ideas

- CLI/wizard compact `--plano` / wizard counts — Phase 15 (UX-01/UX-02)
- SEED-005 postmortem polish — later
- SEED-007 persona/rules package — later
- Hard client-side block on invalid totals — rejected for Phase 14 (soft warn only)
- Always-send-`plano` (even uniform) — rejected; keep legacy uniform payload shape

</deferred>

---

*Phase: 14-mixed-prompt-plan-adherence-demo-enablement*
*Context gathered: 2026-09-22*
