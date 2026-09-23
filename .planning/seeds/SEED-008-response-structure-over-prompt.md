---
id: SEED-008
status: dormant
planted: 2026-09-22
planted_during: v2.1 Phase 14 discuss (mixed prompt + plan-adherence + demo)
trigger_when: estrutura de resposta, response schema, ExerciseBatch contract, prompt inseguro, schema vs prompt, Structured Outputs authority, prompt injection, formato JSON do exercício, enunciado resposta explicacao
priority: high
scope: phase
audit_acknowledged:
  milestone: v2.1
  at: 2026-09-23
  status: dormant
---

# SEED-008: Estrutura de resposta autoritativa (prompt não é contrato seguro)

## Why This Matters

O gerador já monta a **resposta** como JSON tipado (`Exercise` / `ExerciseBatch`: enunciado, resposta, explicacao, echos de dificuldade, …) via Structured Outputs + Pydantic. Em paralelo, `prompts.py` **também descreve** esses campos em prosa no system/user prompt (“forneça enunciado, resposta, explicação…”).

Isso cria uma falsa sensação de segurança:

1. **Prompt não garante shape** — o modelo pode ignorar instruções, misturar markdown, ou “obedecer” a texto injetado em `materia`/`topico` (hoje interpolados crus no `USER_PROMPT_TEMPLATE`).
2. **Schema ≠ adesão pedagógica** — Structured Outputs garante chaves tipadas; **não** garante que o conteúdo respeite o plano (Pitfall 1 / research). A fonte de verdade do **formato** é o schema + validator; a do **plano** é `verify_plan_echo` / VAL — não a prosa do prompt.
3. Sem um artefato explícito (“a estrutura de resposta é o contrato; o prompt só instrui conteúdo”), agentes e fases futuras tendem a **endurecer o prompt** em vez de **endurecer o schema/validação** — o oposto do constraint do projeto (*LLM não é fonte de verdade*).

SEED-007 cobre persona/regras e a tríade validação/pensamento/resposta em nível de comportamento. **Este seed** cobre o contrato **estrutural** da resposta e a política “não confiar no prompt para shape”.

## When to Surface

**Trigger:** when goals mention response JSON structure, output contract, “prompt isn’t safe/reliable for format”, schema-as-authority, prompt injection via request fields, or rewriting prompts to “force” field lists that already exist on `Exercise`.

Surfaces during `$gsd-discuss-phase` / `$gsd-plan-phase` that touch `prompts.py` or `models.py` output fields, `$gsd-new-milestone` for output hardening, or `$gsd-quick` when someone proposes “put the JSON schema in the system prompt”.

Also relevant when adding new `Exercise` fields (BNCC, imagens, storytelling) — those land in **schema first**, prompt second (content hints only).

## What the operator asked for (capture verbatim intent)

1. Verificar se já existe seed sobre a **estrutura de resposta** que o gerador monta.
2. Motivo: a **estrutura de prompt não é segura** (não deve ser o contrato de formato).
3. Se não existir → **criar** a seed (dormant; não implementar agora necessariamente).

## Scope Estimate

**Phase-sized** (ou `$gsd-quick` se só documentação + testes de política):

| Slice | Likely content |
|-------|----------------|
| A — Contrato de saída | Doc curto (ex. `docs/RESPONSE-CONTRACT.md` ou seção no README Embed): campos canônicos de `Exercise` / `ExerciseBatch`; o que o host pode assumir; o que o prompt **não** garante |
| B — Política anti-prompt-as-schema | Regra/skill: proibir duplicar JSON schema no prompt; proibir “validar” formato só com instruções; schema Pydantic + `.parse()` + `validate_exercise_batch` são a autoridade |
| C — Prompt hygiene | Bound/escape/`materia`/`topico` (length caps, strip control chars); prompt descreve **conteúdo pedagógico**, não a árvore JSON |
| D — Testes de política | Offline: prompt unit tests assert **ausência** de dump de schema completo; presença de lista de slots (Phase 14) sem redefinir campos `enunciado`/`resposta`/`explicacao` como “API inventada” |
| E — Align Phase 14+ | Ao expandir prompt misto: enumerar slots/dificuldade; **não** re-listar o contrato de campos já forçado pelo `response_format` |

**Não é:** redesign do RELY; persona (SEED-007); lotes dinâmicos em si (SEED-006 — já promoveu schema echo); packaging (PKG-01).

## Suggested policy (for discuss / plan)

```
Autoridade de FORMATO  →  models.py (Exercise / ExerciseBatch) + Structured Outputs
Autoridade de PLANO    →  GenerationRequest.itens_ordenados + verify_plan_echo / validator
Autoridade de CONTEÚDO →  prompts (tópico, dificuldade por slot, tom) — best-effort
```

- Prompt pode dizer “respeite a dificuldade do slot i”.
- Prompt **não** substitui `response_format=ExerciseBatch` nem o validator.
- Novos campos de saída → Pydantic primeiro; prompt só se precisar de orientação semântica.

## Breadcrumbs

- Output models: `exercise-ai/models.py` (`Exercise`, `ExerciseBatch`, `verify_plan_echo`)
- Prompt (inseguro como contrato): `exercise-ai/prompts.py` (`SYSTEM_PROMPT`, `USER_PROMPT_TEMPLATE`, `build_prompts`)
- Validation: `exercise-ai/validator.py`, `exercise-ai/math_check.py`, `exercise-ai/reliability.py`
- Generators: `exercise-ai/generator*.py` (Structured Outputs / schema)
- Project constraint: `AGENTS.md` / `.planning/PROJECT.md` — LLM não é fonte de verdade
- Research: `.planning/research/PITFALLS.md` Pitfall 1 (schema vs prompt); SUMMARY “schema≠prompt”
- Related seeds: SEED-007 (persona / split validation-thinking-response); SEED-006 (mixed lots — echo fields); SEED-001/003 (new response fields later)

## Notes

Planted 2026-09-22 mid Phase 14 discuss: operator recalled that response structure should be the trusted artifact because prompt structure is not safe. Closest existing seed was SEED-007 (persona/rules) — complementary, not duplicate. Keep dormant until a phase/quick explicitly hardens output contract or prompt hygiene; Phase 14 should still treat schema+validator as authority when wiring mixed prompts (do not “fix” Exercise fields via longer prose).
