# Project Research Summary

**Project:** Gerador de Exercícios com IA
**Domain:** LLM math-exercise generation / dynamic mixed-difficulty batches (per-item specs)
**Milestone:** v2.1 Lotes dinâmicos (SEED-006)
**Researched:** 2026-09-21
**Confidence:** HIGH

## Executive Summary

v2.1 turns the shipped uniform batch pipeline into **lotes dinâmicos**: the operator authors a plan (e.g. 2 fáceis + 3 médios) with optional pedagogical reasoning type per exercise, instead of N copies of one difficulty. Experts ship this with nested Pydantic request/response schemas, an itemized Structured Outputs prompt, and offline plan-adherence validation — not with agent frameworks, per-item API `reasoning_effort`, or a second public generate API.

**Recommended approach:** add nothing to `requirements.txt`. Extend `GenerationRequest` with optional `itens` / plan specs, branch `prompts.build_prompts`, echo difficulty (and tipo) on `Exercise`, enforce plan adherence in `validator.py`, and expose compact plan UX in CLI/wizard — all while keeping `service.generate_batch(GenerationRequest) → ExerciseBatch` unchanged. Uniform scalar requests remain the backward-compatible path.

**Key risks:** schema/prompt mismatch (valid JSON that ignores the mix), length-only validation, confusing pedagogical “tipo de raciocínio” with run-level API `reasoning_effort`, and raising `MAX_QUANTIDADE` without cost/context guards. Mitigate with model invariants (`quantidade` ↔ `len(itens)`), echo-field checks, distinct naming, and cap raise only after small mixed lots prove out.

## Key Findings

### Recommended Stack

See [STACK.md](./STACK.md). **No new dependencies** for v2.1 — mixed batches are schema + prompt + validator + argparse/wizard work on the existing dual-provider Structured Outputs pipeline.

**Core technologies:**
- **Python 3.11+ / pydantic ≥2.0** — nested `list[ExerciseSpec]`, enums, `@model_validator`, `Field(min/max_length)` as single schema source for OpenAI + Gemini
- **openai ≥1.50 / google-genai ≥1.0** — keep `.parse(response_format=ExerciseBatch)` and `model_json_schema()`; enrich models, don’t change clients
- **argparse + stdlib plan parsing** — compact `--plano` / wizard counts; no Click/Typer/Rich
- **pytest ≥8** — offline plan expansion, adherence, and uniform-compat tests

### Expected Features

See [FEATURES.md](./FEATURES.md).

**Must have (table stakes):**
- Batch-plan / difficulty distribution UX (wizard + CLI without N flags)
- Per-exercise difficulty on the request (`itens` / plan → ordered specs)
- Mixed-aware prompt + echoed dificuldade on each `Exercise`
- Validator: count + per-slot plan adherence (then existing math_check / RELY)
- Backward-compatible uniform `dificuldade` + `quantidade`
- Finite raised quantity cap (domain + CLI aligned) — discuss exact number

**Should have (competitive):**
- Pedagogical `tipo_raciocinio` closed enum per item (not API effort)
- Stable slot order matching the plan; plan → ItemSpec as single source of truth
- Compact CLI `--plano` / band-count sugar; embed-friendly richer `GenerationRequest`

**Defer (post-v2.1 / parked):**
- Chunked multi-call large lots (unless single-call fails)
- Per-item API `reasoning_effort`; unbounded quantidade
- BNCC, images, storytelling, PKG-01, OBS-01, LOG-01

### Architecture Approach

See [ARCHITECTURE.md](./ARCHITECTURE.md). Keep the v2.0 library-core + thin-adapters shape: deepen request schema and the prompt/validator pair only. Same seam, failover envelope, RELY loop, and provider SDKs.

**Major components:**
1. **`models.py`** — `ExerciseSpec` + optional `itens` on `GenerationRequest`; echo fields on `Exercise`; `MAX_QUANTIDADE` review
2. **`prompts.py` / `validator.py`** — dual-mode prompt; plan length + per-index adherence (only pipeline leaves that must “understand” the plan)
3. **`main.py` / `wizard.py`** — plan UX adapters that expand to specs, then call unchanged `service.generate_batch`
4. **Unchanged** — `service` signature, failover, RELY, generators’ call shape, run-level `reasoning.py`

### Critical Pitfalls

See [PITFALLS.md](./PITFALLS.md).

1. **Schema vs prompt mismatch** — ship prompt branch + prompt unit tests in the same wave as schema; never schema-only
2. **`quantidade` vs `len(specs)` drift** — enforce one invariant at the Pydantic boundary before LLM
3. **Pedagogical tipo ≠ API `reasoning_effort`** — distinct names; effort stays run-level
4. **Length-only validation** — require echoed per-item fields and index-wise checks
5. **Embed/CLI break or unbounded cost** — uniform fallback; raise cap only after small mixed lots; no default N-call fan-out

## Implications for Roadmap

v2.0 ended at **phase 12**. Continue numbering from **13+**. Research dependency order (schema → prompt/validate → CLI/wizard → cap/polish) maps cleanly to **4 phases**; discuss may fold tipo naming into phase 13 or an early discuss gate before freeze.

Based on research, suggested phase structure:

### Phase 13: Request schema & plan contract
**Rationale:** Everything else reads the plan from types; count invariant and uniform compat must exist before prompts or UX invent conventions.
**Delivers:** `ExerciseSpec` (name TBD); optional `itens` on `GenerationRequest`; `quantidade` ↔ `len(itens)` validator; optional/required echo fields on `Exercise`; model unit tests; uniform path bit-compatible.
**Addresses:** Per-exercise difficulty / ItemSpec; backward-compatible uniform mode; discuss-locked naming for pedagogical tipo vs API effort (field presence may be optional until taxonomy locked).
**Avoids:** quantidade vs specs drift; breaking embed contract; conflating `reasoning` field with API effort.

### Phase 14: Mixed prompt + plan-adherence validation
**Rationale:** Structured Outputs enforce shape, not pedagogy; Core Value requires validator checks before claiming mixed lots work.
**Delivers:** Itemized `build_prompts` branch; validator length + per-slot dificuldade (/ tipo); pipeline wire-through so RELY/failover keep the full request; offline fixtures for mismatch → fail.
**Addresses:** Mixed prompt + schema echo; validator plan adherence; RELY/math_check reuse without redesign.
**Avoids:** Schema vs prompt mismatch; length-only validation; RELY regenerating a stale uniform request.

### Phase 15: CLI / wizard batch-plan UX
**Rationale:** Adapters last so domain rules are already enforced in-library; operators need plan UX without N flags.
**Delivers:** Wizard plan steps (counts per band ± tipo); argparse compact plan / band flags; derive `itens` then `quantidade`; README embed note that `itens` is additive; caller matrix (CLI, wizard, service tests) green.
**Addresses:** Batch-plan distribution UX; compact CLI sugar; embed-friendly same seam.
**Avoids:** Plan only in CLI free text; silent fallback to all-médio; wizard copy conflating API effort with tipo pedagógico.

### Phase 16: Quantity cap review & polish
**Rationale:** Cap raise after mixed lots work at small N; avoids cost/context bombs and premature chunking.
**Delivers:** Revisit `MAX_QUANTIDADE` (modest raise or keep 40) with domain+CLI lockstep; regression suite; optional demo touch only if acceptance needs it; document cost/timeout behavior. Chunking only if discuss proves single-call failure.
**Addresses:** Raised finite quantity cap; honest cost behavior.
**Avoids:** Unbounded quantity; naive chunk shuffle; raising cap before prompt/validator prove mixed quality.

### Phase Ordering Rationale

- **Schema first** — plan is first-class on `GenerationRequest`; CLI must not be the only place the plan exists (anti-pattern from research).
- **Prompt + validator together** — shipping schema without prompt/echo checks produces “looks done” false confidence.
- **UX after domain** — wizard/CLI expand plans; Pydantic owns bounds and enums.
- **Cap last** — SEED-006 “mais quantidade” is real but secondary to correct mixed adherence; chunking stays YAGNI unless measured need.
- **Pedagogical vs API reasoning** — lock in discuss / early phase 13 so schema freeze doesn’t bake the wrong layer.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 13:** Exact taxonomy / enum values for pedagogical `tipo_raciocinio`; whether `Exercise` echo fields are required vs optional (discuss).
- **Phase 16:** Final cap number and whether any sequential chunk path is warranted after soak at new max.

Phases with standard patterns (skip research-phase):
- **Phase 14:** Nested Structured Outputs + `@model_validator` already proven in-repo and via Context7; mirror existing `ExerciseBatch` list pattern.
- **Phase 15:** Argparse + existing `gerar` wizard extension; no new UX libraries.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Add-nothing stack; nested list `.parse()` / Gemini schema verified via Context7 + repo precedent |
| Features | HIGH | Table stakes align SEED-006 + industry mix UX; tipo taxonomy MEDIUM until discuss |
| Architecture | HIGH | Seam preserve is explicit PROJECT.md decision; touchpoints mapped to shipped modules |
| Pitfalls | HIGH | Codebase-specific integration risks well enumerated; LLM mix adherence MEDIUM (provider-dependent) |

**Overall confidence:** HIGH

### Gaps to Address

- **Tipo taxonomy:** closed enum values and whether tipo is P1 must-have or P2 — resolve in discuss-phase before schema freeze.
- **Exercise echo fields:** strongest validation needs them; discuss may prefer prompt-only (weaker) — decide in phase 13 planning.
- **Exact `MAX_QUANTIDADE`:** product ask vs context risk — measure after phase 14; finalize in phase 16.
- **Uniform vs plan precedence:** XOR vs plan-overrides — pick one rule, document, test (FEATURES anti-feature).

## Sources

### Primary (HIGH confidence)
- Context7 `/openai/openai-python`, `/openai/openai-cookbook`, `/websites/developers_openai_api` — nested list Structured Outputs, enums/arrays
- Context7 `/pydantic/pydantic` — nested models, `@model_validator`, list `Field` bounds
- Repo: `exercise-ai/models.py`, `prompts.py`, `validator.py`, `reasoning.py`, `service.py`, `main.py`, `wizard.py`
- `.planning/PROJECT.md` — v2.1 goals, embed contract, out of scope
- SEED-006 — operator intent and slices A–E

### Secondary (MEDIUM confidence)
- Industry quiz/worksheet “Mixed” / distribution patterns — table-stakes feature expectations
- Prior `.planning/research/*` (v2.0) — “add nothing” schema-only milestone precedent

### Tertiary (LOW confidence)
- Exact post-raise comfort zone for N (timeouts / truncation) — needs soak during phase 16
- Whether providers ever expose true per-item effort — out of scope for v2.1 default

---
*Research completed: 2026-09-21*
*Milestone: v2.1 Lotes dinâmicos (SEED-006)*
*Ready for roadmap: yes*
