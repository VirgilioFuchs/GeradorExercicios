---
id: SEED-006
status: dormant
planted: 2026-09-16
planted_during: post-v1.2 (awaiting next milestone)
trigger_when: lote dinâmico, batch, per-exercise, dificuldade por exercício, reasoning por atividade, quantidade alta, mixed difficulty, tipo de raciocínio
priority: high
scope: milestone
audit_acknowledged:
  milestone: v2.0
  at: 2026-09-18
  status: dormant
---

# SEED-006: Lotes dinâmicos — quantidade + dificuldade e raciocínio por exercício

## Why This Matters

Hoje um lote é **uniforme**: um `GenerationRequest` com `dificuldade` e `quantidade` únicas (CLI/wizard cap **40**), e `reasoning_effort` é **global** por run (`LLM_REASONING_EFFORT` / `--reasoning`). Para montar uma prova ou sequência pedagógica, o operador precisa **domínio por atividade**: misturar fácil/médio/difícil no mesmo lote, e definir o **tipo de raciocínio** de cada exercício — além de deixar a IA trabalhar com **mais quantidade** quando o lote cresce. Sem isso, o lab só gera “N cópias do mesmo nível”.

## When to Surface

**Trigger:** when milestone goals mention dynamic batches, per-exercise difficulty, per-item reasoning / tipo de raciocínio, larger quantity limits, mixed-difficulty sets, or “controle fino do lote”

Surfaces during `$gsd-new-milestone` when productizing generation quality beyond one-shot CLI demos (strong fit after or alongside SEED-003 host embed).

Also relevant when extending `GenerationRequest` / `Exercise` schema, prompts, wizard/`gerar`, or validation of batch length + per-item fields.

## What the operator asked for (capture verbatim intent)

1. Deixar a geração de lote **mais dinâmica**.
2. IA poder trabalhar com **mais quantidade**.
3. **Domínio sobre a dificuldade de cada exercício** (não só um nível para o lote inteiro).
4. **Definir o tipo de raciocínio para cada atividade**.

## Scope Estimate

**Milestone-sized** (likely split across phases):

| Slice | Likely content |
|-------|----------------|
| A — Schema | Spec por item: dificuldade (e opcional tipo/raciocínio pedagógico) por exercício; batch plan no request ou lista de specs |
| B — Prompt + validação | Prompt instrui níveis mistos; validator checa quantidade + campos por item |
| C — Reasoning | Esclarecer: reasoning_effort de API (custo/modelo) vs “tipo de raciocínio” pedagógico no enunciado — possivelmente ambos; API effort pode continuar run-level se providers não suportarem por item |
| D — Caps | Revisar `_MAX_QUANTIDADE` (40) / chunking se limites de contexto; custo/`[USAGE]` por chunk |
| E — UX | Wizard/CLI: plano de lote (ex. 2 fáceis + 3 médios) sem forçar N flags manuais |

Depends on current pipeline: `models.py` → `prompts.py` → generators → `validate_exercise_batch` → CLI/`wizard`.

## Breadcrumbs

- Request (uniform today): `exercise-ai/models.py` (`GenerationRequest.dificuldade`, `quantidade`)
- Cap 40: `exercise-ai/main.py` (`_MAX_QUANTIDADE`), `exercise-ai/wizard.py`
- Global reasoning: `exercise-ai/reasoning.py`, `--reasoning` / wizard step
- Prompt constraints: `exercise-ai/prompts.py`
- Related: SEED-003 (host may need rich batch contract); SEED-002 (token cost rises with larger/mixed lots)

## Notes

Planted 2026-09-16 during seed review for next milestone. Operator priority **high** for product control of batches; clarify in discuss-phase whether “tipo de raciocínio” = pedagogical skill taxonomy, API `reasoning_effort`, or both.
