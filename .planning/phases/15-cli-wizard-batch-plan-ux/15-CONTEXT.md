# Phase 15: CLI / wizard batch-plan UX - Context

**Gathered:** 2026-09-23  
**Status:** Ready for planning  
**Mode:** Operator approved agent-recommended defaults (all gray areas)

<domain>
## Phase Boundary

Operator defines a batch plan with compact UX on **wizard `gerar`** and **argparse** (UX-01, UX-02), producing the same `GenerationRequest` shapes the demo already uses after Phase 14. No new schema fields; no pedagogical “tipo de raciocínio”; no RELY/math redesign.

</domain>

<decisions>
## Implementation Decisions

### Wizard plan flow (UX-01)
- **D-01:** Replace the single dificuldade prompt with **three band counts** (fácil / médio / difícil), mirroring the demo. — **Reversibility:** costly — changes interactive contract operators already learn
- **D-02:** Keep a **quantidade** prompt (editable, like demo D-10). Soft-warn on stdout if sum=0 / sum>40 / qty≠sum; still build the request — **Pydantic remains the hard gate** (demo D-11 parity).
- **D-03:** Prompt order: matéria → tópico → **facil → medio → dificil** → quantidade → provider → reasoning → out.

### Argparse compact plano (UX-02)
- **D-04:** Add **`--plano F,M,D`** — three non-negative integers in **fácil→médio→difícil** order (e.g. `--plano 2,3,1`). Parse errors → clear argparse error. — **Reversibility:** costly — becomes the scripted compact API
- **D-05:** **`--plano` XOR legacy uniform:** if `--plano` is present, do **not** also require/use `--dificuldade` for mixed; for a single non-zero band under `--plano`, follow uniform legacy payload (D-07). If `--plano` absent, keep today’s `--dificuldade` + `--quantidade` behavior unchanged.
- **D-06:** Do **not** add three separate `--facil/--medio/--dificil` flags in this phase (YAGNI; `--plano` is enough).

### Uniform vs mixed payload (parity with demo D-12..D-14)
- **D-07:** **Mixed** (2+ bands with count > 0) → `GenerationRequest` with **`plano`** (+ `quantidade` = sum of bands). **Uniform** (exactly one band > 0) → legacy `{ dificuldade, quantidade }` with `dificuldade` from that band and `quantidade` = that band’s count (prefer band count over the editable qty field when constructing). Zero bands → let validation fail (or soft-warn then fail).
- **D-08:** Share one helper (e.g. `plan_ux.build_request_kwargs(...)`) used by **wizard and argparse** so demo/CLI/wizard stay aligned — **Reversibility:** costly — single source of band→request mapping

### Docs & verification
- **D-09:** Short README note + argparse `--help` examples for `--plano`; no new CONTRACT.md.
- **D-10:** Offline tests: argparse mixed/uniform/xor; wizard band answers → request kwargs; existing suite stays green (caller matrix: CLI path + wizard + service imports).

### Agent Discretion
- Exact soft-warn Portuguese copy
- Whether quantidade default when using `--plano` is sum(bands) vs leaving default unused
- Tip string updates in wizard for the new prompts

</decisions>

<specifics>
## Specific Ideas

- Operator: “coloque o que você achar melhor” — lock demo parity over inventing a CLI-only shape.
- Example mixed: `--plano 2,3,0` → plano facil=2, medio=3; quantidade=5.
- Example uniform via plano: `--plano 0,3,0` → dificuldade=medio, quantidade=3 (no plano field).

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — UX-01, UX-02
- `.planning/ROADMAP.md` — Phase 15 goal & success criteria
- `.planning/PROJECT.md` — v2.1; embed contract unchanged
- `.planning/phases/14-mixed-prompt-plan-adherence-demo-enablement/14-CONTEXT.md` — D-09..D-15 demo band/payload parity
- `.planning/phases/13-request-schema-plan-contract/13-CONTEXT.md` — plano XOR itens; expand order

### Code
- `exercise-ai/models.py` — `GenerationRequest`, `PlanoDificuldade`
- `exercise-ai/main.py` — `build_parser`, argparse → `GenerationRequest`
- `exercise-ai/wizard.py` — `collect_wizard_answers`, `run_wizard`
- `demo/app.js` — band→payload reference (D-12..D-14)

### Deferred (do not implement in Phase 15)
- TIPO-OPEN / pedagogical tipo de raciocínio
- CAP-02 raise qty cap
- Always-send-`plano` even for uniform (rejected in Phase 14)
- PKG-01 packaging

</canonical_refs>

<code_context>
## Existing Code Insights

### Reuse
- `PlanoDificuldade` / `GenerationRequest` validation already enforce sum vs quantidade
- Demo `buildGerarPayload` logic is the behavioral oracle for mixed vs uniform

### Don't reinvent
- Do not change service/`generate_batch` contract
- Do not redesign RELY or prompts

### Gaps this phase closes
- Wizard still asks scalar dificuldade only
- Argparse has no compact plano flag

</code_context>

<deferred>
## Deferred Ideas

- Separate `--facil/--medio/--dificil` flags (D-06 deferred)
- Wizard confirm-before-RELY (Phase 13 rejected for host; still out)

</deferred>
