# Project Research Summary

**Project:** Gerador de Exercícios com IA  
**Domain:** Domain AI generation contract + schema-as-format-authority  
**Researched:** 2026-09-23  
**Confidence:** HIGH  
**Milestone:** v2.2 Contrato de geração (SEED-007 + SEED-008)

## Executive Summary

v2.2 hardens how humans and agents treat generation: a domain skill/rules contract (persona, capabilities, pipeline order, validation≠thinking≠response) plus prompt hygiene so **schema + code** own format, not SYSTEM_PROMPT prose. The shipped v2.1 pipeline (`generate_batch` → Structured Outputs → validate → math → `verify_plan_echo` → RELY) stays intact.

**Delivery note (Phase 16 discuss):** user locked **API** skill package under `exercise-ai/skills/generation/` — not Cursor/agent folders (`.cursor` / `.claude` / `.codex`). Research below still applies for persona/rules/schema-as-authority; ignore “Cursor skill path” as the Phase 16 vehicle.

Recommended approach: **zero new runtime dependencies**. Prompt content + code-owned validation; no LLM self-check, schema dumps in prompts, RELY redesign, or packaging in this milestone.

Key risks: agents re-paste JSON schema into SYSTEM_PROMPT; “validate yourself” instructions; confusing `reasoning_effort` with pedagogical tipo; breaking Phase 14 slot lists while cleaning SYSTEM prose.

## Key Findings

### Recommended Stack

No new packages. Format authority remains Pydantic + Structured Outputs; plan authority remains `verify_plan_echo`; content = prompts / API persona modules only.

### Expected Features

**Must have:** API persona/rules modules, triad/authority docs, prompt rewrite, strip field-contract prose, light code hooks, offline policy tests.

**Defer:** PKG-01, multi-persona packs, LangChain validators, BNCC/images, CAP-02, TIPO-OPEN.

### Architecture Approach

Agent-facing Cursor skills are **out** for v2.2 delivery (user decision). Runtime: `exercise-ai/skills/generation/` → future `prompts.py` consumer. Validation stays code-owned.

**Build order (roadmap):** Phases 16–25, one REQ each (skill skeleton → triad → authority → prompts → hygiene/tests).

### Critical Pitfalls

1. Dumping JSON schema into SYSTEM_PROMPT  
2. Asking the model to validate itself  
3. Mixing `reasoning_effort` with pedagogical tipo  
4. Breaking Phase 14 slot enumeration while stripping field prose  

## Implications for Roadmap

See `.planning/ROADMAP.md` phases 16–25. Phase 16 CONTEXT overrides research “Cursor skill” path with `exercise-ai/skills/generation/`.

## Sources

- `.planning/research/STACK.md`, `FEATURES.md`, `ARCHITECTURE.md`, `PITFALLS.md`
- SEED-007, SEED-008
- `.planning/phases/16-domain-skill-index/16-CONTEXT.md`

---
*Synthesized 2026-09-23 for v2.2; SUMMARY restored at pause 2026-09-23*
