# Phase 10 AI-SPEC — Interactive CLI Wizard

**Selected Framework:** None (stdlib `input` / argparse only)
**Phase:** 10-interactive-cli-wizard
**Date:** 2026-09-15

## Intent

Add a Portuguese interactive Q&A entry via first CLI token `gerar`. Answers map into the existing generation pipeline (`GenerationRequest`, provider env, reasoning env, `--out`). No new LLM framework, agent loop, or GUI.

## Model / provider boundary

| Concern | Behavior |
|---------|----------|
| Generation | Unchanged pipeline (`run` / reliability / generators) |
| Reasoning default | Align global default to `medium` (D-08) |
| Providers | openai / gemini / grok / auto-detect — existing keys |

## Evaluation / verification

- Mock `input()` / TTY checks — **no live LLM**, no real TTY required in CI.
- Assert argv `gerar` path vs argparse path; mapping to `run` kwargs; re-prompt for empty JSON path.
- CI remains `pytest exercise-ai -q` via argparse flags (WIZ-03).

## Out of scope (AI)

- LangChain / agents / RAG
- Phase 8 failover logic
- Saved profiles / GUI
- Asking max-retries in wizard
