<!-- GSD:project-start source:PROJECT.md -->

## Project

**Gerador de Exercícios com IA**

Uma aplicação Python simples que gera exercícios de matemática via LLM, recebendo parâmetros (matéria, tópico, dificuldade, quantidade) e retornando JSON estruturado com enunciado, resposta e explicação para cada exercício. O projeto é um laboratório incremental para estudar chamadas a LLM, prompt engineering, structured output, validação e confiabilidade — sem frameworks de agentes na primeira versão.

**Core Value:** O usuário consegue gerar exercícios de matemática confiáveis e estruturados a partir de parâmetros simples, com validação que garante formato correto antes de usar o resultado.

### Constraints

- **Tech stack**: Python, sem frameworks de agentes no MVP
- **Simplicidade**: YAGNI — cada arquivo com responsabilidade única
- **Segurança**: API keys em `.env`, nunca no código ou logs
- **Confiabilidade**: LLM não é fonte de verdade; validação estrutural obrigatória
- **Retries**: Máximo 1–2 tentativas de regeneração; sem loop infinito
- **Testabilidade**: Validador testável sem dependência de API externa

<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->

## Technology Stack

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

- Use `client.chat.completions.parse(response_format=ExerciseBatch)` with Pydantic models
- Set explicit timeouts and max_retries on the client
- Check `message.refusal` when model declines
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

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `$gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `$gsd-debug` for investigation and bug fixing
- `$gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `$gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
