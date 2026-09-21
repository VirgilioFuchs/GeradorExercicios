---
id: "260921-d9y"
status: complete
completed: "2026-09-21"
---

# Quick Summary: Model catalogs GPT/Gemini/Grok

## Done

- `exercise-ai/model_catalog.py` — parse `Modelos.txt` → full catalogs + filtered/capped FALLBACKS + defaults
- Gemini / OpenAI / Grok walk capacity fallovers via shared `model_candidates`
- Defaults: `gpt-5.6-luna`, `gemini-3.1-flash-lite`, `grok-4.6`
- Non-chat ids (image/tts/audio/realtime/…) excluded from generation fallbacks
- Tests: `tests/test_model_catalog.py`; suite **160 passed**

## Commits

(see git log for this quick)

## Notes

- Source of truth remains repo-root `Modelos.txt`
- Cap 12 fallbacks after prefer-order; full catalogs available as `*_MODELS`
