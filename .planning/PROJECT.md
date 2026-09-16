# Gerador de Exercícios com IA

## What This Is

Uma aplicação Python CLI que gera exercícios de matemática via LLM (OpenAI Structured Outputs, Gemini e Grok), recebe parâmetros (matéria, tópico, dificuldade, quantidade) e retorna JSON estruturado com enunciado, resposta e explicação. Laboratório incremental para estudar chamadas a LLM, prompt engineering, structured output, validação, confiabilidade e ops — sem frameworks de agentes.

## Core Value

O usuário consegue gerar exercícios de matemática confiáveis e estruturados a partir de parâmetros simples, com validação que garante formato correto antes de usar o resultado.

## Current State

**Shipped:**
- **v1 MVP** (2026-09-04) — pipeline modular, dual-provider, validação estrutural, pytest, logging sanitizado
- **v1.1 Qualidade do exercício** (2026-09-09) — CLI argparse + dual-output, regeneração limitada (RELY), edges ERR-05, checagem matemática básica
- **v1.2 Ops & Resilience** (2026-09-15) — GitHub Actions CI, failover OpenAI↔Gemini, token usage NDJSON/`[USAGE]`, wizard interativo `gerar`, reasoning default `medium`

**Stack:** Python 3.11+, openai, pydantic v2, python-dotenv, google-genai, pytest. Code under `exercise-ai/`. Suite: 133 tests (no live LLM).

**Known debt (accepted at v1.2 close):** Nyquist VALIDATION gaps (phases 8–10); optional CI-02 GitHub UI reconfirm; wizard E2E integration test optional; exhaustion plural grammar; Grok out of failover by design.

## Current Milestone: v2.0 Embed em Produção

**Goal:** Expor o gerador como biblioteca embutível em outro sistema e demonstrar o fluxo de integração para o time do host (SEED-003 Slice A).

**Target features:**
- `service.py` — fronteira de embed: `GenerationRequest` → `ExerciseBatch`, sem print, sem arquivo, sem `sys.exit`
- `main.run()` como adapter; CLI argparse e wizard `gerar` preservados (regressão zero)
- Contrato de erro utilizável pelo host: `kind` nos `ValueError` de config, `LLM_PROVIDER` restaurado, bound 1–40 no domínio
- Demo local apresentável em `demo/` (`http://[::1]:8642/`, stdlib only, fora do CI) com exercícios + JSON do contrato

**Explicitamente fora:** objeto `Settings` (env segue como config — KISS), `pyproject`/rename (parkado até o stack do host ser conhecido), HTTP/auth, concorrência, imagens e storytelling (Slices B e C).

## Requirements

### Validated (through v1.2)

- ✓ Pipeline LLM + JSON tipado + validação estrutural — v1
- ✓ Dual/triple provider (OpenAI, Gemini, Grok) + API error mapping — v1 / quick
- ✓ pytest offline + LOG-01/02 — v1
- ✓ CLI argparse + `--out` + RELY + math check — v1.1
- ✓ GitHub Actions CI sem secrets — v1.2 / CI-01..02
- ✓ Failover OpenAI↔Gemini — v1.2 / FAILOVER-01..03
- ✓ Token usage observability — v1.2 / TOKEN-01..03
- ✓ Wizard `gerar` + reasoning medium — v1.2 / WIZ-01..03

### Active

- Host embute o gerador chamando uma função de serviço e recebe o lote validado — v2.0
- Falha no gerador não derruba o processo do host, e o tipo de falha é distinguível — v2.0
- CLI e wizard seguem idênticos após a extração do serviço — v2.0
- Demo local mostra o fluxo e o JSON que o host consome — v2.0

### Out of Scope

- LangChain, CrewAI, AutoGen — YAGNI no lab
- RAG, filas, microsserviços — YAGNI
- MySQL / analytics / personalização / agente — v2+ themes
- BNCC — SEED-001 dormant (acknowledged at v1.2 close)
- Imagens / storytelling — SEED-003 Slices B e C, depois do embed
- Lotes dinâmicos (dificuldade/raciocínio por exercício) — SEED-006 dormant
- Packaging (`pyproject` / rename `exercise_ai/`) — parkado até o stack do host ser conhecido

## Context

Pipeline v1.2:

```
CLI (argparse | gerar wizard) → Prompt → LLM (OpenAI|Gemini|Grok)
  → Failover envelope (OpenAI↔Gemini) → Validação + math_check → RELY
  → stdout + --out JSON (+ exercicios-gerados routing)
  → [USAGE] / token-usage NDJSON · [FAILOVER] · fail/erros+postmortem
```

## Constraints

- **Tech stack**: Python, sem frameworks de agentes
- **Simplicidade**: YAGNI — cada arquivo com responsabilidade única
- **Segurança**: API keys em `.env`, nunca no código ou logs
- **Confiabilidade**: LLM não é fonte de verdade; validação + math + bounded RELY
- **Retries**: Máximo 1–2 regenerações; failover no máximo uma troca de provider
- **Testabilidade**: Sem LLM live em pytest / CI

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pipeline simples sem agente | Fundamentos antes de abstrações | ✓ Good — v1 shipped |
| OpenAI Structured Outputs + Pydantic v2 | Schema adherence | ✓ Good |
| Dual/triple provider via LLM_PROVIDER | Flexibilidade de créditos | ✓ Good |
| Math + RELY single loop | No second retry architecture | ✓ Good |
| v1.2 = CI + failover + tokens + wizard | Ops & resilience + UX | ✓ Shipped 2026-09-15 |
| Failover OpenAI↔Gemini only; Grok out | KISS / FAILOVER-01 | ✓ Good |
| Token metrics do not drive failover | Observability ≠ routing | ✓ Good |
| `gerar` coexists with argparse | CI/scripts stay non-interactive | ✓ Good |
| Reasoning default medium | Wizard + flags aligned (D-08) | ✓ Good |

<details>
<summary>Prior milestone notes (v1 → v1.1 → v1.2)</summary>

v1 delivered the MVP pipeline. v1.1 hardened CLI, reliability, and basic math. v1.2 added CI, provider failover, token observability, and the interactive `gerar` wizard.

</details>

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-09-16 — v2.0 Embed em Produção started*
