# Roadmap: Gerador de Exercícios com IA

## Milestones

- ✅ **v1 MVP** — Phases 1–3 (shipped 2026-09-04) — [archive](./milestones/v1-ROADMAP.md) · [requirements](./milestones/v1-REQUIREMENTS.md) · [phases](./milestones/v1-phases/) · [audit](./milestones/v1-MILESTONE-AUDIT.md)
- ✅ **v1.1 Qualidade do exercício** — Phases 4–6 (shipped 2026-09-09) — [archive](./milestones/v1.1-ROADMAP.md) · [requirements](./milestones/v1.1-REQUIREMENTS.md) · [phases](./milestones/v1.1-phases/) · [audit](./milestones/v1.1-MILESTONE-AUDIT.md)
- ✅ **v1.2 Ops & Resilience** — Phases 7–10 (shipped 2026-09-15) — [archive](./milestones/v1.2-ROADMAP.md) · [requirements](./milestones/v1.2-REQUIREMENTS.md) · [phases](./milestones/v1.2-phases/) · [audit](./milestones/v1.2-MILESTONE-AUDIT.md)
- ✅ **v2.0 Embed em Produção** — Phases 11–12 (shipped 2026-09-18) — [archive](./milestones/v2.0-ROADMAP.md) · [requirements](./milestones/v2.0-REQUIREMENTS.md) · [phases](./milestones/v2.0-phases/) · [audit](./milestones/v2.0-MILESTONE-AUDIT.md)
- 🚧 **v2.1 Lotes dinâmicos** — Phases 13–15 (in progress)

## Current Milestone: v2.1 Lotes dinâmicos

**Goal:** O operador monta um lote com controle por exercício (dificuldade mista), em vez de N cópias do mesmo nível — schema → prompt/validator+demo → CLI/wizard.

**Requirements:** 11 v2.1 · see [REQUIREMENTS.md](./REQUIREMENTS.md)

### Phase 13: Request schema & plan contract

**Goal:** O domínio expressa um plano misto (ou uniforme) de forma tipada, com invariantes, sem quebrar o embed `generate_batch → ExerciseBatch`.
**Requirements:** BATCH-01, BATCH-02, BATCH-03, BATCH-04, CAP-01
**Success criteria:**

1. Operador/host pode enviar request com specs por item **ou** modo uniforme (`dificuldade` + `quantidade`)
2. Request com `quantidade` ≠ len(plano) é rejeitado antes da chamada LLM
3. Cada exercício no JSON tipado pode ecoar `dificuldade` do slot
4. Cap de quantidade permanece **40** (domínio + superfícies alinhadas)
5. Suite offline existente continua verde no caminho uniforme

### Phase 14: Mixed prompt + plan-adherence + demo enablement ✅

**Goal:** Lotes mistos são instruídos no prompt, verificados no validator, e **habilitados na demo** (mesmo `GenerationRequest`); RELY/math_check não são redesenhados.
**Requirements:** PROMPT-01, VAL-01, VAL-02, DEMO-01
**Plans:** 3/3 complete
**Status:** Complete — 2026-09-22
**Success criteria:**

1. Com plano misto, o prompt enumera cada slot → dificuldade esperada
2. Validator falha se count ou dificuldade por slot não aderir ao plano
3. Falhas de adesão/validação ainda entram no loop RELY existente (bounded)
4. math_check continua sem overhaul; fixtures offline cobrem mismatch de plano
5. Demo UI permite contagens por banda e `POST /gerar` monta `plano` (caminho misto exercitável sem CLI)

### Phase 15: CLI / wizard batch-plan UX ✅

**Goal:** Operador define o plano com UX compacta (wizard + argparse), sem N flags manuais; mesmo contrato já usado pela demo na Phase 14.
**Requirements:** UX-01, UX-02
**Success criteria:**

1. ✅ Wizard `gerar` permite contagens por banda (ex. fáceis/médios/difíceis) e monta o request
2. ✅ Argparse aceita plano compacto (ex. `--plano`) e deriva `itens`/`quantidade`
3. ✅ Documentação curta: embed/demo/CLI compartilham `GenerationRequest` enriquecido
4. ✅ Caller matrix (CLI, wizard, service, demo) verde offline

## Phases (shipped)

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

<details>
<summary>✅ v2.0 Embed em Produção (Phases 11–12) — SHIPPED 2026-09-18</summary>

- [x] Phase 11: Service Layer Extraction (3/3 plans) — completed 2026-09-16
- [x] Phase 12: Local Embed Demo (2/2 plans) — completed 2026-09-18

</details>

<details>
<summary>🚧 v2.1 Lotes dinâmicos (Phases 13–15) — IN PROGRESS</summary>

- [x] Phase 13: Request schema & plan contract (1/1 plans) — completed 2026-09-22
- [x] Phase 14: Mixed prompt + plan-adherence + demo enablement (3/3 plans) — completed 2026-09-22
- [ ] Phase 15: CLI / wizard batch-plan UX

</details>

## Deferred / open (not in v2.1 phases)

- **CAP-02** — subir cap finito (após v2.1)
- **TIPO-OPEN** — taxonomia de “tipo de raciocínio” (discuss/research; não bloqueia 13–15 de dificuldade mista)
- PKG-01, OBS-01, LOG-01, SEED-001/003/005/007/009

---
*Roadmap updated: 2026-09-22 — Phase 14 complete (UAT 4/4); next Phase 15*
