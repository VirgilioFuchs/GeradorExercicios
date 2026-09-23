---
id: SEED-009
status: dormant
planted: 2026-09-22
planted_during: mid-UAT Phase 14 (v2.1)
trigger_when: math_check, endurecer math, BNCC math rules, curriculum-aligned validation, checker por habilidade, symbolic/math rigor after BNCC
depends_on:

  - SEED-001

priority: medium
scope: phase
audit_acknowledged:
  milestone: v2.1
  at: 2026-09-23
  status: dormant
---

# SEED-009: Endurecer `math_check` alinhado à BNCC

## Why This Matters

O `math_check` atual valida consistência aritmética/básica do lote, mas **não** escala rigor nem tipologias de verificação às **habilidades BNCC** do exercício. Endurecer o checker “no genérico” (mais regras fixas para todo tópico) sem o catálogo/códigos da BNCC arrisca:

1. Rejeitar exercícios válidos fora do perfil da habilidade, ou
2. Aceitar exercícios fracos para o que a BNCC pede naquele código.

A sequência correta: **primeiro SEED-001** (habilidades no request/schema/prompt) → **depois** este seed endurece o `math_check` **por habilidade / família BNCC**, não um monólito cego.

## When to Surface

**Trigger:** only after SEED-001 has landed (or is in active execution) — BNCC codes on request/exercise, prompt alignment, catalog/lookup available enough to key rules.

Surfaces during `$gsd-new-milestone` / `$gsd-plan-phase` when goals mention: math_check rigor, curriculum-aligned validation, checker por habilidade EF*/EM*, or “validar como a BNCC espera”.

**Do not promote** as a standalone math sprint before BNCC tagging exists.

Also relevant when touching `exercise-ai/math_check.py`, `validator.py`, RELY fail paths, or SEED-005 postmortem (richer math fail context).

## What the operator asked for (capture verbatim intent)

1. Nova seed para **endurecer mais o check** (`math_check`).
2. **Depois** de aplicar as BNCC — porque as regras endurecidas devem ser **de acordo com a BNCC**.

## Scope Estimate

**Phase-sized** (after SEED-001 milestone/slice):

| Slice | Intent |
|-------|--------|
| A — Gate de promoção | Checklist: SEED-001 shipped (código(s) BNCC no contrato + prompt) |
| B — Mapa habilidade → regras | Por família/código (ou cluster): o que o checker exige (ex. equação 1º grau vs frações vs geometria) |
| C — Pluggable checks | `math_check` despacha regras tipadas; default = comportamento atual (fail-closed, sem regressão uniforme) |
| D — Offline fixtures | Casos BNCC-tagged: passa / falha / uninterpretable; sem LLM |
| E — Ops | Opcional: postmortem (SEED-005) inclui habilidade + regra que falhou |

**Fora de escopo aqui:** ingest completo da BNCC UI; redesign RELY bounds; persona (SEED-007).

## Ordering (hard constraint)

```
SEED-001 (habilidades BNCC no fluxo)
    ↓
SEED-009 (math_check endurecido por habilidade)
    ↓ (opcional paralelo/depois)
SEED-005 (postmortem mais usável com contexto BNCC+regra)
```

Se alguém pedir “melhorar math_check” sem BNCC: **redirecionar para SEED-001** ou promover ambos no mesmo milestone com 001 antes de 009.

## Breadcrumbs

- Prerequisite seed: `.planning/seeds/SEED-001-habilidades-bncc.md`
- Checker: `exercise-ai/math_check.py`
- Pipeline: `exercise-ai/validator.py` → `check_math_batch`; `reliability.py` RELY + postmortem
- Related: SEED-005 (usable postmortem); SEED-007 (validation vs thinking separation — don’t ask LLM to self-check as substitute)
- Origin: Phase 14 UAT discuss (operator, 2026-09-22)

## Notes

Planted 2026-09-22 mid Phase 14 UAT after operator asked for a math_check hardening seed **sequenced after BNCC**. Keep dormant until SEED-001 is active; do not invent BNCC-blind rule packs that pretend to be curriculum-aligned.
