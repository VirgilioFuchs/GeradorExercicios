# Gerador de Exercícios com IA

## What This Is

Uma aplicação Python CLI que gera exercícios de matemática via LLM (OpenAI Structured Outputs e Gemini), recebe parâmetros (matéria, tópico, dificuldade, quantidade) e retorna JSON estruturado com enunciado, resposta e explicação. Laboratório incremental para estudar chamadas a LLM, prompt engineering, structured output, validação semântica, mapeamento de erros de API e testes sem frameworks de agentes.

## Core Value

O usuário consegue gerar exercícios de matemática confiáveis e estruturados a partir de parâmetros simples, com validação que garante formato correto antes de usar o resultado.

## Current State

**Shipped:**
- **v1 MVP** (2026-09-04) — pipeline modular, dual-provider, validação estrutural, pytest, logging sanitizado
- **v1.1 Qualidade do exercício** (2026-09-09) — CLI argparse + dual-output, regeneração limitada (RELY), edges ERR-05, checagem matemática básica (arithmetic + `ax+b=c`)

**Stack:** Python 3.11+, openai, pydantic v2, python-dotenv, google-genai, pytest. Code under `exercise-ai/`. Suite: 73 tests (no live LLM).

**Known debt:** Nyquist/SECURITY missing for phases 1–2; Phase 6 VALIDATION.md optional; exhaustion plural grammar (`após 1 regenerações:`); no GitHub Actions CI.

## Current Milestone: v1.2 Ops & Resilience

**Goal:** Deixar o lab confiável fora da máquina local — CI automatizado no GitHub e failover de provider quando a API principal falha.

**Target features:**
- CI-01 — GitHub Actions rodando `pytest` (sem LLM live) em push/PR
- FAILOVER-01 — fallback automático OpenAI ↔ Gemini em erros retriáveis/indisponibilidade (sem segundo loop de math/RELY)

**Explicitly out this milestone:** BNCC (SEED-001), MySQL/analytics, polish-only debt batch

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
- ✓ CLI argparse (matéria, tópico, dificuldade, quantidade, `--out`) — v1.1 / CLI-04
- ✓ Regeneração limitada pós-validação + log de duração — v1.1 / RELY-01, RELY-02
- ✓ Edges API unificados (empty choices / Gemini non-APIError) — v1.1 / ERR-05
- ✓ Validação matemática básica + mensagem clara + RELY — v1.1 / MATH-01, MATH-02

### Active

- [ ] CI: GitHub Actions roda pytest sem LLM live em push/PR
- [ ] Failover: fallback automático entre OpenAI e Gemini em falhas retriáveis/indisponibilidade

### Out of Scope

- LangChain, CrewAI, AutoGen — complexidade desnecessária no lab
- RAG, banco vetorial, filas, microsserviços — YAGNI
- MySQL e persistência — v2+ (DB-01)
- Análise de desempenho do aluno — v2+ (ANLY-01)
- Personalização / agente — v2+ (PERS-01, AGNT-01)
- Phoenix / log files persistentes — deferred
- CAS completo — deferred past v1.1
- BNCC / habilidades curriculares — SEED-001 (dormant; not v1.2)

## Context

Pipeline v1.1:

```
CLI argparse → Prompt → LLM (OpenAI|Gemini) → JSON tipado
  → Validação estrutural + math_check → RELY regen (0–N)
  → stdout texto + --out JSON / stderr logs ([VALIDAÇÃO]/[MATH]/[API:*])
```

## Constraints

- **Tech stack**: Python, sem frameworks de agentes
- **Simplicidade**: YAGNI — cada arquivo com responsabilidade única
- **Segurança**: API keys em `.env`, nunca no código ou logs
- **Confiabilidade**: LLM não é fonte de verdade; validação estrutural + math básica
- **Retries**: Máximo 1–2 tentativas de regeneração; sem loop infinito
- **Testabilidade**: Validador e math checks testáveis sem API externa

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pipeline simples sem agente | Fundamentos antes de abstrações | ✓ Good — v1 shipped |
| Módulos exercise-ai/ com campos PT | Separação clara; domínio educacional | ✓ Good |
| OpenAI Structured Outputs + Pydantic v2 | Schema adherence | ✓ Good |
| Dual provider (OpenAI + Gemini) via LLM_PROVIDER | Flexibilidade de créditos | ✓ Good |
| Two-layer stderr ([VALIDAÇÃO]/[API:*]/[MATH]) + plain user errors | Ops detail vs CLI contract | ✓ Good |
| LOG-02: type+status only, never raw str(exc) | Anti-leakage | ✓ Good |
| pytest factories, no live LLM | Durable regression | ✓ Good |
| No GitHub Actions in Phase 3 | D-10; document pytest only | ⚠️ Deferred |
| v1.1 = qualidade incremental (RELY+CLI+MATH) | Melhorar o existente | ✓ Shipped 2026-09-09 |
| Dual output: text stdout + required `--out` JSON | D-14 Phase 4 | ✓ Good |
| Math reuses `generate_validated_batch` only | No second retry loop (D-07) | ✓ Good |
| Uninterpretable math → pass + postmortem record | Avoid false fails (D-02) | ✓ Good |
| Stdlib math heuristics; no CAS | YAGNI (D-09) | ✓ Good |
| v1.2 = CI + provider failover (not BNCC/DB) | User: ops & resilience | — Active |

<details>
<summary>Prior milestone notes (v1 → v1.1 transition)</summary>

v1 delivered the MVP pipeline. v1.1 hardened CLI, reliability, and basic math without jumping to DB/agent/CI.

</details>

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
*Last updated: 2026-09-09 after starting v1.2*
