---
quick_id: 260902-dq9
status: complete
---

# Quick Summary: Documentar formato da API key do Gemini

## What Changed

- Updated `exercise-ai/.env.example` to document both OpenAI and Gemini API key formats
- Added `GEMINI_API_KEY=` template with format hint (`AIza...`)
- Added format hint for existing `LLM_API_KEY` (`sk-...`)

## Files Modified

- `exercise-ai/.env.example`

## Verification

- File contains `LLM_API_KEY=`, `GEMINI_API_KEY=`, and format comments for both providers
- No real secrets included
