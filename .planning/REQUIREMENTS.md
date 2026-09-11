# Requirements: Gerador de Exercícios com IA

**Defined:** 2026-09-09
**Core Value:** O usuário consegue gerar exercícios de matemática confiáveis e estruturados a partir de parâmetros simples, com validação que garante formato correto antes de usar o resultado.
**Milestone:** v1.2 Ops & Resilience

## v1.2 Requirements

Requirements for this milestone. Each maps to roadmap phases.

### Ops (CI)

- [x] **CI-01**: Em push/PR no GitHub, Actions instala deps e roda `pytest` no pacote `exercise-ai` sem chamar LLM live (sem secrets de API no job)
- [x] **CI-02**: Falha de testes deixa o check vermelho e bloqueia merge confiante (status visível no PR)

### Reliability (failover)

- [ ] **FAILOVER-01**: Se o provider primário falhar com erro retriável/indisponibilidade, o sistema tenta o outro provider (OpenAI ↔ Gemini) automaticamente
- [ ] **FAILOVER-02**: Failover não cria um segundo loop de regeneração math/RELY — reusa o caminho existente de geração/validação
- [ ] **FAILOVER-03**: Logs deixam claro qual provider foi tentado/usado no failover (sem secrets)

## Future Requirements

Deferred past v1.2. Tracked but not in current roadmap.

### Persistence & beyond

- **DB-01**: Persistência MySQL para alunos, exercícios, respostas e tentativas
- **ANLY-01**: Identificar tópicos com pior desempenho a partir de dados MySQL
- **PERS-01**: Gerar exercícios com contexto relevante do histórico do aluno
- **AGNT-01**: Agente com ciclo de decisão e ferramentas

### Curriculum

- **BNCC-01**: Habilidades BNCC na geração (SEED-001 — dormant)

## Out of Scope

| Feature | Reason |
|---------|--------|
| BNCC / SEED-001 | Adiado de propósito neste milestone |
| MySQL / analytics / personalização / agente | Salto de produto — v2+ |
| CAS / validação matemática avançada | Já coberto em nível básico no v1.1 |
| Frameworks multiagente (LangChain etc.) | Continua YAGNI no lab |
| Polish-only debt batch (grammar, Nyquist backfill) | Fora do foco ops & resilience |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CI-01 | Phase 7 | Complete |
| CI-02 | Phase 7 | Complete |
| FAILOVER-01 | Phase 8 | Pending |
| FAILOVER-02 | Phase 8 | Pending |
| FAILOVER-03 | Phase 8 | Pending |

**Coverage:**

- v1.2 requirements: 5 total
- Mapped to phases: 5
- Unmapped: 0 ✓

---
*Requirements defined: 2026-09-09*
*Last updated: 2026-09-09 after v1.2 roadmap*
