---
id: "260923-cvj"
title: "Add GPT-6 Sol/Luna to OpenAI model selection"
status: planned
created: "2026-09-23"
---

# Quick Plan: GPT-6 Sol/Luna in selection list

## Goal

Add the new GPT-6 chat models **`gpt-6-luna`** and **`gpt-6-sol`** to `Modelos.txt` and the OpenAI selection fallbacks used by demo/CLI. **Exclude `gpt-6-astra`** from the selection list (keep it in the full catalog if already present).

## Tasks

### Task 1: Catalog + selection fallbacks
- Add `gpt-6-luna` and `gpt-6-sol` to `Modelos.txt` GPT section (near existing `gpt-6-astra`)
- Pin them in `OPENAI_MODEL_FALLBACKS` preferred so they appear in the capped picker (`GET /models`)
- Exclude `astra` from OpenAI generation fallbacks so Astra is not selectable
- Add `gpt-6` to OpenAI reasoning allowlist prefixes (Sol/Luna accept `reasoning_effort`)

### Task 2: Tests
- Assert catalog contains `gpt-6-luna` / `gpt-6-sol`
- Assert both appear in `OPENAI_MODEL_FALLBACKS`
- Assert `gpt-6-astra` is absent from fallbacks
- Assert `openai_supports_reasoning_effort('gpt-6-luna')` is True

## Done when
- Demo/OpenAI selection list includes Sol and Luna, not Astra
- Offline pytest for catalog + reasoning green
