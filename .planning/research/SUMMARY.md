# Project Research Summary

**Project:** Gerador de Exercícios com IA
**Domain:** Python LLM pipeline for math exercise generation
**Researched:** 2026-09-01
**Confidence:** HIGH

## Executive Summary

This project is a small, educational Python application that generates math exercises via an LLM using a linear pipeline: structured prompt → API call → JSON → validation → output. Research confirms the standard 2025–2026 approach for reliable structured output is OpenAI's Structured Outputs with Pydantic models (`chat.completions.parse`), not prompt-only JSON parsing.

The MVP should remain a flat module layout (main, generator, validator, prompts, models) without agent frameworks, RAG, or databases. Table stakes are parameterized input, three-field exercise structure, structural validation, environment-based secrets, and validator unit tests. The main risks are fragile JSON parsing, wrong exercise counts, empty fields, and API key leakage — all addressable in Phase 1 with schema-first generation and a dedicated validator.

## Key Findings

### Recommended Stack

Python 3.11+ with `openai` SDK (Structured Outputs), `pydantic` for models/schema, `python-dotenv` for config, and `pytest` for validator tests. Avoid LangChain, multi-agent frameworks, and microservices for v1.

**Core technologies:**
- **Python 3.11+**: Runtime with modern typing
- **openai + Pydantic `.parse()`**: Guaranteed schema adherence at API level
- **pytest**: Validator tests without live LLM calls

### Expected Features

**Must have (table stakes):**
- Parameterized generation (matéria, tópico, dificuldade, quantidade)
- JSON output with enunciado, resposta, explicação
- Structural validation and clear errors
- API key via environment variable

**Should have (competitive):**
- Bounded retry on validation failure (1–2 attempts)
- Dev logging without secrets
- Difficulty enum in schema

**Defer (v2+):**
- MySQL persistence, performance analytics, personalization, agent loop

### Architecture Approach

Flat pipeline architecture with single responsibility per module. `main.py` orchestrates; `generator.py` owns API calls; `validator.py` is pure and testable; `prompts.py` centralizes templates; `models.py` defines contracts.

**Major components:**
1. **CLI/Entry** — input/output and error handling
2. **Generator** — LLM integration with Structured Outputs
3. **Validator** — structural checks before returning results

### Critical Pitfalls

1. **Markdown-wrapped JSON** — use Structured Outputs, not prompt-only parsing
2. **Wrong exercise count** — validator must enforce `quantidade`
3. **Empty fields** — reject whitespace-only strings
4. **API key leakage** — `.env` only, never log secrets
5. **Infinite retries** — cap at 2 attempts per AGENT.md

## Implications for Roadmap

### Phase 1: MVP Generator Pipeline
**Rationale:** Core value requires end-to-end generation with validation
**Delivers:** Working CLI, modules, validator tests, error handling
**Addresses:** All table-stakes features from FEATURES.md
**Avoids:** JSON fragility, missing validation, key hardcoding

### Phase 2: Reliability & Observability
**Rationale:** Production-safe retry and logging after core works
**Delivers:** Bounded retry, duration logs, argparse CLI
**Uses:** Validator error reasons from PITFALLS.md
**Implements:** Retry pattern from architecture research

### Phase 3: Math Validation (Future milestone)
**Rationale:** Structural validity ≠ mathematical correctness
**Delivers:** Rule-based or symbolic checks on answers

### Phase Ordering Rationale

- Generator before retry (need baseline flow)
- Validator tests in Phase 1 (no LLM dependency)
- MySQL and agent deferred per AGENT.md explicit evolution plan

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 3 (math validation):** sympy vs custom rules for topic-specific checks

Phases with standard patterns (skip research-phase):
- **Phase 1:** Well-documented OpenAI Structured Outputs patterns

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | OpenAI docs + project constraints align |
| Features | HIGH | AGENT.md is detailed |
| Architecture | HIGH | Simple pipeline, proven pattern |
| Pitfalls | HIGH | Common LLM app failure modes |

**Overall confidence:** HIGH

### Gaps to Address

- **Provider choice:** AGENT.md implies OpenAI but doesn't mandate; confirm during Phase 1 planning
- **Math validation depth:** Deferred; research sympy integration when Phase 3 starts

## Sources

### Primary (HIGH confidence)
- OpenAI Structured Outputs cookbook — schema enforcement
- openai-python helpers.md — `.parse()` API
- AGENT.md — project scope and constraints

### Secondary (MEDIUM confidence)
- 2026 Python structured output guides (InfoWok, Team 400)

---
*Research completed: 2026-09-01*
*Ready for roadmap: yes*
