---
id: SEED-001
status: dormant
planted: 2026-09-09
planted_during: v1.2 planning (post v1.1)
trigger_when: BNCC, habilidades BNCC, curriculum alignment, codes EF/EM, tagged skills on exercises
scope: milestone
audit_acknowledged:
  milestone: v1.2
  at: 2026-09-15
  status: dormant
---

# SEED-001: Habilidades da BNCC no gerador de exercícios

## Why This Matters

O projeto já gera exercícios por `matéria` / `tópico` / `dificuldade`, mas escolas e professores no Brasil alinham conteúdo às **habilidades da BNCC**. Sem códigos/habilidades no JSON e no prompt, o lab fica desconectado do currículo oficial — pior para uso pedagógico real e para filtrar/gerar “do que a BNCC pede”.

## When to Surface

**Trigger:** when milestone goals mention BNCC, habilidades curriculares, alinhamento curricular, códigos EF*/EM*, or tagging exercises with curriculum skills

Surfaces during `$gsd-new-milestone` when scope matches curriculum / BNCC work.

Also relevant when extending CLI flags, prompt templates, or `Exercise` / batch JSON schema.

## Scope Estimate

**Milestone-sized** (likely a dedicated v1.x slice): catalog or lookup of habilidades, CLI/input for código(s), prompt instructions, optional field(s) on each exercise in structured output, validation that codes look plausible — full BNCC ingest + UI can be phased.

## Breadcrumbs

- Deferred in Phase 4: `.planning/milestones/v1.1-phases/04-cli-argparse/04-CONTEXT.md` (“BNCC — fora do v1.1”)
- CLI params today: `exercise-ai/main.py` (`--materia`, `--topico`, …)
- Prompt injection: `exercise-ai/prompts.py` (`Matéria` / `Tópico`)
- Models / JSON: `exercise-ai/models.py` (exercise fields — no BNCC yet)

## Notes

Captured during `$gsd-new-milestone` after user asked to annotate: want the project to support placing BNCC skills (habilidades) into the generation flow. Candidate focus for **v1.2** — confirm with user before locking requirements.

**Downstream:** SEED-009 (endurecer `math_check` alinhado à BNCC) depends on this seed landing first.
