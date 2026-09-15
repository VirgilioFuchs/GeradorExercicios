# Phase 9 AI-SPEC — Token Usage Observability

**Selected Framework:** None (stdlib + existing provider SDKs only)
**Phase:** 09-token-usage-observability
**Date:** 2026-09-11

## Intent

This phase does **not** introduce a new agent, RAG stack, or LLM orchestration framework. It adds **observability** around the existing OpenAI / Gemini / Grok generation path: extract usage metadata, estimate or read USD cost, append NDJSON, print `[USAGE]` on stderr.

## Model / provider boundary

| Provider | Usage source | USD source |
|----------|--------------|------------|
| OpenAI | `completion.usage` prompt/completion/total | Local rate table (USD/1M) |
| Gemini | `usage_metadata` token counts | Local rate table (USD/1M) |
| Grok | OpenAI-compatible `usage` | Prefer `cost_in_usd_ticks / 1e10`; else rate table / `indisponível` |

Missing fields → string `indisponível` (never fabricate `0`).

## Evaluation / verification

- Unit tests with mocked usage objects only — **no live LLM**.
- Assert NDJSON append, day+provider path, redaction of secrets, RELY attempt/error/success events.
- CI remains `pytest exercise-ai -q` without API secrets.

## Out of scope (AI)

- New agent loops, tool-calling agents, LangChain/CrewAI
- Live Admin billing APIs
- Pricing-page scrape
- Changing exercise generation quality / prompts (except reading usage from responses)
