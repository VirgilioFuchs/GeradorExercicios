# Phase 16: Domain skill index - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-23
**Phase:** 16-Domain skill index
**Areas discussed:** alvo API vs agente, caminho/nome, espessura, rules vs persona, API pública, idioma, lista nunca faça

---

## Alvo: API vs pastas de agente

| Option | Description | Selected |
|--------|-------------|----------|
| Skill Cursor / `.cursor` | Índice estilo python-ai-engineering para agentes GSD | |
| Skill da API em `exercise-ai/` | Persona/regras para geração runtime | ✓ |

**User's choice:** Implementar regra/skill da API; não trabalhar pastas de agentes (`.cursor`, `.claude`, `.codex`, …).
**Notes:** Redirecionou CONTRACT-01 de “skill de agente” para “módulo de skill da API”.

---

## Caminho e estrutura

| Option | Description | Selected |
|--------|-------------|----------|
| `skills/__init__.py` + `generation.py` | Pacote flat | |
| `skills/generation/` com `persona.py` + `rules.py` | Subpacote separado | ✓ |
| Um único arquivo | `generation_skill.py` | |

**User's choice:** `exercise-ai/skills/generation/` com persona + rules.

---

## Espessura (fase 16)

| Option | Description | Selected |
|--------|-------------|----------|
| Esqueleto + export; prompts não consomem | Mínimo CONTRACT-01 | ✓ |
| Módulos preenchidos; prompts ainda não | | |
| Preenchido + wiring em prompts | Escopo Phase 19 | |

**User's choice:** 1 — esqueleto apenas.

---

## Conteúdo persona vs rules

| Option | Description | Selected |
|--------|-------------|----------|
| Constantes vazias tipadas | | |
| Placeholders de 1 linha | | |
| persona stub; rules só pass/docstring | | ✓ |

**User's choice:** 3.

---

## API pública

| Option | Description | Selected |
|--------|-------------|----------|
| `get_persona_system()` | Função | ✓ (Claude) |
| Constantes | | |
| Dataclass GenerationSkill | | |

**User's choice:** “Não sei — tome a decisão; no verify work vemos.”
**Notes:** Locked as `get_persona_system() -> str`; reversible at verify.

---

## Idioma

| Option | Description | Selected |
|--------|-------------|----------|
| PT-BR | | ✓ |
| Inglês | | |
| Misto | | |

**User's choice:** 1 — PT-BR.

---

## Lista “nunca faça”

| Option | Description | Selected |
|--------|-------------|----------|
| Não incluir agora | | |
| TODO em `rules.py` listando itens futuros | | ✓ |
| Constante vazia tipada | | |

**User's choice:** 2.

---

## Claude's Discretion

- Wording do stub de persona e dos TODOs em `rules.py`
- Detalhe mínimo de `skills/__init__.py` para imports funcionarem no layout atual do `exercise-ai`

## Deferred Ideas

- Skill/rules em pastas de agente
- Conteúdo real de rules / authority / triad (17–18)
- Wiring em `prompts.py` (19+)
- Dataclass GenerationSkill até rules terem conteúdo
