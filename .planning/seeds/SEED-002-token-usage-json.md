---
id: SEED-002
status: dormant
planted: 2026-09-11
planted_during: v1.2 Phase 7 (research / resume)
trigger_when: token usage, consumo de tokens, cost logging, usage metrics, observability, quantificar tokens, billing, prompt tokens, completion tokens
scope: phase
---

# SEED-002: Consumo quantitativo de tokens (log acumulativo + JSON)

## Why This Matters

Hoje o lab gera exercícios via LLM mas **não quantifica custo/uso**. Sem tokens por requisição (e histórico acumulado), não dá para estudar prompt engineering com métricas reais, comparar OpenAI vs Gemini, nem ver o impacto de RELY/regenerações. O operador pediu explicitamente algo **quantitativo**, não só logs qualitativos.

## When to Surface

**Trigger:** when milestone/phase goals mention tokens, usage metrics, cost, observability beyond stderr tags, or “quantificar consumo LLM”

Surfaces during `$gsd-new-milestone` or when discussing logging/observability after CI + failover (v1.2 Phases 7–8).

Also relevant when touching generators (`generator.py` / `generator_gemini.py`), reliability regen loops, or stderr logging.

## What the operator asked for (capture verbatim intent)

1. **Quantitativo** — consumo de tokens por requisição (prompt / completion / total, conforme o provider expuser).
2. **Log por requisição** — cada chamada aparece no log; **não substituir** as anteriores (append / acumulação).
3. **Persistência** — ao final (ou de forma contínua), gravar tudo em arquivos **`.json`**.
4. **Pasta separada** — mini-módulo/função em diretório próprio (não misturar no core do pipeline sem isolamento).

## Scope Estimate

**Phase-sized** (small vertical slice after v1.2 ops, or early v1.3 observability):

- Novo pacote/pasta dedicada (ex. `exercise-ai/token_usage/` ou similar — nome a decidir na discuss)
- Extrair `usage` das respostas OpenAI / Gemini (Structured Outputs / generate)
- Append em memória + flush JSON (um arquivo por run e/ou log acumulativo)
- Stderr: linha por request **sem apagar** histórico (não “último só”)
- Sem secrets nos JSON; provider/model ids ok; nunca API keys
- Testes com mocks de `usage` — sem LLM live

## Breadcrumbs

- Deferred related: PROJECT “Phoenix / log files persistentes”
- Generators: `exercise-ai/generator.py`, `exercise-ai/generator_gemini.py` (API response objects)
- Reliability regen: `exercise-ai/reliability.py` (`generate_validated_batch` — multiple calls)
- Logging today: stderr tags `[API:*]` duration — no token fields yet
- Engineering rules: `.cursor/rules/20-ai-engineering.mdc` (cost controls / logging)

## Notes

Captured mid Phase 7 research session: user said “depois me lembre” — **important addition**, not for Phase 7 CI. Do not mix into CI or failover plans unless operator promotes this seed into the active milestone.
