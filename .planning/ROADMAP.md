# Roadmap: Gerador de Exercícios com IA

## Milestones

- ✅ **v1 MVP** — Phases 1–3 (shipped 2026-09-04) — [archive](./milestones/v1-ROADMAP.md) · [requirements](./milestones/v1-REQUIREMENTS.md) · [phases](./milestones/v1-phases/) · [audit](./milestones/v1-MILESTONE-AUDIT.md)
- ✅ **v1.1 Qualidade do exercício** — Phases 4–6 (shipped 2026-09-09) — [archive](./milestones/v1.1-ROADMAP.md) · [requirements](./milestones/v1.1-REQUIREMENTS.md) · [phases](./milestones/v1.1-phases/) · [audit](./milestones/v1.1-MILESTONE-AUDIT.md)
- ✅ **v1.2 Ops & Resilience** — Phases 7–10 (shipped 2026-09-15) — [archive](./milestones/v1.2-ROADMAP.md) · [requirements](./milestones/v1.2-REQUIREMENTS.md) · [phases](./milestones/v1.2-phases/) · [audit](./milestones/v1.2-MILESTONE-AUDIT.md)
- 🚧 **v2.0 Embed em Produção** — Phases 11–12 (in progress)

## Phases

<details>
<summary>✅ v1 MVP (Phases 1–3) — SHIPPED 2026-09-04</summary>

- [x] Phase 1: Project Setup & LLM Pipeline (1/1 plans)
- [x] Phase 2: Validation & Error Handling (1/1 plans)
- [x] Phase 3: Tests, Logging & Docs (1/1 plans)

</details>

<details>
<summary>✅ v1.1 Qualidade do exercício (Phases 4–6) — SHIPPED 2026-09-09</summary>

- [x] Phase 4: CLI argparse (1/1 plans)
- [x] Phase 5: Reliability & Error Edges (1/1 plans)
- [x] Phase 6: Math Quality (1/1 plans)

</details>

<details>
<summary>✅ v1.2 Ops & Resilience (Phases 7–10) — SHIPPED 2026-09-15</summary>

- [x] Phase 7: Continuous Integration (1/1 plans)
- [x] Phase 8: Provider Failover (1/1 plans)
- [x] Phase 9: Token Usage Observability (1/1 plans)
- [x] Phase 10: Interactive CLI Wizard (1/1 plans)

</details>

### 🚧 v2.0 Embed em Produção (In Progress)

**Milestone Goal:** Expor o gerador como biblioteca embutível (`service.generate_batch` → `ExerciseBatch`) e demonstrar o fluxo de integração para o time do host (SEED-003 Slice A).

- [x] **Phase 11: Service Layer Extraction** — Fronteira de embed in-process: lote validado, erros discrimináveis, CLI intacta, env restaurado, encoding/timeout endurecidos (completed 2026-09-16)
- [ ] **Phase 12: Local Embed Demo** — Página throwaway em `demo/` (`http://[::1]:8642/`, stdlib only) como aceite visual do contrato

## Phase Details

### Phase 11: Service Layer Extraction

**Goal**: Host embute o gerador in-process via `generate_batch` e recebe `ExerciseBatch` validado (ou erro discriminável), sem derrubar o processo; CLI argparse e wizard `gerar` permanecem idênticos.
**Depends on**: Phase 10 (shipped)
**Requirements**: EMBED-01, EMBED-02, EMBED-03, EMBED-04, EMBED-05, EMBED-06, EMBED-07
**Success Criteria** (what must be TRUE):

  1. Host chama `generate_batch(request)` e recebe `ExerciseBatch` validado — sem print de exercício, sem arquivo de saída, sem `sys.exit` no caminho de biblioteca
  2. Host distingue falha de configuração, entrada inválida e geração esgotada sem casar mensagem PT (`kind` / subclasses dos tipos já levantados)
  3. Operator executa CLI argparse e wizard `gerar` com comportamento idêntico ao pré-extração; bound 1–40 preservado no domínio e no argparse
  4. Após qualquer chamada (com ou sem failover), `LLM_PROVIDER` (e overrides de reasoning, se usados) voltam ao valor anterior
  5. Client Gemini tem timeout HTTP finito com pior caso documentado; diagnósticos/CLI não quebram em cp1252 com glifos como `√`/`→`; documentação curta do contrato (JSON + tabela de erros) e lista de nomes de módulo reservados estão disponíveis

**Plans**: 3/3 plans executed

Plans:

- [x] 11-01-PLAN.md — Pure seam: `service.generate_batch` + `run()` adapter + re-point pinned tests
- [x] 11-02-PLAN.md — Domain 1–40, error subclasses, scoped env restore, FS hygiene / guarded flush
- [x] 11-03-PLAN.md — Encoding harden, Gemini timeout, README embed contract + reserved names

**Notes**: Sequenciar pure seam move primeiro (suite verde), depois higiene de env/`kind`/encoding/timeout. Manter `generate_batch(...) -> ExerciseBatch` (não alargar). Packaging (PKG-01) e print→logging ficam fora — débito conhecido / próximo milestone.

### Phase 12: Local Embed Demo

**Goal**: Operator e time do host veem o fluxo de integração ponta a ponta numa demo local throwaway que consome o contrato da Phase 11.
**Depends on**: Phase 11
**Requirements**: DEMO-01, DEMO-02
**Success Criteria** (what must be TRUE):

  1. Operator abre `http://[::1]:8642/` e vê form CLI-equivalente, exercícios renderizados, JSON bruto do contrato, estado "Gerando…" e erro por categoria
  2. Servidor recusa bind não-loopback; segunda geração concorrente recebe HTTP 409 (Lock); POST de geração exige `application/json` e Host/Origin na allowlist
  3. Banner throwaway e README da demo deixam explícita a nota de expiração / delete-at-close

**Plans**: 2 plans

Plans:

- [ ] 12-01-PLAN.md — Wave 0 guards/error_map + tracer POST `/gerar` → `generate_batch` (Lock/Host/Origin/JSON)
- [ ] 12-02-PLAN.md — Full UI D-01..D-12 + throwaway chrome/docs D-13..D-16

**UI hint**: yes

**Notes**: Stdlib only (`ThreadingHTTPServer` + `AF_INET6`); fora do pacote e do CI. Demo carrega `.env` no próprio `__main__` — service não faz `load_dotenv` na importação.

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 11. Service Layer Extraction | 3/3 | Complete    | 2026-09-16 |
| 12. Local Embed Demo | 0/2 | Planned | - |

## Next Milestone (after v2.0)

**Lead item:** **PKG-01** — Packaging `pyproject.toml` + rename `exercise_ai/` (pré-condição do embed in-process real; `sys.path.insert` empiricamente quebrado).

Other deferred themes (not this roadmap): OBS-01 (usage alongside batch), LOG-01 (print→logging), SEED-003 B/C (imagens/storytelling), SEED-001 BNCC, MySQL / analytics / personalização / agente.

---
*Last milestone shipped: v1.2 — 2026-09-15*
*Active: v2.0 Embed em Produção — Phases 11–12*
*Roadmap created: 2026-09-16*
