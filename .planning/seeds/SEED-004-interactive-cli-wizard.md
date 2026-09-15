---
id: SEED-004
status: dormant
planted: 2026-09-15
planted_during: v1.2 post Phase 9 (after reasoning quick plan)
trigger_when: CLI interativo, wizard, perguntas, tip, prompt, sem flags, interactive, TUI, stdin, questionário
priority: high
scope: phase
---

# SEED-004: CLI interativo com perguntas + tips (sem depender de `--flags`)

## Why This Matters

O operador quer **chamar o arquivo** e responder passo a passo (não montar `python main.py --materia ... --out ...`). Cada pergunta mostra uma **tip** embaixo; flags argparse continuam existindo para scripts/CI, mas o caminho humano vira conversa.

## What the operator asked for (verbatim intent)

Fluxo desejado:

1. Chama o arquivo
2. **Tipo de exercício:** (digita) → envia → tip embaixo
3. **Matéria:** → tip
4. **Quantidade:** → tip
5. **Provedor:** → tip
6. **Nome do JSON:** → tip
7. … (demais params do run atual)

“Aparece uma tip em baixo de cada pergunta ao invés de colocar profiles (`--`).”

Ordem implícita do operador: **depois** do modo de raciocínio unificado (quick 260915-d26) e tipicamente **depois** de Phase 8 Failover — ou como Phase 10 UX no fim de v1.2 / início do próximo milestone (a decidir).

## Scope Estimate

**Phase-sized** (1–2 plans):

| Slice | Content |
|-------|---------|
| A — Wizard | Modo interativo quando argv mínimo / flag `--interactive` / zero args; prompts PT com tip sob cada campo |
| B — Mapping | Mapear respostas → `GenerationRequest` + `--out` nome JSON + provider + reasoning (se já existir) |
| C — Coexist | Manter argparse para automação; wizard não quebra CI/`pytest` |

## Breadcrumbs

- `exercise-ai/main.py` — argparse surface hoje
- Phase 4 CLI dual-output (`--out` JSON)
- Quick reasoning (`--reasoning`) when shipped — wizard should ask effort too if present

## Explicitly out (until discuss)

- GUI / web form
- Profiles salvos em arquivo (operator rejected “profiles (--)” as the primary UX)
- Replacing argparse entirely
