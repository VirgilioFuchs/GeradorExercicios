# Requirements: Gerador de Exercícios com IA

**Defined:** 2026-09-23  
**Milestone:** v2.2 Contrato de geração  
**Core Value:** Gerar exercícios de matemática confiáveis e estruturados com validação de formato — agora com contrato de domínio explícito (persona/regras) e schema como autoridade de formato.

## v2.2 Requirements

Requirements for this milestone. Each maps to roadmap phases.

### CONTRACT — Domain skill & authority

- [x] **CONTRACT-01**: Domain skill index exists for exercise generation (mirrors `skills/python-ai-engineering` pattern)
- [ ] **CONTRACT-02**: Docs/rules separate **validation** (deterministic code) vs **thinking** (API `reasoning_effort`) vs **response** (`Exercise` fields)
- [ ] **CONTRACT-03**: Authority map documented: format → schema/Structured Outputs · plan → `verify_plan_echo` · content → prompts

### PROMPT — Align prompts to contract

- [ ] **PROMPT-02**: SYSTEM/USER prompts mirror persona and pedagogical rules from the domain contract
- [ ] **PROMPT-03**: Field-contract prose listing enunciado/resposta/explicação as format API is removed from prompts
- [ ] **PROMPT-04**: Phase 14 slot enumeration is preserved for uniform and mixed batches

### VAL — Light code-owned hooks

- [ ] **VAL-03**: No LLM self-check path is added; structural/plan/math validation remain code-owned
- [ ] **VAL-04**: Light hygiene on interpolated `materia`/`topico` (bound and/or strip control chars) before prompt build

### TEST — Offline policy

- [ ] **TEST-01**: Offline tests assert absence of JSON-schema / field-contract dumps in prompts
- [ ] **TEST-02**: Offline tests assert slot list remains present in built prompts

## Future Requirements

Deferred; tracked but not in current roadmap.

### Packaging / ops

- **PKG-01**: Packaging `pyproject.toml` + rename `exercise_ai/`
- **OBS-01**: Usage/cost alongside batch return
- **LOG-01**: print → logging

### Product depth

- **CAP-02**: Raise finite quantity cap
- **TIPO-OPEN**: Pedagogical “tipo de raciocínio” taxonomy
- **SEED-001 / SEED-009**: BNCC skills → BNCC-aligned math_check
- **SEED-003**: Images / storytelling
- **SEED-005**: Usable postmortem UX

## Out of Scope

| Feature | Reason |
|---------|--------|
| LangChain / CrewAI / multi-agent validator | Lab constraint; LLM is not source of truth |
| Dump full JSON schema into SYSTEM_PROMPT | Format authority is Pydantic + Structured Outputs |
| RELY / math_check / failover redesign | Already shipped; SEED-009 waits on BNCC |
| PKG-01 / HTTP product API | Parked; embed seam already exists |
| Multi-persona personality packs | Single professor PT-BR until discuss unlocks |
| BNCC / images | Separate seeds |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CONTRACT-01 | Phase 16 | Complete |
| CONTRACT-02 | Phase 17 | Pending |
| CONTRACT-03 | Phase 18 | Pending |
| PROMPT-02 | Phase 19 | Pending |
| PROMPT-03 | Phase 20 | Pending |
| PROMPT-04 | Phase 21 | Pending |
| VAL-03 | Phase 22 | Pending |
| VAL-04 | Phase 23 | Pending |
| TEST-01 | Phase 24 | Pending |
| TEST-02 | Phase 25 | Pending |

**Coverage:**

- v2.2 requirements: 10 total
- Mapped to phases: 10
- Unmapped: 0

---
*Requirements defined: 2026-09-23*  
*Last updated: 2026-09-23 — v2.2 Contrato de geração (SEED-007 + SEED-008)*
