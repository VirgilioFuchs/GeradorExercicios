---
id: SEED-007
status: dormant
planted: 2026-09-21
planted_during: mid v2.1 new-milestone + quick (model lists)
trigger_when: personalidade, persona, regras da IA, system prompt, skill geração, comportamento do modelo, validação vs pensamento vs resposta, configurações da IA, exercise generation contract
priority: high
scope: phase
audit_acknowledged:
  milestone: v2.1
  at: 2026-09-23
  status: dormant
---

# SEED-007: Personalidade, regras e configurações da IA (contrato de geração)

## Why This Matters

Hoje o lab tem:

- engenharia genérica de agentes em `skills/python-ai-engineering/SKILL.md` → `.cursor/rules/10-python.mdc` + `20-ai-engineering.mdc`
- um `SYSTEM_PROMPT` / `USER_PROMPT_TEMPLATE` curtos em `prompts.py` (tom de professor + campos obrigatórios)

Falta um **contrato de domínio** — no mesmo espírito do skill de engenharia, mas **específico para geração de exercícios**: personalidade, regras pedagógicas, funcionalidades do sistema, e como o modelo deve se portar quando o operador/host pede para criar exercícios. Sem isso, prompts e agentes misturam **pensar**, **responder** e **validar**, e o pipeline real (`prompt → LLM → validate → math_check → RELY`) não fica documentado como arquitetura que o modelo (e os agentes GSD) devem respeitar.

## When to Surface

**Trigger:** when milestone/phase/quick goals mention AI persona, generation rules, system prompt hardening, skill for exercise generation, separating validation vs thinking vs response, or “como o modelo deve se comportar ao gerar exercícios”

Surfaces during `$gsd-new-milestone`, `$gsd-discuss-phase` (prompt/schema), or `$gsd-quick` when rewriting prompts / adding agent skills for this repo.

Also relevant when touching `prompts.py`, `validator.py`, `math_check.py`, `reliability.py`, `reasoning.py`, or adding skills under `skills/` / `.cursor/skills/`.

## What the operator asked for (capture verbatim intent)

1. **Seed** (não implementação imediata obrigatória) de **personalidades, regras e configurações da IA**.
2. Formato **tipo** `skills/python-ai-engineering/SKILL.md` — skill/contrato que aponta regras autoritativas — mas **específico** para:
   - regras de **geração de exercícios**
   - **funcionalidades do sistema** (o que o gerador faz / não faz)
   - como o modelo deve se **portar** quando o usuário pede para criar exercícios
3. **Separar** funcionalidades de:
   - **validação** (código determinístico: schema, adesão ao plano, math_check — LLM não é fonte de verdade)
   - **pensamento** (reasoning_effort / planejamento interno da API — run-level; não confundir com tipo pedagógico)
   - **resposta** (enunciado / resposta / explicação estruturados no JSON)
4. **Planejar** como o modelo (e agentes) seguem a **arquitetura correta** do pipeline — não inventar um segundo agente de “validação” dentro do prompt quando o código já valida.

## Scope Estimate

**Phase-sized** (ou `$gsd-quick` grande se só o skill + ponteiros; milestone se incluir rewrite forte de prompts + testes):

| Slice | Likely content |
|-------|----------------|
| A — Skill índice | `skills/exercise-generation/SKILL.md` (ou similar) no padrão do python-ai-engineering: aponta regras autoritativas; GSD aplica em plan/execute/review |
| B — Regras de domínio | Doc/rule (ex. `.cursor/rules/30-exercise-generation.mdc` ou `docs/EXERCISE-AI-CONTRACT.md`): personalidade, tom PT-BR, limites de escopo (tópico/dificuldade), o que nunca fazer (inventar fora do tópico, keys em log, etc.) |
| C — Separação de concerns | Tabela explícita: **Pensamento** (API effort) vs **Resposta** (campos Exercise) vs **Validação** (validator/math/RELY) vs **Config** (provider, model lists, env) |
| D — Alinhamento arquitetural | Diagrama curto do pipeline v2.0+; “quando o usuário pede gerar → host/CLI → service → prompt → LLM → validate → …” — skill manda agentes respeitarem essa ordem |
| E — Prompt wiring | Opcional: `SYSTEM_PROMPT` passa a espelhar o contrato (sem duplicar validação no prompt); testes offline de presença de regras críticas |

**Não é:** LangChain/multi-agent; BNCC (SEED-001); imagens (SEED-003 B); lotes dinâmicos (SEED-006) — pode **referenciar** lotes quando promovidos, mas o seed é o contrato de comportamento.

## Suggested architecture split (for discuss / plan)

```
Configuração (provider, model, reasoning_effort, env)
        ↓
Persona + regras de geração (system/user prompts — domínio)
        ↓
Resposta estruturada (Exercise / ExerciseBatch — enunciado, resposta, explicação)
        ↓
Validação determinística (Pydantic + validator + math_check + RELY)
```

- **Pensamento:** knob de API (`reasoning.py`) — não é campo do exercício.
- **Resposta:** único output do LLM no contrato Structured Outputs.
- **Validação:** código; falha → RELY / erro tipado — não “peça ao modelo para se validar” como substituto.

## Breadcrumbs

- Skill padrão a espelhar: `skills/python-ai-engineering/SKILL.md`
- Rules genéricas AI: `.cursor/rules/20-ai-engineering.mdc`
- Prompts atuais: `exercise-ai/prompts.py` (`SYSTEM_PROMPT`, `USER_PROMPT_TEMPLATE`, `build_prompts`)
- Validação: `exercise-ai/validator.py`, `exercise-ai/math_check.py`, `exercise-ai/reliability.py`
- Reasoning API: `exercise-ai/reasoning.py`
- Service seam: `exercise-ai/service.py` (`generate_batch`)
- Models: `exercise-ai/models.py`
- Related seeds: SEED-006 (lotes — muda prompt/plano); SEED-005 (postmortem); quick pendente de listas de modelos (config)

## Notes

Planted 2026-09-21 during conversation: operator wants a domain skill/contract analogous to python-ai-engineering, focused on exercise-generation persona/rules/config and a clean split validation / thinking / response aligned with the real pipeline. Prefer promote via `$gsd-quick` (skill + rule file) or a small phase after prompt-touching work (e.g. with SEED-006). Do not invent full taxonomy of “personalidades” until discuss locks tone variants (single professor vs multiple personas).
