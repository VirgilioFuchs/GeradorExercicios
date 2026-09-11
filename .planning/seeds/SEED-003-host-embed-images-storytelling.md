---
id: SEED-003
status: dormant
planted: 2026-09-11
planted_during: v1.2 Phase 7 (post plan-phase)
trigger_when: integração produção, embed, embed system, production integration, imagens geradas, image generation, storytelling, narrativa, exercícios com história, white-label, host app
priority: critical
scope: milestone
---

# SEED-003: Embed em sistema em produção + imagens + storytelling

## Why This Matters

O lab (Gerador de Exercícios) não é o produto final sozinho: o operador precisa **implementar este pequeno sistema dentro de outro já em produção** para criação de exercícios. Sem esse caminho de integração, o valor fica preso ao CLI local. Depois, o produto precisa crescer em **mídia (imagens geradas)** e em **pedagogia (exercícios com storytelling)** — camadas que mudam schema, prompts, validação e UX do host.

**Prioridade:** extremamente importante (operator flag).

## When to Surface

**Trigger:** when milestone goals mention production embedding/integration, host app, generated images/illustrations for exercises, storytelling/narrative exercise generation, or “levar o gerador para produção”

Surfaces during `$gsd-new-milestone` after v1.2 (CI + failover) or when discussing productization / host integration.

Also relevant when extending `Exercise` JSON schema, CLI/API surface, prompts, or output formats beyond plain text/JSON.

## What the operator asked for (capture verbatim intent)

1. **Integração em produção (crítico):** implementar este pequeno sistema **dentro de outro sistema já em produção** dedicado à criação de exercícios (embed / library / API — forma a decidir na discuss).
2. **Mais à frente — imagens:** implementar as **imagens que vão ser geradas** (artefatos visuais ligados aos exercícios).
3. **Depois — storytelling:** desenvolver uma maneira da **IA criar exercícios com storytelling** (narrativa pedagógica, não só enunciado seco).

Ordem implícita do operador: **integração host → imagens → storytelling**.

## Scope Estimate

**Milestone-sized** (likely split across phases / sub-milestones):

| Slice | Likely content |
|-------|----------------|
| A — Host integration | API/SDK ou módulo embutível; contrato de I/O estável; auth/config do host; sem depender só do CLI |
| B — Generated images | Campos/URLs de imagem no JSON; pipeline de geração; storage; validação; sem secrets em logs |
| C — Storytelling exercises | Prompt patterns + schema (contexto narrativo / história); validação; possível flag CLI/`GenerationRequest` |

Depends on v1.2 ops (CI, failover) for production confidence before deep host embed.

## Breadcrumbs

- Current surface: `exercise-ai/main.py` CLI + JSON `--out`
- Models: `exercise-ai/models.py` (`Exercise` / `ExerciseBatch` — text fields only today)
- Prompts: `exercise-ai/prompts.py`
- Related dormant: SEED-001 BNCC (curriculum), SEED-002 token usage (observability)
- PROJECT deferred: MySQL / analytics / personalização / agente (v2+)

## Notes

Captured after Phase 7 plan verified. **Do not mix into Phase 7 CI or Phase 8 failover** unless operator promotes this seed into the active milestone. Prefer promoting via `$gsd-new-milestone` with clear phase order: integration → images → storytelling.
