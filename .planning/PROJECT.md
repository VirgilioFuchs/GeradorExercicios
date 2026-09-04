# Gerador de Exercícios com IA

## What This Is

Uma aplicação Python CLI que gera exercícios de matemática via LLM (OpenAI Structured Outputs e Gemini), recebe parâmetros (matéria, tópico, dificuldade, quantidade) e retorna JSON estruturado com enunciado, resposta e explicação. Laboratório incremental para estudar chamadas a LLM, prompt engineering, structured output, validação semântica, mapeamento de erros de API e testes sem frameworks de agentes.

## Core Value

O usuário consegue gerar exercícios de matemática confiáveis e estruturados a partir de parâmetros simples, com validação que garante formato correto antes de usar o resultado.

## Current State

**Shipped:** v1 MVP (2026-09-04) — 3 phases, 28 requirements, pytest suite (31 tests), dual-provider generation, semantic validation, sanitized logging, root README.

**Stack:** Python 3.11+, openai, pydantic v2, python-dotenv, google-genai, pytest. Code under `exercise-ai/`.

**Known debt:** WR-03/WR-04 edge exception mapping; Nyquist/SECURITY artifacts missing for phases 1–2; no GitHub Actions CI.

## Current Milestone: v1.1 Qualidade do exercício

**Goal:** Melhorar o que já existe — CLI usável, regeneração limitada após falha, e checagem matemática básica das respostas — sem DB, agente ou CI.

**Target features:**
- RELY-01/02 + WR-03/04 — retry 1–2 após falha de validação; log de duração LLM; edges de erro API
- CLI-04 — argparse para matéria, tópico, dificuldade, quantidade
- MATH-01 — validação matemática básica além da estrutural

## Requirements

### Validated

- ✓ Gerar exercícios via LLM com matéria, tópico, dificuldade, quantidade — v1
- ✓ JSON estruturado com enunciado, resposta e explicação — v1
- ✓ Validação estrutural (chave `exercicios`, quantidade, campos) — v1
- ✓ Módulos separados: main, generator(s), prompts, models, validator — v1
- ✓ Erros de API/rede/timeout/rate limit e respostas inválidas tratados — v1
- ✓ API keys via `.env` (nunca hardcoded) — v1
- ✓ Testes unitários do validador sem LLM real — v1
- ✓ Logs de desenvolvimento sem segredos — v1
- ✓ README de setup/execução — v1

### Active

- [ ] Retry automático com limite (RELY-01) e log de duração (RELY-02)
- [ ] Fechar WR-03/WR-04 no mapeamento de erros API
- [ ] CLI argparse (CLI-04)
- [ ] Validação matemática básica de respostas (MATH-01)

### Out of Scope

- LangChain, CrewAI, AutoGen — complexidade desnecessária no lab
- RAG, banco vetorial, filas, microsserviços — YAGNI
- MySQL e persistência — v2+ (DB-01)
- Análise de desempenho do aluno — v2+ (ANLY-01)
- Personalização / agente — v2+ (PERS-01, AGNT-01)
- Phoenix / log files persistentes — deferred
- GitHub Actions CI — deferred (dívida ops; não é foco de v1.1)

## Context

Pipeline linear entregue no MVP:

```
Entrada → Prompt → LLM (OpenAI|Gemini) → JSON tipado → Validação → stdout JSON / stderr logs
```

v1.1 endurece o mesmo pipeline (CLI → generate → validate[+math] → retry limitado). Persistência e agente ficam para milestones posteriores.

## Constraints

- **Tech stack**: Python, sem frameworks de agentes
- **Simplicidade**: YAGNI — cada arquivo com responsabilidade única
- **Segurança**: API keys em `.env`, nunca no código ou logs
- **Confiabilidade**: LLM não é fonte de verdade; validação estrutural (+ math básica em v1.1)
- **Retries**: Máximo 1–2 tentativas de regeneração; sem loop infinito
- **Testabilidade**: Validador (e math checks) testáveis sem dependência de API externa

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pipeline simples sem agente | Fundamentos antes de abstrações | ✓ Good — v1 shipped |
| Módulos exercise-ai/ com campos PT | Separação clara; domínio educacional | ✓ Good |
| OpenAI Structured Outputs + Pydantic v2 | Schema adherence | ✓ Good |
| Dual provider (OpenAI + Gemini) via LLM_PROVIDER | Flexibilidade de créditos | ✓ Good |
| Two-layer stderr ([VALIDAÇÃO]/[API:*]) + plain user errors | Ops detail vs CLI contract | ✓ Good |
| LOG-02: type+status only, never raw str(exc) | Anti-leakage | ✓ Good |
| pytest factories, no live LLM | Durable regression | ✓ Good |
| No GitHub Actions in Phase 3 | D-10; document pytest only | ⚠️ Deferred past v1.1 |
| v1.1 = qualidade incremental (RELY+CLI+MATH), not v2 product jump | User: melhorar o existente | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-09-04 after starting v1.1*
