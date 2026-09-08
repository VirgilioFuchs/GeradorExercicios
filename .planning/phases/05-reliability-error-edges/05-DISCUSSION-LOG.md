# Phase 5: Reliability & Error Edges - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-08
**Phase:** 5-Reliability & Error Edges
**Areas discussed:** Limite/contagem, disparo de regeneração, onde vive o loop, prompt no retry, UX, duração, ERR-05/WR-03/WR-04

---

## Limite e contagem de tentativas

| Option | Description | Selected |
|--------|-------------|----------|
| 1 regeneração fixa | Total 2 LLM calls | |
| 2 regenerações fixas | Total 3 LLM calls | |
| Default via env | Configurável | partial → |
| CLI `--max-retries` | Override por execução | partial → |
| Política mista validação/API | | |
| Você decide | | |

**User's choice:** Default via env + alteração via `--max-retries` CLI; depois: hierarquia CLI > env > default `1`; semântica = regenerações; faixa `0|1|2|3`
**Notes:** Amplia teto PROJECT 1–2 para permitir 3 regenerações

---

## O que dispara regeneração

| Option | Description | Selected |
|--------|-------------|----------|
| Só validação estrutural | | |
| Validação + LLM inválida/parse | Sem auth/timeout | clarified vs 5 |
| Qualquer ValueError/RuntimeError | | |
| Só validação; API nunca retry | | |
| Como 2 + hook para math Phase 6 | | ✓ |
| Você decide | | |

**User's choice:** Opção 5 (após esclarecer que 2 ≠ 5: 5 inclui contrato Phase 6)
**Notes:** User disse “prefiro a fase 5” no sentido da opção 5

---

## Onde vive o loop

| Option | Description | Selected |
|--------|-------------|----------|
| Dentro de `main.run` | | |
| `run_with_retry` em main | | |
| Módulo dedicado reliability/retry | | ✓ |
| Dentro de generate_exercises | | |
| Dentro do validator | | |
| Você decide | | |

**User's choice:** 3 — módulo dedicado

---

## Prompt / feedback na regeneração

| Option | Description | Selected |
|--------|-------------|----------|
| Mesmo prompt | | → |
| Prompt + erro validação | | |
| Prompt repair separado | | |
| Erro só na 2ª+ regen | | |
| Nunca alterar prompt nesta fase | | ✓ |
| Você decide | | |

**User's choice:** Deixar estruturação de prompt para próximo milestone se precisar (= mesmo prompt agora; repair deferred)
**Notes:** User asked what YAGNI means mid-thread

---

## UX durante / após retry

| Option | Description | Selected |
|--------|-------------|----------|
| Estágios + Tentativa N/M; erro visível | | |
| Estágios sem contador | | |
| Silencioso no retry | | partial |
| Estágios + erro só ao esgotar | | mix |
| Stdout parcial em falhas | | rejected |
| Você decide | | |

**User's choice:** Mistura 1+3: fluxo Gerando→Validando→`1ª Regeneração`…; erro só ao esgotar; stdout/--out só sucesso
**Notes:** Prefere “1ª Regeneração” contando a partir das regenerações

---

## Formato do log de duração

| Option | Description | Selected |
|--------|-------------|----------|
| Por chamada LLM | | |
| Por tentativa generate+validate | | |
| LLM + label tentativa | | |
| Agregado no fim (total + chamadas) | | ✓ |
| LLM por chamada + total | | |
| Você decide | | |

**User's choice:** 4

---

## ERR-05 / WR-03 / WR-04

| Option | Description | Selected |
|--------|-------------|----------|
| Guard + RuntimeError | | |
| Invalid response retriável | | ✓ (part) |
| Edges só unificam msg; sem retry | | |
| Mapper unificado + testes | | ✓ (part) |
| Mínimo if-not-choices | | |
| Você decide | | |

**User's choice:** Recomendação do agente 2+4

---

## the agent's Discretion

- Nome do módulo (`reliability.py` vs `retry.py`)
- Unidade exata de duração (ms vs s)
- Wording preciso das strings PT além do padrão “Nª Regeneração”

## Deferred Ideas

- Prompt repair / feedback ao modelo no retry — próximo milestone
- Provider failover — fora v1.1
- Math — Phase 6
