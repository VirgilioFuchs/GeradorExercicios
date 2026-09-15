---
status: complete
quick_id: 260915-d26
slug: add-unified-reasoning-thinking-mode-for-
---

# Quick Summary: Unified reasoning / thinking mode

## What shipped

Operator-facing `--reasoning` / `LLM_REASONING_EFFORT` (`none|low|medium|high`, default **`low`**) mapped per provider without Responses API migration:

- **Grok:** `reasoning_effort=` on existing `chat.completions.parse`
- **Gemini:** `ThinkingConfig(thinking_level=..., include_thoughts=False)` (`none`→`minimal`)
- **OpenAI:** capability gate — omit on `gpt-4o-mini`; pass for `gpt-5*` / `o*` prefixes + stderr tip when ignored

## Files

| File | Change |
|------|--------|
| `exercise-ai/reasoning.py` | **Created** — resolve + adapters |
| `exercise-ai/generator.py` | Effort kwargs on OpenAI-compatible parse |
| `exercise-ai/generator_gemini.py` | ThinkingConfig on generate_content |
| `exercise-ai/main.py` | `--reasoning` → env |
| `exercise-ai/tests/test_reasoning.py` | **Created** — offline mocks |
| `README.md`, `.env.example` | Document flag/env + provider notes |
| `RESEARCH.md`, `PLAN.md` | Provider research + revised plan |

## Tests

`pytest exercise-ai -q` → **102 passed**

## Out of scope (unchanged)

SEED-004 interactive wizard; Responses API; model default swaps
