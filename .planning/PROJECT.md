# Gerador de Exercícios com IA

## What This Is

Uma aplicação Python CLI e biblioteca embutível que gera exercícios de matemática via LLM (OpenAI Structured Outputs, Gemini e Grok), com lotes uniformes ou mistos por dificuldade. Retorna JSON tipado (enunciado, resposta, explicação + ecos de dificuldade). Laboratório incremental para LLM, structured output, validação, confiabilidade, ops e embed in-process — sem frameworks de agentes.

## Core Value

O usuário consegue gerar exercícios de matemática confiáveis e estruturados a partir de parâmetros simples (incluindo plano misto por faixa), com validação e adesão ao plano antes de usar o resultado — também via `service.generate_batch` para um host embutir o gerador.

## Current State

**Shipped:**
- **v1 MVP** (2026-09-04) — pipeline modular, dual-provider, validação estrutural, pytest, logging sanitizado
- **v1.1 Qualidade do exercício** (2026-09-09) — CLI argparse + dual-output, RELY, edges ERR-05, math check básico
- **v1.2 Ops & Resilience** (2026-09-15) — CI, failover OpenAI↔Gemini, token usage, wizard `gerar`, reasoning `medium`
- **v2.0 Embed em Produção** (2026-09-18) — `service.generate_batch`, erros discrimináveis, demo local throwaway
- **v2.1 Lotes dinâmicos** (2026-09-23) — `plano`/`itens` tipados, slot prompts + `verify_plan_echo`, demo bands, CLI `--plano` + wizard bands

**Next:** define via `$gsd-new-milestone` (candidates: PKG-01 packaging, SEED-007 persona contract, CAP-02, TIPO-OPEN, BNCC/SEED-001→009)

**Stack:** Python 3.11+, openai, pydantic v2, python-dotenv, google-genai, pytest. Code under `exercise-ai/`. Suite: **198** package tests (no live LLM) + demo offline tests.

**Known debt:** PKG-01; OBS-01; LOG-01; Nyquist gaps; dormant seeds SEED-001/003/005/007/008/009.

## Requirements

### Validated (through v2.1)

- ✓ Pipeline LLM + JSON tipado + validação estrutural — v1
- ✓ Dual/triple provider (OpenAI, Gemini, Grok) + API error mapping — v1 / quick
- ✓ pytest offline + LOG-01/02 — v1
- ✓ CLI argparse + `--out` + RELY + math check — v1.1
- ✓ GitHub Actions CI sem secrets — v1.2
- ✓ Failover OpenAI↔Gemini — v1.2
- ✓ Token usage observability — v1.2
- ✓ Wizard `gerar` + reasoning medium — v1.2
- ✓ Embed `generate_batch` + erros `kind` + env restore + README contrato — v2.0
- ✓ Demo local stdlib com guards — v2.0
- ✓ Plano misto tipado (BATCH-01..04) + CAP-01 (=40) — v2.1
- ✓ Slot prompts + plan-echo RELY + demo bands (PROMPT/VAL/DEMO-01) — v2.1
- ✓ CLI `--plano` + wizard band UX (UX-01..02) — v2.1

### Active

_(Empty — define in `$gsd-new-milestone`)_

### Out of Scope

- LangChain, CrewAI, AutoGen — YAGNI no lab
- RAG, filas, microsserviços — YAGNI
- MySQL / analytics / personalização / agente — v2+ themes
- Packaging `pyproject.toml` + rename — PKG-01 (parked)
- Usage/cost no retorno do lote — OBS-01 (parked)
- print→logging — LOG-01 (parked)
- BNCC — SEED-001 dormant (SEED-009 waits on it)
- Imagens / storytelling — SEED-003 B/C
- Overhaul math_check genérico antes da BNCC
- HTTP produto / FastAPI / Flask / Streamlit — demo throwaway stdlib
- Concorrência / async / thread pool — contrato sequencial

## Context

```
Host/demo/CLI/wizard → GenerationRequest (uniforme | plano | itens)
  → service.generate_batch
  → Prompt (slot list) → LLM (OpenAI|Gemini|Grok)
  → Failover → Validação + math_check → verify_plan_echo → RELY
  → ExerciseBatch | ConfigError | InvalidRequestError | GenerationFailedError
```

Mixed (2+ bands) → `plano`; uniform (1 band) → legado `dificuldade`+`quantidade`. Cap quantidade **40**.

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
| Pipeline simples sem agente | Fundamentos antes de abstrações | ✓ Good — v1 |
| OpenAI Structured Outputs + Pydantic v2 | Schema adherence | ✓ Good |
| Dual/triple provider via LLM_PROVIDER | Flexibilidade de créditos | ✓ Good |
| Math + RELY single loop | No second retry architecture | ✓ Good |
| Failover OpenAI↔Gemini only; Grok out | KISS | ✓ Good |
| Keep `generate_batch(...) -> ExerciseBatch` | Do not widen return in v2.0 | ✓ Good |
| Packaging PKG-01 parked | Real embed install later | — Pending |
| Print→logging deferred | Known debt LOG-01 | — Pending |
| v2.1 = SEED-006 lotes dinâmicos only | Product focus | ✓ Shipped 2026-09-23 |
| `verify_plan_echo` after validate in RELY | Keep math_check ownership | ✓ Good |
| `batch.dificuldades` = unique band summary (1–3) | G-14-4 | ✓ Good |
| Shared `plan_ux` for demo/CLI/wizard payload rules | One contract, three surfaces | ✓ Good |
| SEED-009 after SEED-001 | Harden math_check by BNCC skill | — Dormant |
| SEED-007/008/009 ack’d at v2.1 close | Promote to next milestone | — Deferred |

<details>
<summary>Prior milestone notes (v1 → v2.0)</summary>

v1 MVP pipeline. v1.1 CLI/RELY/math. v1.2 CI/failover/tokens/wizard. v2.0 embed seam + throwaway demo.

</details>

## Evolution

This document evolves at phase transitions and milestone boundaries.

---
*Last updated: 2026-09-23 after v2.1 milestone*
