---
id: "260921-dsv"
status: complete
completed: "2026-09-21"
---

# Quick Summary: Demo model select

## Done

- `LLM_MODEL` scoped env (like provider/reasoning); `generate_exercises` honors it
- `GET /models` → fallback lists + defaults from `model_catalog`
- Demo Ambiente: `<select name="model">` refreshes by provider; POST `/gerar` sends `model`
- Tests: UI markers, `/models`, env restore, generator env read

## Notes

- Picker uses **fallbacks** (generation-suitable, capped), not the full Modelos.txt catalog
- Empty model = provider default
