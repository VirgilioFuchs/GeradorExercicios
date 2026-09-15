# RESEARCH — Unified reasoning / thinking mode (revised)

**Quick:** 260915-d26  
**Revised:** 2026-09-15 (Context7 + lab + OpenAI model-support evidence)

## Goal

One operator-facing effort knob that maps to each provider’s **native, documented** control — with the **cheapest correct wiring** (no Responses API migration, no OpenAI-compat shim for Gemini, no blind retry loops).

## Efficient implementation principles

1. **Stay on existing call paths** — keep Structured Outputs / JSON schema already in production.
2. **Pass native params only when supported** — never send a reasoning field to models that 400 on it.
3. **Prefer capability gates over try/fail/retry** — one fewer round-trip, deterministic tests.
4. **One shared level enum + thin per-provider adapters** — avoid three CLIs / three env vars.

---

## Provider findings

### Grok (xAI) — validated & cheapest win

| Item | Finding | Source |
|------|---------|--------|
| Preferred docs surface | Responses API `reasoning: { effort }` (`low\|medium\|high\|xhigh`) | docs.x.ai `/v1/responses` |
| Chat Completions | Marked **legacy**, still supported; longer timeouts recommended for heavy reasoning | docs.x.ai legacy chat-completions |
| **Lab (this repo)** | `client.beta.chat.completions.parse(..., reasoning_effort="low")` works; cut ~11s → ~3.6s and reasoning_tokens 434→80 | live test 2026-09-15 |
| `extra_body={"reasoning":{"effort":...}}` | Did **not** reduce tokens on chat.completions | same lab |
| Efficient choice | **Keep** `chat.completions.parse` + kwarg `reasoning_effort=` — do **not** migrate to Responses in this quick (would rework Structured Outputs) | YAGNI |

**Adapter:** always pass `reasoning_effort=<unified>` for Grok (`none` if API rejects later → then gate; today lab used `low`).

---

### OpenAI — gate by model, do not retry

| Item | Finding | Source |
|------|---------|--------|
| Param | Chat Completions: `reasoning_effort` (`none\|minimal\|low\|medium\|high\|xhigh\|max`) | developers.openai.com Chat Completions params |
| Preferred modern API | Responses: `reasoning: { effort }` on **reasoning** models (GPT-5.x / o-series) | Reasoning guide |
| **`gpt-4o-mini` (our default)** | **Does not support** reasoning — sending `reasoning.effort` / `reasoning_effort` → HTTP 400 `unsupported_parameter` | OpenAI model page + community/SDK gates (e.g. Codex #36735) |
| Efficient choice | **Omit** the param for non-reasoning models. **Do not** “try then retry without” (wastes latency + muddies errors). | capability gate |

**Adapter:**

```text
if model_supports_reasoning_effort(model):
    kwargs["reasoning_effort"] = mapped_level
# else: omit entirely (even for "none")
```

Initial allowlist (conservative, extend later): models matching `gpt-5*`, `o1*`, `o3*`, `o4*` (and documented reasoning IDs). **`gpt-4o-mini` / `gpt-4o` → omit.**

Stderr once when operator set a level but model cannot use it:  
`[API:openai] reasoning_effort não suportado por {model}; ignorado.`

---

### Gemini (google-genai) — ThinkingConfig on existing generate_content

| Item | Finding | Source |
|------|---------|--------|
| Native (our SDK path) | `GenerateContentConfig(thinking_config=ThinkingConfig(thinking_level=...))` | ai.google.dev flash-lite + thinking docs |
| Levels | `minimal` \| `low` \| `medium` \| `high` — **prefer `thinking_level` over numeric `thinking_budget`** | Gemini 3.5 what’s-new |
| Do not combine | `thinking_level` + `thinking_budget` → **400** | same |
| Defaults | Flash-Lite often defaults toward speed (`minimal`); Flash toward `medium` | what’s-new |
| OpenAI-compat Gemini endpoint | Can use `reasoning_effort` **or** google `thinking_config` — not both; we **already use native google-genai** | ai.google.dev openai compat |
| Efficient choice | Stay on **native** `google.genai` + `ThinkingConfig`; set `include_thoughts=False` (must not leak thoughts into exercise JSON) | KISS + LOG-02 |

**Adapter:** map unified → Gemini level; attach only `thinking_config` (never budget).

| Unified | Gemini `thinking_level` |
|---------|-------------------------|
| `none` | `minimal` |
| `low` | `low` |
| `medium` | `medium` |
| `high` | `high` |

If a future fallback model rejects `thinking_level`, **then** omit config once (narrow catch) — not the primary strategy.

---

## Recommended architecture (efficient)

```
CLI --reasoning / env LLM_REASONING_EFFORT
        ↓
resolve_reasoning_effort() → Literal["none","low","medium","high"]  # default low
        ↓
┌─────────────────┬──────────────────────┬─────────────────────┐
│ Grok adapter    │ OpenAI adapter       │ Gemini adapter      │
│ always kwargs   │ gate by model        │ ThinkingConfig      │
│ reasoning_effort│ omit if unsupported  │ thinking_level map  │
└─────────────────┴──────────────────────┴─────────────────────┘
        ↓
existing parse / generate_content (unchanged schema)
```

**Module:** `exercise-ai/reasoning.py` (resolve + maps + `openai_supports_reasoning_effort(model)`) — keeps generators thin.

**Not in this quick:** Responses API migration, xai-sdk, Gemini OpenAI-compat base_url, wizard CLI (SEED-004).

---

## Wave strategy (revised)

| Wave | Why |
|------|-----|
| **1 — Grok tracer** | Already proven live; highest latency ROI; proves CLI/env/resolver |
| **2 — Gemini** | Same product surface; native ThinkingConfig next to existing JSON schema |
| **3 — OpenAI gate** | Documented non-support on `gpt-4o-mini`; implement omit + allowlist + stderr tip |

**Fallback policy (revised):**  
- ❌ Blind “call with param → on 400 retry without” as default for OpenAI  
- ✅ Capability gate for OpenAI  
- ✅ Optional narrow Gemini omit-on-reject only if fallback models 400  

---

## Flag / env (locked proposal)

- CLI: `--reasoning {none,low,medium,high}` (clearer than `--thinking` for Grok/OpenAI docs language)
- Env: `LLM_REASONING_EFFORT`
- Default: `low`
- CLI overrides env

---

## Test strategy (offline)

- Mock assert Grok/OpenAI `parse` called with/without `reasoning_effort`
- Mock assert Gemini `GenerateContentConfig` includes `thinking_config.thinking_level`
- Assert `gpt-4o-mini` path **never** passes reasoning kwarg
- CLI invalid value → argparse error
- No live LLM in CI

## Risks

| Risk | Mitigation |
|------|------------|
| Allowlist misses a new OpenAI reasoning model | Extensible prefix list + stderr when omitted |
| Gemini fallback model rejects thinking_level | Narrow retry-without-config; log once |
| Operator expects OpenAI gpt-4o-mini to “think less” | Docs: OpenAI default model ignores flag; Grok/Gemini honor it |
| xAI pushes Responses-only later | Out of scope; note in RESEARCH for future quick |
