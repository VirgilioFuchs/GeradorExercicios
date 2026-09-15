---
status: complete
quick_id: 260911-fvq
slug: add-grok-provider-for-exercise-generatio
---

# Quick Plan: Add Grok provider

## Goal

Allow generating exercises via **Grok (xAI)** using `GROK_API_KEY` (already in `.env.example`), mirroring OpenAI/Gemini patterns without new agent frameworks.

## Approach (locked)

- **Reuse OpenAI Python SDK** with `base_url="https://api.x.ai/v1"` and `api_key=GROK_API_KEY` ([CITED: docs.x.ai OpenAI-compatible + structured outputs]).
- **No new PyPI package** (openai already in requirements).
- Env name: **`GROK_API_KEY`** (operator’s `.env.example`), not `XAI_API_KEY`.
- Default model: `grok-4.6` (xAI docs examples).
- Logs: `[API:grok]` type+status only; redact `GROK_API_KEY` like other keys.
- CLI: `--provider grok`; auto-detect after gemini/openai when only Grok key present.
- Tests: mocks only — no live LLM.

## Tasks

1. Refactor `generator.py` OpenAI path into shared OpenAI-compatible helper; add Grok client + dispatch.
2. Update `main.py` (`_ensure_provider_key`, `--provider` choices).
3. Update `.env.example` comment for `LLM_PROVIDER` to include `grok`; README env/flag tables.
4. Extend tests (resolve provider, CLI, empty choices / auth sanitize for grok).
5. Run `pytest exercise-ai -q`; Semgrep on changed files if available.

## Out of scope

- Failover Phase 8 wiring of Grok as secondary
- SEED-002 token usage
- New SDK (`xai-sdk`)
