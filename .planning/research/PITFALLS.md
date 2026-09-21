# Pitfalls Research

**Domain:** Adding per-exercise difficulty / pedagogical reasoning and mixed batches to an existing uniform-batch LLM exercise generator (Structured Outputs, RELY, math_check, CLI/wizard, embed `service.generate_batch`)
**Researched:** 2026-09-21
**Confidence:** HIGH for codebase-specific integration risks (models, validator, prompts, reasoning, caps, embed contract); MEDIUM for LLM adherence under mixed specs (provider-dependent)

> Scope note. v2.0 already shipped the embed seam. This milestone does **not** re-litigate `sys.exit`, env restore, or demo guards. Focus is SEED-006: moving from one `dificuldade` + `quantidade` to a **batch plan** (per-item difficulty and “tipo de raciocínio”), while keeping RELY, math_check, Structured Outputs, wizard, and `generate_batch` coherent.
>
> Suggested phase labels below match SEED-006 slices (A–E). Roadmap may renumber; keep the prevention intent.

---

## Critical Pitfalls

### Pitfall 1: Schema vs prompt mismatch (uniform prompt after mixed request)

**What goes wrong:**
`GenerationRequest` gains a list of per-item specs (or a batch plan), but `prompts.py` still fills a single `{dificuldade}` / `{quantidade}` template. The model sees “nível médio, gere 5” while the host expected 2 fáceis + 3 difíceis. Structured Outputs still returns a valid `ExerciseBatch` of length N — so RELY and length checks pass, and the product lies.

**Why it happens:**
Today prompt and request are 1:1 (`request.dificuldade`, `request.quantidade`). Easy to extend the Pydantic model and forget the only place the LLM reads intent. Providers that enforce schema do **not** enforce pedagogical alignment with the plan.

**How to avoid:**
Treat the prompt as a derived view of the plan: one canonical formatter that lists each slot (`#1 facil / raciocinio X`, …) and states “exercise i must match spec i”. Add a unit test that the built prompt contains every plan entry (no live LLM). Reject shipping schema without updating `build_*_prompt` in the same change.

**Warning signs:**
- Prompt golden/snapshot still mentions a single dificuldade string.
- Tests construct mixed `GenerationRequest` but assert only `len(exercicios) == quantidade`.
- Manual spot-check: all items feel same level despite a mixed plan.

**Phase to address:** Slice A (schema) and Slice B (prompt + validation) together — do not merge schema without prompt.

---

### Pitfall 2: Count of items vs specs length (`quantidade` vs `len(specs)`)

**What goes wrong:**
Two sources of truth: top-level `quantidade` and `len(item_specs)`. Callers pass `quantidade=5` with 3 specs, or specs with implied count and a stale `quantidade`. Validator today only checks `len(exercicios) == request.quantidade` — it never notices the plan is inconsistent. CLI/wizard/host each invent a different convention.

**Why it happens:**
Uniform batches made `quantidade` the only count. Adding a list without a single derivation rule invites drift across argparse, wizard, and `service.generate_batch`.

**How to avoid:**
Pick one rule and enforce at the Pydantic boundary (prefer: `quantidade` is derived as `len(specs)` and not independently settable; or require equality and fail fast with `InvalidRequestError`). Document the rule in README embed contract. CLI/wizard build specs first, then derive quantity — never the reverse.

**Warning signs:**
- Model fields both `quantidade` and `specs` without a validator tying them.
- Host bugs: wrong length batches or silent truncation of the plan.
- Error messages say “quantidade incorreta” when the real bug was a short specs list.

**Phase to address:** Slice A (schema / request contract) — before generators or UX.

---

### Pitfall 3: Pedagogical “tipo de raciocínio” confused with API `reasoning_effort`

**What goes wrong:**
Operators ask for “tipo de raciocínio por atividade” (SEED-006). Implementers wire per-item values into `LLM_REASONING_EFFORT` / `--reasoning` / `resolve_reasoning_effort()`, or name a prompt field `reasoning` that shadows API effort. Result: wrong cost profile (high effort for every item), provider kwargs applied incorrectly, or pedagogical intent never reaching the enunciado constraints. Gemini/OpenAI/Grok mappings in `reasoning.py` stay run-global — per-item API effort is not supported the same way.

**Why it happens:**
Same English word “reasoning” for two layers: (1) pedagogical skill/taxonomy in the exercise, (2) provider thinking/effort knob for the whole call. Wizard already has a reasoning step; easy to overload it.

**How to avoid:**
Discuss-phase lock two distinct names in the public contract (e.g. `tipo_raciocinio` / `raciocinio_pedagogico` vs `reasoning_effort`). Keep API effort **run-level** unless a provider later supports per-item (document that). Pedagogical type goes into prompt + optional output metadata / validation enum — never into `to_gemini_thinking_level` / OpenAI `reasoning_effort` kwargs.

**Warning signs:**
- Field named `reasoning` on an item spec with values `low|medium|high`.
- Wizard reuses the global reasoning prompt text for per-exercise “tipo”.
- Token/`[USAGE]` spikes when “adding tipo de raciocínio” without raising quantity.

**Phase to address:** Slice C (reasoning clarification) early — ideally before schema freeze; reinforce in Slice E (wizard copy).

---

### Pitfall 4: Breaking CLI / wizard / host embed contract

**What goes wrong:**
`GenerationRequest` shape changes (required new fields, removed uniform `dificuldade`, or different constructors). CLI argparse, `gerar` wizard, demo form, and host code that still builds `GenerationRequest(topico=…, dificuldade=…, quantidade=…)` break or silently default the whole batch to one level. `InvalidRequestError` kinds proliferate; demo and README drift.

**Why it happens:**
v2.0 promised a stable `generate_batch(request) -> ExerciseBatch`. Product pressure adds fields without a compatibility story (optional plan with uniform fallback vs. hard cut).

**How to avoid:**
Decide explicitly: (a) backward-compatible — uniform `dificuldade`+`quantidade` still works and expands to N identical specs; or (b) breaking — bump docs and update every adapter in one phase. Prefer (a) for embed hosts. Update CLI, wizard, `service` tests, and README contract in the same wave. Keep error `kind`s stable; add new validation messages, don’t rename existing ones without migration notes.

**Warning signs:**
- Only `test_service` updated; wizard/demo still call old kwargs.
- Host integration tests fail on `ValidationError` from Pydantic, not `InvalidRequestError`.
- README still documents only three request fields.

**Phase to address:** Slice A (compat rule) + Slice E (CLI/wizard/demo adapters); verify embed contract before marking milestone done.

---

### Pitfall 5: Unbounded cost from larger batches / raised caps

**What goes wrong:**
Cap rises above 40 (or chunking multiplies calls) without cost guards. One wizard session or host call burns large token budgets; RELY doubles worst-case (generate + regen). Failover may replay a huge batch on the second provider. OBS-01 (usage on return) is parked — operators lack in-band cost feedback.

**Why it happens:**
SEED-006 asks for “mais quantidade”; raising `MAX_QUANTIDADE` looks like a one-line change. Context limits and `$` scale with N × difficulty × reasoning_effort, not with “one batch”.

**How to avoid:**
Raise caps only with: hard max, optional chunk size, and clear UX estimate (“this may take several API calls”). Keep RELY bound (1–2). Prefer chunking with per-chunk `[USAGE]` over one giant Structured Output. Do not couple raise-cap to per-item API effort. Document that larger N increases timeout risk (Gemini 30s already).

**Warning signs:**
- Plan says “remove cap” without chunking design.
- Timeouts / truncated JSON increase after cap change.
- Token NDJSON days jump while feature flag “mixed batch” is on.

**Phase to address:** Slice D (caps & chunking) — after schema works for small mixed batches.

---

### Pitfall 6: Validation only checks length, not per-item difficulty adherence

**What goes wrong:**
`validate_exercise_batch` already checks count and non-empty fields, then `check_math_batch`. Mixed batches ship with items that ignore the plan (all “médio”). Product looks done; pedagogical control is fake.

**Why it happens:**
Length equality is easy and already tested. True difficulty/reasoning adherence needs either (1) model-echoed metadata fields in the Structured Output schema (`dificuldade` per exercise matching spec[i]), or (2) expensive human/LLM-as-judge — out of scope for a heavy overhaul, but a **minimal echo field** is in scope for mixed lots.

**How to avoid:**
Extend output schema with per-exercise `dificuldade` (and optional `tipo_raciocinio`) and assert `batch.exercicios[i].dificuldade == specs[i].dificuldade`. Keep checks offline in pytest with fixtures. Do not claim “domain over difficulty” if only prompt text changed. Math_check remains orthogonal — don’t overload it for difficulty.

**Warning signs:**
- Acceptance criteria say “mixed difficulty” but tests only assert `len == N`.
- Output `Exercise` still has only enunciado/resposta/explicacao.
- RELY never fires on “wrong difficulty” because nothing raises.

**Phase to address:** Slice B (prompt + validation) — core of the milestone quality bar.

---

### Pitfall 7: Naive chunking that shuffles or drops specs

**What goes wrong:**
Large plans are split into chunks of K for context/cost. Chunks are validated separately then concatenated — but order of specs is lost, RELY regenerates one chunk and remaps indices wrong, or failover retries only the last chunk. Final batch length matches `quantidade` while item i no longer matches spec i.

**Why it happens:**
Uniform batches chunk by count alone. Mixed batches must chunk **by plan slices** with stable indices.

**How to avoid:**
Chunk as contiguous slices of the specs list; pass slice-local prompts that still label global indices; concatenate in order; validate the **full** plan after merge (not only per-chunk length). RELY should regenerate the failing chunk against that chunk’s specs, then re-validate the merged batch. No parallel chunk fans (project constraint: sequential).

**Warning signs:**
- Chunk helper takes only `quantidade` and a single dificuldade.
- Tests for chunking use uniform fixtures only.
- Off-by-one: last chunk shorter and specs misaligned.

**Phase to address:** Slice D (caps & chunking) — only after Slice B validation knows about specs.

---

### Pitfall 8: RELY / math_check / failover assume a uniform request forever

**What goes wrong:**
`reliability` and `failover` pass the same `GenerationRequest` through. After schema change, regen prompts still say “all medium”, or math_check postmortems omit which spec failed. Failover OpenAI↔Gemini regenerates with a request object missing the plan field (defaulted), producing a different batch shape.

**Why it happens:**
Pipeline was built when request was four scalars. Deep call sites use `request.dificuldade` without going through a plan helper.

**How to avoid:**
Introduce a small accessor (`iter_specs(request)`, `effective_quantidade(request)`) used by prompt, validator, reliability, and logging. Grep for `.dificuldade` / `.quantidade` after the change. Fixture factories in tests must build mixed plans. Failover must serialize the full request — no reconstrution from env + three flags.

**Warning signs:**
- Grep shows prompt/validator updated but `reliability.py` / `failover.py` still format old fields.
- First attempt mixed, regen uniform (or vice versa).
- Postmortem JSON lacks per-item expected difficulty.

**Phase to address:** Slice B (wire-through) with regression tests; spot-check in Slice D if chunking adds paths.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Keep only prompt text for mixed difficulty; no echo fields | Ships UX faster | Cannot validate adherence; silent quality regression | Spike / discuss demos only — never as done for SEED-006 |
| Dual fields `quantidade` + `specs` without invariant | Less migration pain | Permanent off-by-one and host bugs | Never — fix at model boundary |
| Raise `MAX_QUANTIDADE` without chunking | Satisfies “more quantity” ask | Timeouts, cost spikes, fragile Structured Outputs | Only if new max stays small and tested (e.g. modest bump) |
| Reuse `--reasoning` for pedagogical tipo | One less flag | Cost/API confusion forever | Never — distinct names |
| Breaking `GenerationRequest` without uniform fallback | Cleaner model | Hosts/demo/CLI churn; embeds break | Only with explicit version/docs wave same phase |
| Per-item API `reasoning_effort` via N calls | True per-item compute | N× latency/cost; fights sequential embed contract | Out of scope unless later milestone; not v2.1 default |

## Integration Gotchas

Common mistakes when connecting to existing pipeline pieces and providers.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| OpenAI Structured Outputs / Pydantic `.parse()` | Change request only; leave `Exercise` schema unchanged | Add echo fields needed for validation; keep `strict` schema in sync with prompts |
| Gemini / Grok generators | Copy OpenAI prompt path; forget thinking/effort still global | Pedagogical fields in prompt; `reasoning_effort` / thinking level stay run-level via `reasoning.py` |
| `validate_exercise_batch` | Assert length only | Length + per-index spec match (+ existing nonempty + math_check) |
| RELY loop | Regenerate with stale uniform request | Same full plan object every attempt; bounded 1–2 |
| Failover OpenAI↔Gemini | Rebuild request from CLI globals | Pass original `GenerationRequest` unchanged |
| `service.generate_batch` | New required kwargs; Pydantic errors escape as raw `ValidationError` | Map bad plans to `InvalidRequestError`; preserve `kind` contract |
| CLI argparse + wizard `gerar` | N flags per exercise | Batch-plan UX (e.g. “2 facil, 3 medio”); derive specs once |
| Demo / host | Still posts uniform JSON body | Update contract + examples; keep uniform shorthand if compat promised |
| Token `[USAGE]` | Attribute cost only to `quantidade` | Log plan summary (mix + N); chunk rows if multi-call |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Single huge Structured Output | Truncation, parse errors, RELY thrash | Chunk by specs; validate merge | Roughly when N grows past current comfort (~40) or dense difíceis |
| RELY × full batch regen | Double token bill on one bad item | Prefer chunk-scoped regen if chunking exists | Any N≫10 with flaky math_check |
| High run-level reasoning_effort + large N | Slow calls, Gemini 30s timeout | Keep effort orthogonal; don’t raise both blindly | Medium+ effort with large mixed lots |
| Prompt listing every spec without summarization | Context bloat, ignored tail specs | Compact plan table; optional chunking | Long taxonomic “tipo” strings × high N |

## Security Mistakes

Domain-specific issues for this lab (not generic web OWASP).

| Mistake | Risk | Prevention |
|---------|------|------------|
| Logging full batch plans with secrets elsewhere in env dumps | Key leakage if debug expands | Keep LOG-02 discipline; never log API keys; plans are OK, env is not |
| Host accepts unbounded specs list from untrusted UI | Cost DoS against operator’s API key | Enforce max N at service boundary (same as CLI cap) |
| Free-text “tipo de raciocínio” injected raw into prompts without bounds | Prompt injection / junk cost | Enum or length-capped allowlist for pedagogical types |

## UX Pitfalls

Common operator-facing mistakes for mixed batches.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| N separate `--dificuldade` flags | Unusable for real provas | Plan DSL or repeated “add slot” in wizard |
| Wizard step still asks one dificuldade then quantity | Operator thinks mix is impossible | Plan-first step; show summary before call |
| Label global API reasoning as “tipo de raciocínio” | Wrong mental model; surprise bills | Separate copy: “esforço do modelo (custo)” vs “tipo pedagógico do exercício” |
| Silent fallback to all-médio when plan parse fails | Wrong exam, trusted output | Fail with clear `InvalidRequestError` / CLI message |
| No preview of cost/time when raising N | Anger after long/expensive run | Warn when N or mix exceeds thresholds |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Mixed request schema:** Uniform shorthand still works *or* all callers migrated — verify CLI, wizard, service tests, demo, README
- [ ] **Prompt:** Built string lists every spec / index — verify unit test on `build_*_prompt`
- [ ] **Count invariant:** `quantidade` ↔ `len(specs)` enforced in model — verify invalid combos raise before LLM
- [ ] **Per-item validation:** Echo fields checked index-wise — verify pytest fixtures for mismatched difficulty
- [ ] **Naming:** Pedagogical tipo ≠ `reasoning_effort` — verify wizard labels and field names
- [ ] **Pipeline wire-through:** reliability + failover + generators use plan helpers — verify grep for stale `.dificuldade`-only formatting
- [ ] **Caps:** New max has tests + optional chunking design — verify no “unlimited”
- [ ] **Chunking (if any):** Merge order preserves spec[i] — verify mixed fixture across chunk boundary
- [ ] **Embed errors:** Bad plans → `InvalidRequestError`, not raw Pydantic in host — verify `test_service`
- [ ] **Observability:** `[USAGE]` / logs mention N and mix — verify not only “quantidade=N”

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Schema/prompt mismatch | MEDIUM | Fix formatter; add prompt unit test; force one RELY-path regression with mixed fixture |
| quantidade vs specs drift | LOW | Add model invariant; fix callers to derive count; document |
| Reasoning name collision | MEDIUM | Rename fields; split wizard steps; audit `reasoning.py` call sites |
| Embed/CLI break | MEDIUM | Restore uniform fallback or publish breaking note; update demo/README same PR |
| Cost overrun | LOW–HIGH | Lower cap; disable chunk fan-out; set reasoning medium/low; pay bill / rotate keys if needed |
| Length-only validation | MEDIUM | Add echo fields + assertions; quarantine “shipped” claims until green |
| Chunk mis-merge | HIGH | Stop chunking in prod path; regenerate full batch with correct ordered specs; add merge test |
| RELY/failover stale request | MEDIUM | Thread full request object; add test: regen prompt contains same plan |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls (SEED-006 slices → likely v2.1 phases).

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Schema vs prompt mismatch | A+B Schema & Prompt | Prompt unit test lists all specs; spot mixed generation |
| quantidade vs specs length | A Request contract | Pydantic/InvalidRequest tests for mismatched counts |
| Pedagogical vs API reasoning | C Reasoning clarify (discuss → implement) | Distinct field names; wizard copy review; no per-item effort kwargs |
| CLI/wizard/host contract break | A compat + E UX adapters | Full caller matrix green; README embed section updated |
| Unbounded cost / raised caps | D Caps & chunking | Cap tests; usage warning; timeout soak at new max |
| Validation length-only | B Prompt + validation | Offline tests: wrong echo dificuldade → ValueError / RELY |
| Chunking shuffles specs | D Caps & chunking | Cross-boundary mixed fixture; full-plan validate after merge |
| RELY/failover uniform assumption | B wire-through (+ D if chunks) | Grep clean; failover test with mixed request object |

**Suggested phase order:** A (schema + count invariant + compat) → C naming lock (can start in discuss before A freeze) → B (prompt + per-item validation + pipeline wire-through) → E (CLI/wizard UX) → D (cap raise / chunking last).

## Sources

- SEED-006 (`seeds/SEED-006-dynamic-batch-per-exercise.md`) — operator intent and slices A–E
- PROJECT.md v2.1 milestone goals — mixed lots, cap review, wizard plan UX, reasoning clarify
- Codebase: `models.GenerationRequest` / `Exercise` (uniform today); `prompts.py` single dificuldade; `validator.validate_exercise_batch` length + nonempty + math_check; `reasoning.py` run-level effort; `main`/`wizard` `MAX_QUANTIDADE` 40; `service.generate_batch` embed contract
- Prior milestone lessons: RELY bounded; failover preserves request; Structured Outputs ≠ semantic truth
- OpenAI Structured Outputs pattern — schema adherence ≠ instruction adherence

---
*Pitfalls research for: v2.1 dynamic / mixed batches on existing LLM exercise generator*
*Researched: 2026-09-21*
