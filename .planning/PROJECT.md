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

**Current Milestone: v2.1 Lotes dinâmicos** (in progress)

**Shipped in milestone so far:**
- Phase 13 — `GenerationRequest` plano misto / uniforme tipado, cap 40
- Phase 14 — prompt slot list + `verify_plan_echo` (RELY) + demo band counts / `plano` POST; UAT 4/4

**Next:** Phase 15 — CLI / wizard batch-plan UX

**Stack:** Python 3.11+, openai, pydantic v2, python-dotenv, google-genai, pytest. Code under `exercise-ai/`. Suite: ~179 package tests + ~23 demo tests (no live LLM).

**Known debt (parked):** PKG-01 packaging/rename; OBS-01 usage alongside batch; LOG-01 print→logging; Nyquist VALIDATION draft/gaps; dormant seeds SEED-001/003/005/007/008/009 (009 depends on 001).

## Current Milestone: v2.1 Lotes dinâmicos

**Goal:** O operador monta um lote com controle por exercício (dificuldade e tipo de raciocínio), em vez de N cópias do mesmo nível.

**Target features:**
- Spec por item: dificuldade (e tipo de raciocínio) por exercício no request — ✓ Phase 13
- Prompt + validação do lote misto (quantidade e campos por item) + demo bands — ✓ Phase 14
- Revisar cap de quantidade (hoje 40) se fizer sentido para lotes maiores — CAP-02 deferred
- UX CLI/wizard: plano de lote (ex. 2 fáceis + 3 médios) sem N flags manuais — Phase 15
- Esclarecer na discuss: “tipo de raciocínio” pedagógico vs `reasoning_effort` da API — TIPO-OPEN

**Promoted seed:** SEED-006

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
- ✓ Plano misto tipado no request (BATCH-*) — Phase 13
- ✓ Prompt slots + plan-echo RELY + demo band/`plano` (PROMPT/VAL/DEMO-01) — Phase 14

### Active

- UX CLI/wizard compacto para plano de lote — Phase 15 / UX-01..02
- Lotes dinâmicos restante (tipo de raciocínio pedagógico) — TIPO-OPEN / SEED-006 remnant

### Out of Scope

- LangChain, CrewAI, AutoGen — YAGNI no lab
- RAG, filas, microsserviços — YAGNI
- MySQL / analytics / personalização / agente — v2+ themes
- Packaging `pyproject.toml` + rename — PKG-01 (parked; pós-v2.1)
- Usage/cost no retorno do lote — OBS-01 (parked)
- print→logging — LOG-01 (parked)
- BNCC — SEED-001 dormant (SEED-009 math_check hardening waits on it)
- Imagens / storytelling — SEED-003 Slices B e C
- Overhaul de validação matemática/semântica além do necessário para lotes mistos (generic harden before BNCC)
- HTTP produto / FastAPI / Flask / Streamlit — demo foi throwaway stdlib
- Concorrência / async / thread pool — contrato sequencial

## Context

Pipeline v2.1 (Phases 13–14):

```
Host/demo → service.generate_batch(GenerationRequest [plano|uniforme])
  → Prompt (slot list) → LLM (OpenAI|Gemini|Grok)
  → Failover envelope → Validação + math_check → verify_plan_echo → RELY
  → ExerciseBatch | ConfigError | InvalidRequestError | GenerationFailedError
Demo bands → buildGerarPayload (mixed→plano / uniform→legacy)
CLI (argparse | gerar wizard) → main.run → generate_batch  # Phase 15: compact plano UX
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
| Packaging PKG-01 parked | Real embed install later; v2.1 = product batches | — Pending |
| Print→logging deferred; host `redirect_stderr` | Known debt LOG-01 | — Pending |
| v2.1 = SEED-006 lotes dinâmicos only | Product focus; PKG/OBS/LOG/imagens/BNCC deferred | — Active |
| Demo = ThreadingHTTPServer + Lock→409, `[::1]:8642`, stdlib | Throwaway accept of embed contract | ✓ Good |
| Error classes in service.py; leaf lazy-import | Avoid cycles | ✓ Good |
| Gemini HttpOptions.timeout=30000 ms | Align magnitude to OpenAI 30s | ✓ Good |
| `verify_plan_echo` after validate in RELY (not validator.py) | D-05; keep math_check ownership | ✓ Phase 14 |
| `batch.dificuldades` = unique band summary (1–3), not per-exercise pad | G-14-4; canonical compare + schema/prompt | ✓ Phase 14 |
| SEED-009 after SEED-001 | Harden math_check by BNCC skill, not generic | — Dormant |

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
*Last updated: 2026-09-22 after Phase 14*
