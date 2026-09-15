# Phase 8 AI-SPEC — Provider Failover

**Selected Framework:** None (stdlib + existing OpenAI / google-genai paths only)
**Phase:** 08-provider-failover
**Date:** 2026-09-15

## Intent

This phase does **not** introduce a new agent framework, RAG, or multi-agent orchestrator. It adds a **thin failover envelope** around the existing `generate_validated_batch` path: if the primary provider fails with an eligible API availability error, retry once on the other of **OpenAI ↔ Gemini**.

## Model / provider boundary

| Role | Providers |
|------|-----------|
| Failover pair | OpenAI ↔ Gemini only |
| Out of failover | Grok (single-provider behavior; document) |
| Decision inputs | Exception kind from existing mappers — **not** token/USD metrics |

## Evaluation / verification

- Unit/integration tests with mocks only — **no live LLM**.
- Assert: failover on timeout/rate/conn/generic API; no failover on auth/math/invalid-response; Grok skip; missing secondary key → clear PT error; `[FAILOVER]` stderr without secrets.
- CI remains `pytest exercise-ai -q` without API secrets.

## Out of scope (AI)

- LangChain / CrewAI / AutoGen
- Grok in the failover chain
- Failover driven by math/validation failure or token cost
- Changing prompts / structured-output schemas (except env provider switch)
