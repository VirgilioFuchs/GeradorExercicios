---
id: SEED-005
status: dormant
planted: 2026-09-16
planted_during: post-v1.2 (awaiting next milestone)
trigger_when: postmortem, math_postmortem, diagnóstico de falha, fail/postmortem, usable failure report, melhorar postmortem
priority: medium
scope: phase
---

# SEED-005: Postmortem mais utilizável

## Why This Matters

Hoje, na falha final (math/validação após RELY), o lab grava `math_postmortem.jsonl` sob `exercicios-gerados/fail/postmortem/`. O arquivo existe e é testável, mas **não é fácil de usar**: pouco contexto da run (request, attempts, provider), formato pouco legível para o operador, e fraca ponte com stderr/`[MATH]`/`[USAGE]`. Sem um postmortem acionável, debugar falhas de lote vira adivinhar a partir de logs soltos.

**Não é o foco do próximo produto** — capturar agora para não perder o intent.

## When to Surface

**Trigger:** when milestone/phase goals mention postmortem UX, failure diagnostics, `math_postmortem`, fail/postmortem readability, or “entender por que a geração falhou”

Surfaces during `$gsd-new-milestone` or `$gsd-quick` when ops/debug quality is in scope (can ride after host-embed or as a small reliability polish phase).

Also relevant when touching `reliability.py`, `math_check.py`, or fail-path routing under `exercicios-gerados/`.

## What the operator asked for (capture verbatim intent)

1. **Melhorar o postmortem** para ficar **mais utilizável** (não só gravar jsonl mínimo).
2. **Não priorizar agora** — seed / backlog consciente, não fase imediata.

## Scope Estimate

**Phase-sized** (or large `$gsd-quick`):

- Enriquecer records: request snapshot (matéria/tópico/dificuldade/quantidade), attempt count, provider, error kinds, exercise index — **sem secrets**
- Formato mais legível (JSON indentado por run, ou sumário PT no stderr apontando o arquivo)
- Opcional: um arquivo por falha com timestamp vs append único acumulativo
- Manter contrato LOG-02 (nunca API keys / payloads sensíveis)
- Testes offline cobrindo shape + “só no fail final”

## Breadcrumbs

- Writer: `exercise-ai/reliability.py` (`_write_postmortem`, final-fail path)
- Records: `exercise-ai/math_check.py` (`drain_inconsistency_records`, uninterpretable buffers)
- Path: `exercise-ai/output_paths.py` (`DEFAULT_POSTMORTEM_PATH` → `fail/postmortem/math_postmortem.jsonl`)
- Docs: `exercise-ai/exercicios-gerados/README.md`
- Tests: `exercise-ai/tests/test_reliability.py` (`test_math_exhaustion_prefix_and_postmortem`, …)
- Origin: Phase 6 math quality (v1.1) — postmortem only on final fail (D-08)

## Notes

Planted 2026-09-16 during new-milestone seed review. Operator: useful later, **not current focus**. Prefer promote via `$gsd-new-milestone` or `$gsd-quick` when debugging friction bites.
