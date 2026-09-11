# Roadmap: Gerador de Exercícios com IA

## Milestones

- ✅ **v1 MVP** — Phases 1–3 (shipped 2026-09-04) — [archive](./milestones/v1-ROADMAP.md) · [requirements](./milestones/v1-REQUIREMENTS.md) · [phases](./milestones/v1-phases/) · [audit](./milestones/v1-MILESTONE-AUDIT.md)
- ✅ **v1.1 Qualidade do exercício** — Phases 4–6 (shipped 2026-09-09) — [archive](./milestones/v1.1-ROADMAP.md) · [requirements](./milestones/v1.1-REQUIREMENTS.md) · [phases](./milestones/v1.1-phases/) · [audit](./milestones/v1.1-MILESTONE-AUDIT.md)
- 🚧 **v1.2 Ops & Resilience** — Phases 7–8 (in progress)

## Phases

<details>
<summary>✅ v1 MVP (Phases 1–3) — SHIPPED 2026-09-04</summary>

- [x] Phase 1: Project Setup & LLM Pipeline (1/1 plans)
- [x] Phase 2: Validation & Error Handling (1/1 plans)
- [x] Phase 3: Tests, Logging & Docs (1/1 plans)

</details>

<details>
<summary>✅ v1.1 Qualidade do exercício (Phases 4–6) — SHIPPED 2026-09-09</summary>

- [x] Phase 4: CLI argparse (1/1 plans) — completed 2026-09-08
- [x] Phase 5: Reliability & Error Edges (1/1 plans) — completed 2026-09-08
- [x] Phase 6: Math Quality (1/1 plans) — completed 2026-09-09

</details>

### 🚧 v1.2 Ops & Resilience (In Progress)

**Milestone Goal:** Deixar o lab confiável fora da máquina local — CI automatizado no GitHub e failover de provider quando a API principal falha.

- [ ] **Phase 7: Continuous Integration** — GitHub Actions roda pytest sem LLM live em push/PR
- [ ] **Phase 8: Provider Failover** — Fallback automático OpenAI ↔ Gemini em erros retriáveis/indisponibilidade

## Phase Details

### Phase 7: Continuous Integration
**Goal**: Todo push/PR no GitHub dispara um job que instala deps e roda a suíte pytest do `exercise-ai` sem chamar LLM live nem exigir secrets de API; falha de teste deixa o check vermelho e visível no PR.
**Depends on**: Phase 6 (shipped)
**Requirements**: CI-01, CI-02
**Success Criteria** (what must be TRUE):
  1. Em push ou abertura/atualização de PR, o operator vê um workflow GitHub Actions iniciando para o repositório
  2. O job instala dependências do pacote e executa `pytest` no `exercise-ai` sem variáveis/secrets de API de LLM no workflow
  3. Quando a suíte passa, o check no PR fica verde; quando falha, fica vermelho e o merge confiante fica bloqueado pelo status visível
  4. A suíte no CI não faz chamadas live a OpenAI/Gemini (mesma garantia local: sem LLM real)
**Plans**: 1 plan

Plans:
- [ ] 07-01-PLAN.md — Single-job GitHub Actions CI (pytest offline) + README note

### Phase 8: Provider Failover
**Goal**: Se o provider primário falhar com erro retriável ou indisponibilidade, o sistema tenta automaticamente o outro (OpenAI ↔ Gemini), reusando o caminho existente de geração/validação/RELY (sem segundo loop) e deixando claro nos logs qual provider foi tentado/usado — sem secrets.
**Depends on**: Phase 7
**Requirements**: FAILOVER-01, FAILOVER-02, FAILOVER-03
**Success Criteria** (what must be TRUE):
  1. Com o provider primário indisponível ou em erro retriável, o usuário ainda obtém geração via o provider secundário sem mudar flags de CLI além da config de provider
  2. Failover não introduz um segundo loop de regeneração math/RELY — a tentativa no provider alternativo reusa `generate_validated_batch` / caminho de validação já existente
  3. Em stderr, o operator consegue identificar qual provider foi tentado e qual foi usado após failover (tags/mensagens sem secrets)
  4. Falhas não-retriáveis no primário não disparam failover indevido (comportamento previsível para o operator)
  5. Testes cobrem o caminho de failover sem LLM live (mocks/fakes)
**Plans**: TBD

Plans:
- [ ] 08-01: TBD (created during plan-phase)

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Project Setup & LLM Pipeline | v1 | 1/1 | Complete | 2026-09-04 |
| 2. Validation & Error Handling | v1 | 1/1 | Complete | 2026-09-04 |
| 3. Tests, Logging & Docs | v1 | 1/1 | Complete | 2026-09-04 |
| 4. CLI argparse | v1.1 | 1/1 | Complete | 2026-09-08 |
| 5. Reliability & Error Edges | v1.1 | 1/1 | Complete | 2026-09-08 |
| 6. Math Quality | v1.1 | 1/1 | Complete | 2026-09-09 |
| 7. Continuous Integration | v1.2 | 0/1 | Planned | - |
| 8. Provider Failover | v1.2 | 0/TBD | Not started | - |

## Future Themes

Tracked for next milestone planning (`$gsd-new-milestone`):

- **Persistence:** MySQL (DB-01)
- **Analytics / Personalization / Agent:** ANLY-01, PERS-01, AGNT-01
- **Curriculum:** BNCC / habilidades (BNCC-01 / SEED-001 — dormant)

---
*Last milestone archived: v1.1 — 2026-09-09*
*v1.2 roadmap created: 2026-09-09*
