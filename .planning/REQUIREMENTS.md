# Requirements: Gerador de Exercícios com IA

**Defined:** 2026-09-04
**Core Value:** O usuário consegue gerar exercícios de matemática confiáveis e estruturados a partir de parâmetros simples, com validação que garante formato correto antes de usar o resultado.
**Milestone:** v1.1 Qualidade do exercício

## v1.1 Requirements

Requirements for this milestone. Each maps to roadmap phases.

### CLI

- [ ] **CLI-04**: Usuário passa matéria, tópico, dificuldade e quantidade via argumentos de linha de comando (`argparse`)

### Reliability

- [ ] **RELY-01**: Após falha de validação, o sistema regenera automaticamente no máximo 1–2 vezes (sem loop infinito)
- [ ] **RELY-02**: Logs registram duração da chamada LLM (sem segredos)
- [ ] **ERR-05**: Empty OpenAI `choices` e falhas Gemini não-`APIError` usam o mesmo caminho de erro mapeado (fecha WR-03/WR-04)

### Math quality

- [ ] **MATH-01**: Validador rejeita respostas matematicamente inconsistentes em casos básicos (escopo exato na discuss/plan da fase)
- [ ] **MATH-02**: Falha matemática gera mensagem clara e pode disparar regeneração (RELY), se aplicável

## Future Requirements

Deferred past v1.1. Tracked but not in current roadmap.

### Persistence & beyond

- **DB-01**: Persistência MySQL para alunos, exercícios, respostas e tentativas
- **ANLY-01**: Identificar tópicos com pior desempenho a partir de dados MySQL
- **PERS-01**: Gerar exercícios com contexto relevante do histórico do aluno
- **AGNT-01**: Agente com ciclo de decisão e ferramentas

### Ops

- **CI-01**: GitHub Actions rodando `pytest exercise-ai -q` em PR

## Out of Scope

| Feature | Reason |
|---------|--------|
| MySQL / analytics / personalização / agente | Salto de produto — pós v1.1 |
| GitHub Actions CI | Dívida ops; não é foco de qualidade do exercício |
| Frameworks multiagente (LangChain etc.) | Continua YAGNI no lab |
| Validação matemática avançada (CAS completo) | MATH-01 é básico apenas |
| Provider failover automático | Separado de RELY regeneração; defer |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CLI-04 | TBD | Pending |
| RELY-01 | TBD | Pending |
| RELY-02 | TBD | Pending |
| ERR-05 | TBD | Pending |
| MATH-01 | TBD | Pending |
| MATH-02 | TBD | Pending |

**Coverage:**
- v1.1 requirements: 6 total
- Mapped to phases: 0 (pending roadmap)
- Unmapped: 6

---
*Requirements defined: 2026-09-04*
*Last updated: 2026-09-04 after v1.1 requirements confirmation*
