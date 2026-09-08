---
phase: "01"
phase_name: "project-setup-llm-pipeline"
project: "Gerador de Exercícios com IA"
generated: "2026-09-02T14:14:00.000Z"
counts:
  decisions: 5
  lessons: 3
  patterns: 4
  surprises: 3
missing_artifacts: []
---

# Phase 01 Learnings: project-setup-llm-pipeline

## Decisions

### OpenAI Structured Outputs com Pydantic v2

Usar `client.beta.chat.completions.parse` com schema `ExerciseBatch` em vez de JSON livre via prompt.

**Rationale:** Garante aderência estrutural nativa do SDK, reduz parsing frágil e alinha com requisitos de confiabilidade do MVP.
**Source:** 01-CONTEXT.md (D-01), 01-01-SUMMARY.md

---

### Modelo padrão gpt-4o-mini

Fixar `gpt-4o-mini` como modelo default de geração.

**Rationale:** Custo baixo com suporte a structured outputs strict; adequado para laboratório e iteração rápida.
**Source:** 01-CONTEXT.md (D-02), 01-01-SUMMARY.md

---

### Campos de domínio em português no JSON

Contrato público com `exercicios`, `enunciado`, `resposta`, `explicacao`, `materia`, `topico`, `dificuldade`.

**Rationale:** Alinhamento com AGENT.md e público-alvo brasileiro; decisão de contrato one-way.
**Source:** 01-CONTEXT.md (D-05), 01-01-SUMMARY.md

---

### Estrutura modular em exercise-ai/

Separar responsabilidades em `main`, `generator`, `prompts`, `models`, `validator` dentro de `exercise-ai/`.

**Rationale:** YAGNI com fronteiras claras; validação completa e testes ficam para fases posteriores.
**Source:** 01-CONTEXT.md (D-07, D-08, D-09), 01-01-PLAN.md

---

### Entrada demo hardcoded no MVP

Parâmetros canônicos em `main.py` (equação 1º grau, fácil, quantidade 3); argparse adiado para v2.

**Rationale:** Reduz escopo da Fase 1 ao pipeline LLM end-to-end; CLI parametrizada é requisito futuro (CLI-04).
**Source:** 01-CONTEXT.md (D-10, D-12), 01-01-PLAN.md

---

## Lessons

### Resolução multi-path do .env é necessária

Executar de `exercise-ai/` ou da raiz exige fallback entre `exercise-ai/.env` e `.env` na raiz.

**Context:** Usuários podem invocar `python main.py` ou `python exercise-ai/main.py`; sem fallback, a chave parece ausente mesmo estando configurada.
**Source:** 01-01-SUMMARY.md (Decisions Made)

---

### Validador stub separa Fase 1 de Fase 2 com clareza

Pass-through mínimo em `validator.py` permite pipeline completo sem bloquear por regras ainda não implementadas.

**Context:** VERIFICATION confirma tipo e lista não vazia; validação semântica (quantidade, campos, JSON inválido) é escopo explícito da Fase 2.
**Source:** 01-VERIFICATION.md, 01-01-SUMMARY.md (Next Phase Readiness)

---

### UAT humano complementa cobertura automatizada

Seis deliverables auto-passaram via bloco `coverage:` no SUMMARY; smoke test manual confirmou geração real com API.

**Context:** Teste 1 validou execução real com OpenAI; Teste 2 confirmou que auto-verificação reflete expectativa do usuário.
**Source:** 01-UAT.md, 01-01-SUMMARY.md (coverage block)

---

## Patterns

### Pipeline linear determinístico

`main.py` → `prompts.build_prompts` → `generator.generate_exercises` → API → `ExerciseBatch` → `validator.validate_exercise_batch` → JSON stdout.

**When to use:** Fluxos CLI single-shot sem agentes; mantém observabilidade e testabilidade por etapa.
**Source:** 01-01-SUMMARY.md (patterns-established)

---

### Error boundary defensivo no CLI

Capturar `ValueError`, `RuntimeError` e exceção genérica; mensagens em `stderr`, exit code 1, sem mascarar causa.

**When to use:** Qualquer entry point que chama API externa ou validação; base para ERR-* da Fase 2.
**Source:** 01-01-SUMMARY.md, 01-VERIFICATION.md (Truth #4)

---

### Structured coverage no SUMMARY para UAT

Bloco YAML `coverage:` com `verification` refs e `human_judgment: false` permite auto-pass determinístico no verify-work.

**When to use:** Fases com verificação automatizada clara; reduz checkpoints manuais redundantes.
**Source:** 01-01-SUMMARY.md (frontmatter coverage), 01-UAT.md

---

### Single-responsibility por módulo Python

Um arquivo por concern (`models`, `prompts`, `generator`, `validator`, `main`) sem frameworks de agentes.

**When to use:** MVP Python com fronteira LLM; facilita mock de generator nos testes da Fase 3.
**Source:** 01-01-SUMMARY.md (Accomplishments)

---

## Surprises

### Execução sem desvios e sem issues

Plano executado exatamente como escrito; nenhum issue registrado no SUMMARY.

**Impact:** Fase 1 fechou com 4/4 truths verificados e 16/16 requisitos satisfeitos na primeira tentativa.
**Source:** 01-01-SUMMARY.md (Deviations, Issues Encountered)

---

### Duração real abaixo da média registrada

SUMMARY reporta 10 min; STATE acumula ~15 min/plano como média de velocidade.

**Impact:** Calibração de estimativas ainda indisponível (`sample_count: 0`, `applied: false`); próximas fases precisam de `estimate` no PLAN para calibrar.
**Source:** 01-01-SUMMARY.md (Performance), estimate-calibrate output

---

### UAT usou OpenAI, não Gemini

Smoke test passou com `LLM_API_KEY` (OpenAI); suporte Gemini foi adicionado depois via quick tasks.

**Impact:** Provedor validado em UAT foi OpenAI; dispatch multi-provedor (Gemini) ficou fora do escopo formal da Fase 1 mas útil operacionalmente.
**Source:** 01-UAT.md (Test 1 note)
