---
quick_id: 260902-dt4
status: complete
---

# Quick Summary: Gerador Gemini

## What Changed

- Added `exercise-ai/generator_gemini.py` using Google Gemini structured JSON output (`gemini-2.0-flash` default)
- Updated `exercise-ai/generator.py` to auto-select provider via `LLM_PROVIDER` or available API keys (prefers Gemini when only `GEMINI_API_KEY` is set)
- Added `google-genai>=1.0.0` to requirements
- Documented optional `LLM_PROVIDER` in `.env.example`

## Usage

1. Copy `.env.example` to `.env`
2. Set `GEMINI_API_KEY=AIza...` (leave `LLM_API_KEY` empty)
3. Run `python main.py` from `exercise-ai/`

## Files Modified

- `exercise-ai/generator_gemini.py` (new)
- `exercise-ai/generator.py`
- `exercise-ai/requirements.txt`
- `exercise-ai/.env.example`
