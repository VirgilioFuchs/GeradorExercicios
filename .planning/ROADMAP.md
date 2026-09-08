# Roadmap: Gerador de Exercícios com IA

## Milestones

- ✅ **v1 MVP** — Shipped 2026-09-04 (3 phases, 28 requirements) — [archive](./milestones/v1-ROADMAP.md) · [requirements](./milestones/v1-REQUIREMENTS.md) · [audit](./milestones/v1-MILESTONE-AUDIT.md)
- 🚧 **v1.1 Qualidade do exercício** — In progress (phases 4–6)

**Created:** 2026-09-04
**Core Value:** Gerar exercícios de matemática confiáveis e estruturados com validação de formato
**Granularity:** Coarse (3 phases)
**Mode:** Vertical MVP slices / tracer-friendly

## Overview

v1.1 endurece o pipeline MVP já shipped: CLI usável sem editar código, regeneração limitada após falha de validação com logs de duração e erros de API consistentes, e checagem matemática básica das respostas — sem DB, agente ou CI.

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 4 | CLI argparse | Usuário passa parâmetros via linha de comando | CLI-04 | 3 |
| 5 | Reliability & Error Edges | Regeneração limitada, duração LLM logada, erros API unificados | RELY-01, RELY-02, ERR-05 | 4 |
| 6 | Math Quality | Respostas matematicamente inconsistentes rejeitadas (com regeneração quando aplicável) | MATH-01, MATH-02 | 3 |

**Total:** 3 phases | 6 v1.1 requirements | 100% coverage ✓

---

## Phases

- [x] **Phase 4: CLI argparse** - Usuário gera exercícios passando matéria, tópico, dificuldade e quantidade por argumentos (completed 2026-09-08)
- [x] **Phase 5: Reliability & Error Edges** - Retry limitado pós-validação, log de duração LLM, edges de erro API unificados (completed 2026-09-08)
- [ ] **Phase 6: Math Quality** - Validador rejeita inconsistências matemáticas básicas e dispara regeneração quando aplicável

---

## Phase Details

### Phase 4: CLI argparse

**Goal:** Usuário passa matéria, tópico, dificuldade e quantidade via argumentos de linha de comando sem editar código
**Depends on:** Nothing (v1 MVP shipped — phases 1–3 complete)
**Requirements:** CLI-04
**Mode:** mvp
**Success Criteria** (what must be TRUE):

  1. Usuário executa o gerador com `--materia`, `--topico`, `--dificuldade`, `--quantidade` e `--out` obrigatório; recebe texto legível no stdout e JSON válido no arquivo `--out` (D-14)
  2. Argumentos inválidos ou `--out` ausente produzem mensagem de uso clara em português no stderr (exit não-zero) sem chamar o LLM
  3. README documenta a invocação por argumentos (incluindo `--provider` e `--out`)

**Plans:** 1/1 plans executed
Plans:

- [x] 04-01-PLAN.md — CLI argparse tracer (text stdout + required --out) then full flags/provider/docs

### Phase 5: Reliability & Error Edges

**Goal:** Após falha de validação o sistema regenera no máximo 1–2 vezes; duração da chamada LLM é observável; edges de erro API usam o mesmo caminho mapeado
**Depends on:** Phase 4 (CLI é a superfície de uso; regeneração/erros atuam no mesmo fluxo)
**Requirements:** RELY-01, RELY-02, ERR-05
**Mode:** mvp
**Success Criteria** (what must be TRUE):

  1. Após falha de validação, o sistema tenta regenerar no máximo 1–2 vezes e para (sem loop infinito); sucesso na regeneração entrega JSON válido
  2. Se todas as tentativas falham, o usuário vê erro claro de validação (não hang nem retry silencioso)
  3. Logs (stderr) registram duração da chamada LLM sem segredos (API keys / payloads sensíveis)
  4. Empty OpenAI `choices` e falhas Gemini não-`APIError` produzem o mesmo tipo de erro mapeado/usuário que os demais erros de API (fecha WR-03/WR-04)

**Plans**: 1/1 plans

Plans:

- [x] 05-01-PLAN.md — Reliability loop, ERR-05 edges, RELY_MAX_RETRIES docs + Phase 6 hook

### Phase 6: Math Quality

**Goal:** Validador rejeita respostas matematicamente inconsistentes em casos básicos; falha matemática gera mensagem clara e pode disparar regeneração (RELY)
**Depends on:** Phase 5 (hooks de regeneração RELY disponíveis)
**Requirements:** MATH-01, MATH-02
**Mode:** mvp
**Success Criteria** (what must be TRUE):

  1. Validador rejeita respostas matematicamente inconsistentes nos casos básicos definidos na discuss/plan da fase (testável sem LLM real)
  2. Falha matemática produz mensagem clara identificando o problema (distinta de falha estrutural genérica)
  3. Quando aplicável, falha matemática dispara o caminho de regeneração limitada (RELY-01); esgotadas as tentativas, o fluxo falha de forma previsível

**Plans**: TBD

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 4. CLI argparse | 1/1 | Complete | 2026-09-08 |
| 5. Reliability & Error Edges | 1/1 | Complete | 2026-09-08 |
| 6. Math Quality | 0/? | Not started | - |

---

## Phase Ordering Rationale

1. **Phase 4 first:** CLI argparse é o vertical slice mais isolado — usuário já gera exercícios; torna parâmetros observáveis sem depender de retry/math
2. **Phase 5 second:** Reliability endurece o pipeline de geração/validação existente (retry, timing, error edges) antes de acrescentar checagens novas
3. **Phase 6 last:** Math quality estende o validador e reusa o hook de regeneração da Phase 5 (MATH-02 → RELY)

## Future Themes (post v1.1)

Tracked in REQUIREMENTS.md Future / Out of Scope — not in this roadmap:

- **Persistence:** MySQL (DB-01)
- **Analytics / Personalization / Agent:** ANLY-01, PERS-01, AGNT-01
- **Ops:** GitHub Actions CI (CI-01)
- **Reliability (deferred):** Provider failover automático

---
*Roadmap created: 2026-09-04 (v1.1)*
*v1 archived: 2026-09-04 — see ./milestones/*
