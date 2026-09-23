---
id: "260923-cvj"
status: complete
completed: "2026-09-23"
commit: "4bba7fd"
---

# Quick Summary: GPT-6 Sol/Luna in OpenAI selection

## Done

- `Modelos.txt`: added `gpt-6-luna`, `gpt-6-sol` (Astra remains in full catalog only)
- `model_catalog.py`: preferred fallbacks pin Sol/Luna; exclude `astra` from selection/generation fallbacks
- `reasoning.py`: `gpt-6` prefix accepts `reasoning_effort`
- Tests: catalog + reasoning assertions; **18 passed**

## Selection list (OpenAI fallbacks)

`gpt-5.6-luna`, `gpt-6-luna`, `gpt-6-sol`, … — **no** `gpt-6-astra`

## Note

Restart `demo/serve.py` after pull so `/models` refreshes.
