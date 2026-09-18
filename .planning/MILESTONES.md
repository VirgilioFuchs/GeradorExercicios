# Milestones

## v2.0 Embed em Produção (Shipped: 2026-09-18)

**Closeout:** override_closeout (2 dormant seeds acknowledged at close; audit status `passed`)  
**Known verification overrides:** 2 newly acknowledged (SEED-005, SEED-006), 2 carried forward from a prior close (see STATE.md Deferred Items)  
**Phases completed:** 2 phases, 5 plans, 12 tasks  
**Requirements:** 9/9 v2.0 satisfied  
**Integration:** 4/4 wiring · 3/3 E2E flows  
**Audit:** [v2.0-MILESTONE-AUDIT.md](./milestones/v2.0-MILESTONE-AUDIT.md)

**Key accomplishments:**

- Pure move of `service.generate_batch(request) -> ExerciseBatch` with `main.run` as CLI adapter; suite green after re-pointing monkeypatches
- Host-safe seam: 1–40 domain bounds, discriminable error kinds, always-on env restore, CLI-only postmortem, OSError-guarded flush.
- Windows cp1252-safe diagnostics, Gemini 30s HTTP timeout, and a README host embed contract covering the three error subclasses.
- Stdlib AF_INET6 demo on [::1]:8642 with POST /gerar → generate_batch, Host/Origin/JSON guards, Lock→409, and offline Wave 0 tests
- Operator demo UX with Contrato/Ambiente form, Exercícios|JSON tabs, Gerando…/error badges, throwaway banner, and anti-accretion docs

**Known tech debt (accepted):**

- PKG-01 packaging/rename (lead of next milestone); OBS-01 usage alongside batch; LOG-01 print→logging; Nyquist VALIDATION draft for phase 12 / missing for 11; `demo/` throwaway pending delete-at-operator discretion.

**Archives:** [roadmap](./milestones/v2.0-ROADMAP.md) · [requirements](./milestones/v2.0-REQUIREMENTS.md) · [phases](./milestones/v2.0-phases/) · [audit](./milestones/v2.0-MILESTONE-AUDIT.md)

---

## v1.2 Ops & Resilience (Shipped: 2026-09-15)

**Closeout:** override_closeout (2 dormant seeds acknowledged at close; audit status `tech_debt` accepted)  
**Known verification overrides:** 2 newly acknowledged (SEED-001, SEED-003), 0 carried forward  
**Phases completed:** 4 phases, 4 plans, 5 tasks  
**Requirements:** 11/11 v1.2 satisfied  
**Integration:** 11/11 wiring · 5/5 E2E flows  
**Audit:** [v1.2-MILESTONE-AUDIT.md](./milestones/v1.2-MILESTONE-AUDIT.md)

**Key accomplishments:**

- GitHub Actions CI runs `pytest exercise-ai -q` offline on push/PR to `master` (no LLM secrets).
- OpenAI ↔ Gemini auto-failover via a thin envelope around `generate_validated_batch`, with `api_error_kind` discrimination and a full offline D-12 mock matrix.
- Token usage observability: in-memory collector, `[USAGE]` stderr, day+provider NDJSON under `token-usage/`.
- Portuguese `gerar` wizard maps tip-backed Q&A into existing `main.run`, with global reasoning default `medium` and argparse kept for CI.

**Known tech debt (accepted):**

- CI-02 GitHub UI confirmation optional if not already observed; Nyquist VALIDATION missing for phases 8–10; wizard tests patch `run()` (no single E2E wizard→failover→flush test); Grok excluded from failover by design.

**Archives:** [roadmap](./milestones/v1.2-ROADMAP.md) · [requirements](./milestones/v1.2-REQUIREMENTS.md) · [phases](./milestones/v1.2-phases/) · [quick](./milestones/v1.2-quick/) · [audit](./milestones/v1.2-MILESTONE-AUDIT.md)

---

## v1.1 Qualidade do exercício (Shipped: 2026-09-09)

**Closeout:** verified_closeout (all artifact types clear; audit status `passed`)  
**Phases completed:** 3 phases, 3 plans, 9 tasks  
**Requirements:** 6/6 v1.1 satisfied  
**Integration:** 8/8 wiring · 6/6 E2E flows  
**Audit:** [v1.1-MILESTONE-AUDIT.md](./milestones/v1.1-MILESTONE-AUDIT.md)

**Key accomplishments:**

- CLI gera exercícios com flags PT, texto legível no stdout e JSON obrigatório em `--out`.
- Bounded regenerate loop in `reliability.py` with `retriable` API edges, aggregate `total_ms`/`chamadas`, and public `--max-retries` / `RELY_MAX_RETRIES`
- Stdlib arithmetic + ax+b=c math checks wired through validator into the existing RELY regen loop, with `[MATH]` dual-channel UX, exhaustion prefix, and final-only postmortem.

**Known tech debt (accepted):**

- Exhaustion plural grammar (`após 1 regenerações:`); suite Pydantic/genai warnings; Phase 6 VALIDATION.md optional (research skipped)

**Archives:** [roadmap](./milestones/v1.1-ROADMAP.md) · [requirements](./milestones/v1.1-REQUIREMENTS.md) · [phases](./milestones/v1.1-phases/)

---

## v1 MVP (Shipped: 2026-09-04)

**Closeout:** verified_closeout (all artifact types clear; audit status was `tech_debt` accepted at close)  
**Phases completed:** 3 phases, 3 plans, 8 tasks  
**Requirements:** 28/28 v1 satisfied  
**Integration:** 14/14 wiring · 5/5 E2E flows  
**Audit:** [v1-MILESTONE-AUDIT.md](./milestones/v1-MILESTONE-AUDIT.md)

**Key accomplishments:**

- Modular Python LLM generation pipeline using OpenAI Structured Outputs, Pydantic v2 schemas, centralized Portuguese prompts, and CLI JSON orchestration.
- Dual-provider dispatch (`LLM_PROVIDER`: OpenAI + Gemini) with env-based API keys.
- Semantic validation and typed OpenAI/Gemini API errors with two-layer Portuguese diagnostics and fail-fast CLI.
- Durable pytest suite (31 tests, no live LLM), LOG-01/02 sanitized stderr logging, root README.

**Known tech debt (accepted):**

- Nyquist/SECURITY missing for phases 1–2; WR-03/WR-04 edge mapping; Phase 3 EVAL partial; no CI Actions.

**Archives:** [roadmap](./milestones/v1-ROADMAP.md) · [requirements](./milestones/v1-REQUIREMENTS.md) · [phases](./milestones/v1-phases/)

---
