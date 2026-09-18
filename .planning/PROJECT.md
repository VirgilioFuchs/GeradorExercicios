# Gerador de Exercícios com IA

## What This Is

Uma aplicação Python CLI e biblioteca embutível que gera exercícios de matemática via LLM (OpenAI Structured Outputs, Gemini e Grok), recebe parâmetros (matéria, tópico, dificuldade, quantidade) e retorna JSON estruturado com enunciado, resposta e explicação. Laboratório incremental para estudar chamadas a LLM, prompt engineering, structured output, validação, confiabilidade, ops e embed in-process — sem frameworks de agentes.

## Core Value

O usuário consegue gerar exercícios de matemática confiáveis e estruturados a partir de parâmetros simples, com validação que garante formato correto antes de usar o resultado — agora também via `service.generate_batch` para um host embutir o gerador.

## Current State

**Shipped:**
- **v1 MVP** (2026-09-04) — pipeline modular, dual-provider, validação estrutural, pytest, logging sanitizado
- **v1.1 Qualidade do exercício** (2026-09-09) — CLI argparse + dual-output, regeneração limitada (RELY), edges ERR-05, checagem matemática básica
- **v1.2 Ops & Resilience** (2026-09-15) — GitHub Actions CI, failover OpenAI↔Gemini, token usage NDJSON/`[USAGE]`, wizard interativo `gerar`, reasoning default `medium`
- **v2.0 Embed em Produção** (2026-09-18) — `service.generate_batch` → `ExerciseBatch`, erros discrimináveis (`kind`/subclasses), env restore, encoding/timeout, demo local throwaway `demo/` em `[::1]:8642`

**Stack:** Python 3.11+, openai, pydantic v2, python-dotenv, google-genai, pytest. Code under `exercise-ai/`. Suite: 155 package tests + 17 demo tests (no live LLM).

**Known debt (accepted at v2.0 close):** PKG-01 packaging/rename (lead of next milestone); OBS-01 usage alongside batch; LOG-01 print→logging; Nyquist VALIDATION draft/gaps (phases 8–12); dormant seeds SEED-001/005/006; SEED-003 B/C.

## Next Milestone Goals

**Lead:** **PKG-01** — Packaging `pyproject.toml` + rename `exercise_ai/` (pré-condição do embed in-process real).

Other candidates: OBS-01 (usage/cost with batch), LOG-01 (print→logging), SEED-003 B/C (imagens/storytelling).

## Requirements

### Validated (through v2.0)

- ✓ Pipeline LLM + JSON tipado + validação estrutural — v1
- ✓ Dual/triple provider (OpenAI, Gemini, Grok) + API error mapping — v1 / quick
- ✓ pytest offline + LOG-01/02 — v1
- ✓ CLI argparse + `--out` + RELY + math check — v1.1
- ✓ GitHub Actions CI sem secrets — v1.2 / CI-01..02
- ✓ Failover OpenAI↔Gemini — v1.2 / FAILOVER-01..03
- ✓ Token usage observability — v1.2 / TOKEN-01..03
- ✓ Wizard `gerar` + reasoning medium — v1.2 / WIZ-01..03
- ✓ Host chama `generate_batch` e recebe `ExerciseBatch` (sem print/arquivo/`sys.exit`) — v2.0 / EMBED-01
- ✓ Erros discrimináveis por `kind`/subclasses — v2.0 / EMBED-02
- ✓ CLI + wizard idênticos pós-extração; bound 1–40 — v2.0 / EMBED-03
- ✓ `LLM_PROVIDER` (e overrides) restaurados após chamada — v2.0 / EMBED-04
- ✓ Gemini timeout HTTP finito documentado — v2.0 / EMBED-05
- ✓ Diagnósticos/CLI cp1252-safe (`√`/`→`) — v2.0 / EMBED-06
- ✓ README contrato JSON + erros + nomes reservados — v2.0 / EMBED-07
- ✓ Demo local stdlib `[::1]:8642` (form, tabs, Gerando…, erros) — v2.0 / DEMO-01
- ✓ Demo guards (loopback, Lock→409, Host/Origin/JSON) + anti-accretion — v2.0 / DEMO-02

### Active

- Packaging `pyproject.toml` + rename `exercise_ai/` — próximo milestone / PKG-01
- Usage/cost/`run_id`/provider efetivo junto com o lote — OBS-01 (não alargar `-> ExerciseBatch` em v2.0)
- Conversão print→logging (~33 sites) — LOG-01

### Out of Scope

- LangChain, CrewAI, AutoGen — YAGNI no lab
- RAG, filas, microsserviços — YAGNI
- MySQL / analytics / personalização / agente — v2+ themes
- BNCC — SEED-001 dormant
- Imagens / storytelling — SEED-003 Slices B e C
- Lotes dinâmicos — SEED-006 dormant
- HTTP produto / FastAPI / Flask / Streamlit — demo foi throwaway stdlib
- Concorrência / async / thread pool — contrato sequencial

## Context

Pipeline v2.0:

```
Host/demo → service.generate_batch(GenerationRequest)
  → Prompt → LLM (OpenAI|Gemini|Grok)
  → Failover envelope (OpenAI↔Gemini) → Validação + math_check → RELY
  → ExerciseBatch | ConfigError | InvalidRequestError | GenerationFailedError
CLI (argparse | gerar wizard) → main.run → generate_batch (+ stdout/--out / flush)
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
| Keep `generate_batch(...) -> ExerciseBatch` | Do not widen return in v2.0 | ✓ Good |
| Packaging PKG-01 parked | Lead of next milestone | — Pending |
| Print→logging deferred; host `redirect_stderr` | Known debt LOG-01 | — Pending |
| Demo = ThreadingHTTPServer + Lock→409, `[::1]:8642`, stdlib | Throwaway accept of embed contract | ✓ Good |
| Error classes in service.py; leaf lazy-import | Avoid cycles | ✓ Good |
| Gemini HttpOptions.timeout=30000 ms | Align magnitude to OpenAI 30s | ✓ Good |

<details>
<summary>Prior milestone notes (v1 → v1.1 → v1.2 → v2.0)</summary>

v1 delivered the MVP pipeline. v1.1 hardened CLI, reliability, and basic math. v1.2 added CI, provider failover, token observability, and the interactive `gerar` wizard. v2.0 extracted the embed seam and shipped a local throwaway demo.

</details>

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-09-18 after v2.0 milestone*
