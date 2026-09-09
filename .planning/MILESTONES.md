# Milestones

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
