---
status: complete
quick_id: 260911-fvq
slug: add-grok-provider-for-exercise-generatio
---

# Summary: Add Grok provider

## Done

- Grok (xAI) generation via existing OpenAI SDK + `base_url=https://api.x.ai/v1`, env **`GROK_API_KEY`**, default model **`grok-4.6`**.
- Shared OpenAI-compatible structured-output path (`_generate_with_openai_compatible` / `map_openai_compatible_error`) — DRY with OpenAI; logs `[API:grok]`; redacts `GROK_API_KEY`.
- CLI `--provider grok`, auto-detect after Gemini/OpenAI when only Grok key is set.
- Docs: `.env.example`, README env/flag tables.
- Tests (mocked only): resolve, empty choices, auth sanitize, CLI missing key / provider env — **80 passed**.

## Evidence

- Context7 `/websites/x_ai`: `OpenAI(..., base_url="https://api.x.ai/v1")` + `client.beta.chat.completions.parse`.
- Serena: inspected `_resolve_provider` / `generate_exercises` before edit.
- Semgrep MCP: unavailable (RPC connection lost) — not claimed as clean scan.

## Out of scope (unchanged)

- Phase 8 failover wiring
- SEED-002 token usage
- New `xai-sdk` dependency
