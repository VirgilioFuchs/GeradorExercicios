---
id: "260921-dsv"
title: "Demo model select from catalog"
status: planned
created: "2026-09-21"
---

# Quick Plan: Demo model selection

## Goal
Operator picks a model from `model_catalog` fallbacks in the demo Ambiente section; generation uses that model.

## Approach
- Scoped env `LLM_MODEL` (same pattern as provider/reasoning) — no `generate_batch` signature change
- `generate_exercises` reads `LLM_MODEL` when `model` arg is None
- `GET /models` returns fallback lists + defaults
- UI: `<select name="model">` refreshed when provider changes

## Tasks
1. Wire LLM_MODEL in generator + demo `_apply_env`
2. GET /models + form/JS
3. Tests (markers + /models + gerar with model env)
