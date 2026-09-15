---
status: pending
quick_id: 260915-d26
slug: add-unified-reasoning-thinking-mode-for-
---

# Quick Plan: Unified reasoning mode (revised after provider research)

## Goal

Add `--reasoning` / `LLM_REASONING_EFFORT` (`none|low|medium|high`, default **`low`**) mapped efficiently:

- **Grok:** `reasoning_effort=` on existing `chat.completions.parse` (lab-proven)
- **Gemini:** `ThinkingConfig(thinking_level=...)` on existing `generate_content` (native SDK)
- **OpenAI:** pass only if model supports reasoning; **`gpt-4o-mini` omits** (no blind retry)

See `RESEARCH.md` for citations and rejected approaches (Responses migration, extra_body, thinking_budget).

## Approach (locked)

| Decision | Value |
|----------|--------|
| Flag | `--reasoning` (not `--thinking` / not profiles) |
| Env | `LLM_REASONING_EFFORT`; CLI wins |
| Default | `low` |
| Module | `exercise-ai/reasoning.py` — resolve + OpenAI allowlist + Gemini map (`none`→`minimal`) |
| OpenAI unsupported | **Omit param** + one-line stderr; **no** try/400/retry |
| Grok | Always pass `reasoning_effort` |
| Gemini | `thinking_level` only; never `thinking_budget`; `include_thoughts=False` |
| Waves | Grok tracer → Gemini → OpenAI gate |
| Out | Responses API, xai-sdk, SEED-004 wizard, model swaps |

## Tasks

### 1. Tracer — resolver + Grok wiring + CLI/env
- Add `reasoning.py`: `REASONING_LEVELS`, `resolve_reasoning_effort()`, `to_gemini_thinking_level()`, `openai_supports_reasoning_effort(model)`.
- Wire Grok/OpenAI-compatible `parse(..., **effort_kwargs)` where Grok always gets kwargs.
- `main.py`: `--reasoning`; export env before run (mirror `--provider`).
- Tests: resolve defaults/CLI; Grok mock receives `reasoning_effort="low"`.
- `.env.example` + README note (Grok honors; OpenAI default model may ignore).

### 2. Gemini ThinkingConfig
- Pass mapped `ThinkingConfig` into existing `GenerateContentConfig` alongside JSON schema.
- Tests: mock generate_content config includes `thinking_level="low"` for default; `none`→`minimal`.

### 3. OpenAI capability gate
- Build effort kwargs only when `openai_supports_reasoning_effort(model)`; else omit + stderr tip.
- Tests: `gpt-4o-mini` call has **no** `reasoning_effort`; allowlisted fake `gpt-5-mini` (or prefix) **has** it.
- Full `pytest exercise-ai -q`.

## Done when

- Three adapters behave per RESEARCH
- Default `low` when unset
- Suite green offline; no new PyPI deps

## Out of scope

- SEED-004 interactive wizard
- Migrating off chat.completions / google-genai generate_content
- Changing `DEFAULT_*_MODEL` strings
