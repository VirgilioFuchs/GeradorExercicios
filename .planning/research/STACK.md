# Stack Research

**Domain:** Python LLM exercise generation (educational)
**Researched:** 2026-09-01
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.11+ | Runtime | Modern typing, dataclasses, wide LLM SDK support |
| openai | ≥1.50 | LLM API client | Native Structured Outputs via `chat.completions.parse()` with Pydantic |
| pydantic | ≥2.0 | Data models + schema | Single source of truth for models and JSON schema; field validators for semantic checks |
| python-dotenv | ≥1.0 | Config | Load `LLM_API_KEY` from `.env` without hardcoding |
| pytest | ≥8.0 | Testing | Standard for validator unit tests without LLM calls |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| httpx | (via openai) | HTTP | Underlying client; handle timeouts via SDK |
| logging (stdlib) | — | Observability | Dev logs for generation start/end, validation failures |
| typing / dataclasses (stdlib) | — | Types | If Pydantic feels heavy for internal-only structs (prefer Pydantic for LLM boundary) |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| pytest | Unit tests | Mock LLM responses for validator tests |
| ruff (optional) | Lint/format | Add later if team grows; not required for MVP |
| `.env.example` | Onboarding | Document `LLM_API_KEY` without secrets |

## Installation

```bash
pip install openai pydantic python-dotenv
pip install pytest  # dev
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| openai + Structured Outputs | Anthropic Claude with tool_use / JSON | If user already has Anthropic credits; add provider abstraction in v2 |
| pydantic | dataclass + manual JSON schema | Only if zero-deps is mandatory; loses `.parse()` integration |
| openai SDK | instructor library | Cross-provider abstraction; overkill for single-provider MVP |
| CLI stdin/args | FastAPI REST API | When exposing HTTP endpoint (v2+) |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| LangChain / CrewAI / AutoGen | Hides LLM fundamentals; violates project constraints | Plain SDK + small modules |
| RAG / vector DB | No retrieval need for parameterized generation | Direct prompt with topic/difficulty |
| Microservices / queues | Premature for CLI MVP | Single Python package |
| `json.loads` on free-form LLM text only | Fragile; markdown fences and truncation | Structured Outputs + fallback validator |
| GPT-3.5 / models without strict schema | No guaranteed schema adherence | gpt-4o-mini or gpt-4o-2024-08-06+ |

## Stack Patterns by Variant

**If OpenAI is the provider:**
- Use `client.chat.completions.parse(response_format=ExerciseBatch)` with Pydantic models
- Set explicit timeouts and max_retries on the client
- Check `message.refusal` when model declines

**If adding a second provider later:**
- Introduce thin `LLMProvider` protocol; keep prompts and validation provider-agnostic

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| openai ≥1.50 | pydantic ≥2.0 | `.parse()` requires recent SDK |
| Structured Outputs | gpt-4o-2024-08-06, gpt-4o-mini | Pin model string; aliases may not enforce schema |

## Sources

- OpenAI Structured Outputs cookbook — `response_format` with `strict: true`, Pydantic `.parse()`
- openai-python helpers.md — `chat.completions.parse()` behavior and limitations
- InfoWok / Team 400 guides (2026) — production patterns: enums, bounded retry, semantic validators
- AGENT.md (project) — explicit exclusions and MVP scope

---
*Stack research for: Python LLM math exercise generator*
*Researched: 2026-09-01*
