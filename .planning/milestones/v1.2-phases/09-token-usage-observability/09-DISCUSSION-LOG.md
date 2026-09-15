# Phase 9: Token Usage Observability - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-11
**Phase:** 9-Token Usage Observability
**Areas discussed:** JSON layout, flush timing, folder path, stderr fields, missing usage, provider separation, attempt/error/success, tokens+USD; plus researched extras (schema, rates, gitignore, timezone)

---

## 1. Layout dos JSON

| Option | Description | Selected |
|--------|-------------|----------|
| Um JSON por run | Arquivo único sobrescrito/rotacionado por invocação | |
| NDJSON append global | Um arquivo contínuo sem partição | |
| NDJSON append por dia | Append + pasta/arquivo do dia | ✓ |

**User's choice:** NDJSON append separado por dia  
**Notes:** Confirmado com pasta diária sob `token-usage/`

---

## 2. Quando gravar

| Option | Description | Selected |
|--------|-------------|----------|
| A cada request | Flush contínuo | |
| Final da run | Acúmulo em memória + flush no fim | ✓ |

**User's choice:** Final da run

---

## 3. Pasta/módulo

| Option | Description | Selected |
|--------|-------------|----------|
| `exercise-ai/token_usage/` só código | — | |
| `exercise-ai/token-usage/{datas}` dados | Path pedido | ✓ |

**User's choice:** `exercise-ai/token-usage/{separação de datas}`  
**Notes:** Agent locked código em `token_usage/` (underscore) vs dados `token-usage/` (hífen)

---

## 4. Stderr

| Option | Description | Selected |
|--------|-------------|----------|
| Só totais | — | |
| Entrada/saída + consumo + tempo + preço | Pedido completo | ✓ |

**User's choice:** entrada/saída, consumo final, tempo de execução e preço  
**Notes:** Agent locked: tokens only (não texto); tag `[USAGE]`

---

## 5. Usage ausente

| Option | Description | Selected |
|--------|-------------|----------|
| Omitir evento | — | |
| Zeros | — | |
| `indisponível` | Literal PT | ✓ |

**User's choice:** coloca indisponível até o momento

---

## 6. Providers

| Option | Description | Selected |
|--------|-------------|----------|
| Um NDJSON misturado | — | |
| Separar providers | Arquivos/partições distintos | ✓ |

**User's choice:** separa os providers  
**Notes:** Agent locked: `openai.ndjson` / `gemini.ndjson` / `grok.ndjson` sob o dia

---

## 7. Tentativas / erros / sucessos

| Option | Description | Selected |
|--------|-------------|----------|
| Só sucesso final | — | |
| Tentativas + erros + sucessos | — | ✓ |

**User's choice:** registrar as tentativas, erros e sucessos

---

## 8. Tokens e USD

| Option | Description | Selected |
|--------|-------------|----------|
| Só tokens | — | |
| Tokens + USD | — | ✓ |

**User's choice:** tokens e USD  
**Notes:** Research: Grok `cost_in_usd_ticks`; OpenAI/Gemini rate table local; missing → `indisponível`

---

## the agent's Discretion

- Schema NDJSON + `run_id`, `usd_source`
- Local calendar date for folders
- `.gitignore` for generated NDJSON
- Approximate rate table with documented updates (no live scrape)
- Preserve existing `total_ms`/`chamadas` aggregate; add USAGE lines

## Deferred Ideas

- Admin billing APIs, FX/BRL, pricing scrape, Phoenix, SEED-003
