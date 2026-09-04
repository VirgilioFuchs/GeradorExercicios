---
phase: "02"
phase_name: "validation-error-handling"
project: "Gerador de Exercícios com IA"
generated: "2026-09-04T12:24:00.000Z"
counts:
  decisions: 6
  lessons: 5
  patterns: 4
  surprises: 4
missing_artifacts: []
---

# Phase 02 Learnings: validation-error-handling

## Decisions

### Validar no ExerciseBatch já parseado (D-01)

Regras semânticas (quantidade, campos, lista) operam no objeto Pydantic pós-Structured Outputs, não em JSON bruto livre.

**Rationale:** Structured Outputs já garante schema; a Fase 2 fecha gaps semânticos (cardinalidade, whitespace) sem reintroduzir parsing frágil.
**Source:** 02-CONTEXT.md (D-01), 02-01-PLAN.md

---

### Duas camadas de stderr (D-05 / D-09)

Usuário vê texto PT plano via `print(str(err))`; logs detalhados usam prefixos `[VALIDAÇÃO]` / `[API:openai|gemini]` e dados brutos.

**Rationale:** Documentação/debug sem poluir a mensagem principal nem o stdout JSON.
**Source:** 02-CONTEXT.md (D-05, D-09), 02-01-SUMMARY.md

---

### VALIDATION_REPORT_MODE como constante no código (D-08)

Constante `"all"` | `"first_exercise"` em `validator.py`, não env var.

**Rationale:** Preferência explícita na discuss-phase; evita config operacional prematura no MVP.
**Source:** 02-CONTEXT.md (D-08), 02-01-SUMMARY.md

---

### Fail-fast sem retry (D-13)

Abortar com exit 1 em falha de validação ou API; sem loop de regeneração nesta fase.

**Rationale:** RELY-* e failover ficam em v2; Fase 2 só reporta erros com clareza.
**Source:** 02-CONTEXT.md (D-13, deferred), 02-01-PLAN.md

---

### Gemini: tabela status_code quando subclasses tipadas não existem

Documentar `GEMINI_ERROR_CLASSIFICATION:` com `priority-1 N/A on this SDK` e mapear 401/403, 429, 408/504 + heurística de rede.

**Rationale:** SDK `google-genai` instalado não expõe subclasses timeout/rate/auth/connection nomeadas; inventar classes falsas quebraria o contrato do plano.
**Source:** 02-01-SUMMARY.md (key-decisions), 02-VERIFICATION.md

---

### Mensagem unificada de chave ausente (D-10)

Uma frase PT nomeando `GEMINI_API_KEY` e `LLM_API_KEY` / `.env` em `_resolve_provider` e ambos `get_client`.

**Rationale:** ERR-01 e UX consistente independente do provedor escolhido.
**Source:** 02-CONTEXT.md (D-10), 02-01-SUMMARY.md

---

## Lessons

### Harness de exceções OpenAI precisa capturar mais que TypeError

Construtores recentes do SDK podem levantar `AttributeError` com `response=None` antes do fallback de subclass no `_make()` do plano.

**Context:** Task 2 verify falhou no harness; produção `map_openai_error` estava correta. Harness local alargou para `Exception`; script do PLAN como colado ainda pode falhar neste SDK.
**Source:** 02-01-SUMMARY.md (Deviations)

---

### Verifies efêmeros não contam como suite de eval

Scripts `_verify_02_*.py` / `python -c` passam must_haves mas somem do repo; EVAL-REVIEW marca dimensões como PARTIAL/MISSING e score 16/100 (NOT IMPLEMENTED).

**Context:** AI-SPEC e ROADMAP deferiram pytest à Fase 3; o auditor trata isso como gap de cobertura de avaliação, não como falha de implementação dos guardrails.
**Source:** 02-EVAL-REVIEW.md, 02-AI-SPEC.md, 02-VERIFICATION.md

---

### `str(exc)` em logs `[API:*]` pode vazar fragmentos de chave

Code review WR-01: `AuthenticationError` e corpos de provedor frequentemente incluem a chave (ou prefixo `sk-...`) quando logados com `str(exc)`.

**Context:** Mensagem ao usuário está sanitizada; a camada de log detalhado ainda viola “API keys never in logs” sem redaction.
**Source:** 02-REVIEW.md (WR-01), 02-EVAL-REVIEW.md (No secret leakage MISSING)

---

### Auto-chain após plan-only quebra intenção do usuário

`$gsd-plan-phase` com auto-advance iniciou execute quando o usuário só queria planejar; foi cancelado e handoff registrou anti-pattern blocking.

**Context:** Resume/execute só após `$gsd-execute-phase` explícito; `_auto_chain_active` limpo.
**Source:** Session handoff / `.continue-here` (consumido), 02-UAT.md (fluxo pós-pause)

---

### Gate api-coverage bloqueia UAT sem COVERAGE.md

verify:pre com `workflow.api_coverage_gate` exige matriz INTEGRATE/OPT-OUT antes de `$gsd-verify-work`.

**Context:** Phase 2 integra OpenAI+Gemini; COVERAGE.md criado na retomada do UAT (12 INTEGRATE / 6 OPT-OUT).
**Source:** 02-UAT.md session, COVERAGE.md

---

## Patterns

### Validation failure: log then raise plain ValueError

Escrever `[VALIDAÇÃO]` + JSON bruto em stderr; `raise ValueError(user_message)` sem prefixo na exception.

**When to use:** Qualquer falha semântica pós-parse antes de stdout.
**Source:** 02-01-SUMMARY.md (patterns-established), 02-VERIFICATION.md

---

### API failure: map_*_error + [API:provider] then RuntimeError PT

Helpers testáveis logam tipo/detalhe e retornam `RuntimeError` plain; caller usa `raise mapped from exc`.

**When to use:** Timeouts, rate limits, auth, conexão, empty/refusal/unparseable em ambos provedores.
**Source:** 02-01-SUMMARY.md, 02-01-PLAN.md

---

### main user line sempre `print(str(err))`

Sem wrappers `"Erro de configuração…"`; stage labels só em stderr; sucesso = stdout JSON-only.

**When to use:** Boundary do CLI demo e qualquer orquestração fail-fast alinhada a D-05/D-14/D-15.
**Source:** 02-01-SUMMARY.md, 02-VERIFICATION.md, 02-UAT.md

---

### Tracer then expand (2 tasks, inline threshold)

Task 1 tracer (validator + main labels) com verify automatizado; Task 2 expande mappers API; Pattern C inline quando `task_count <= inline_plan_threshold`.

**When to use:** Fases pequenas de harden com contrato e2e no primeiro task.
**Source:** 02-01-PLAN.md, 02-01-SUMMARY.md (Task Commits)

---

## Surprises

### google-genai sem subclasses tipadas de erro

Prioridade-1 do plano (isinstance em Timeout/Rate/Auth/Connection) não aplicável no SDK instalado.

**Impact:** Documentação `priority-1 N/A` + tabela status_code; classify-coverage e verifies aceitaram o caminho documentado.
**Source:** 02-01-SUMMARY.md, 02-VERIFICATION.md

---

### Estimate 45 min vs actual ~25 min

Plano estimou 45 min; SUMMARY registrou duração ~25 min (2 tasks, 4 files).

**Impact:** Calibração de estimativa para fases similares de harden/error-handling.
**Source:** 02-01-PLAN.md (`estimate: 45min`), 02-01-SUMMARY.md (`duration: 25 min`)

---

### Empty `completion.choices` foge do map_openai_error

IndexError em `choices[0]` não é `OpenAIError` → cai no `except Exception` genérico do main (WR-03).

**Impact:** Mensagem PT de ERR-03 pode não aparecer; gap residual para Fase 3 / fix de review.
**Source:** 02-REVIEW.md (WR-03)

---

### Smoke DEMO_API_ERROR ajudou UAT mas não deve permanecer

Gancho temporário nos generators permitiu 12/12 smokes de mensagens CLI; removido após confirmação do usuário.

**Impact:** Bom padrão de demo local; risco se esquecido no código de produção (foi removido antes do UAT complete).
**Source:** 02-UAT.md (note no teste 1)

---
