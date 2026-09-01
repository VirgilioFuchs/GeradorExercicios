# Requirements: Gerador de Exercícios com IA

**Defined:** 2026-09-01
**Core Value:** O usuário consegue gerar exercícios de matemática confiáveis e estruturados a partir de parâmetros simples, com validação que garante formato correto antes de usar o resultado.

## v1 Requirements

### Project Scaffold

- [ ] **SCAF-01**: Projeto Python com estrutura modular (`main.py`, `generator.py`, `validator.py`, `prompts.py`, `models.py`)
- [ ] **SCAF-02**: `requirements.txt` com dependências mínimas documentadas
- [ ] **SCAF-03**: `.env.example` documenta `LLM_API_KEY`; `.env` no `.gitignore`
- [ ] **SCAF-04**: `README.md` com instruções de setup e execução

### Data Models

- [ ] **MODL-01**: Modelo `Exercise` com campos `enunciado`, `resposta`, `explicacao`
- [ ] **MODL-02**: Modelo de lote com chave `exercicios` (lista de exercícios)
- [ ] **MODL-03**: Modelo de entrada com `materia`, `topico`, `dificuldade`, `quantidade`

### Prompts

- [ ] **PRMT-01**: Template de prompt centralizado em `prompts.py`
- [ ] **PRMT-02**: Prompt instrui modelo a respeitar tópico, dificuldade e quantidade exata
- [ ] **PRMT-03**: Prompt exige retorno somente JSON, sem texto extra

### Generation

- [ ] **GEN-01**: Usuário pode gerar exercícios informando matéria, tópico, dificuldade e quantidade
- [ ] **GEN-02**: Gerador chama LLM via SDK (preferir Structured Outputs quando disponível)
- [ ] **GEN-03**: Gerador converte resposta para estrutura de dados tipada
- [ ] **GEN-04**: Chave de API carregada de variável de ambiente (nunca hardcoded)

### Validation

- [ ] **VALD-01**: Validador rejeita JSON inválido ou estrutura ausente
- [ ] **VALD-02**: Validador verifica presença da chave `exercicios`
- [ ] **VALD-03**: Validador verifica quantidade de exercícios igual à solicitada
- [ ] **VALD-04**: Validador verifica campos obrigatórios não vazios em cada exercício
- [ ] **VALD-05**: Validador retorna motivo claro de falha para cada caso

### Error Handling

- [ ] **ERR-01**: Erro claro quando chave de API está ausente
- [ ] **ERR-02**: Tratamento de erro de rede, timeout e rate limit
- [ ] **ERR-03**: Tratamento de resposta vazia ou estrutura inválida
- [ ] **ERR-04**: Erros não são silenciados; mensagens úteis para desenvolvimento

### CLI & Output

- [ ] **CLI-01**: `python main.py` executa fluxo completo com entrada de demonstração ou parâmetros
- [ ] **CLI-02**: Saída final é JSON válido no formato especificado
- [ ] **CLI-03**: Fluxo: entrada → geração → validação → saída ou erro

### Testing

- [ ] **TEST-01**: Testes unitários do validador sem chamadas reais ao LLM
- [ ] **TEST-02**: Casos: JSON válido, JSON inválido, chave ausente, campo faltando, quantidade errada, lista vazia

### Logging

- [ ] **LOG-01**: Logs de desenvolvimento registram início, parâmetros (sem segredos), sucesso/falha e motivo de validação
- [ ] **LOG-02**: Chave de API e dados sensíveis nunca aparecem em logs

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Reliability

- **RELY-01**: Regeneração automática com máximo de 1–2 tentativas após falha de validação
- **RELY-02**: Log de duração da chamada LLM

### CLI Enhancement

- **CLI-04**: Argumentos de linha de comando (argparse) para todos os parâmetros de entrada

### Math Validation

- **MATH-01**: Validação matemática básica de respostas (além da estrutural)

### Persistence

- **DB-01**: Persistência MySQL para alunos, exercícios, respostas e tentativas

### Analytics

- **ANLY-01**: Identificar tópicos com pior desempenho a partir de dados MySQL

### Personalization

- **PERS-01**: Gerar exercícios com contexto relevante do histórico do aluno

### Agent

- **AGNT-01**: Agente com ciclo de decisão e ferramentas (consultar DB, gerar, validar, salvar)

## Out of Scope

| Feature | Reason |
|---------|--------|
| LangChain / CrewAI / AutoGen | AGENT.md — complexidade desnecessária no MVP |
| RAG / banco vetorial | Sem necessidade de retrieval na v1 |
| Filas / microsserviços | YAGNI para CLI local |
| Interface web | Foco no pipeline core primeiro |
| Agente multi-step | Somente após MySQL e análise de desempenho |
| Validação matemática profunda | Estrutura primeiro; correção matemática em v2+ |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SCAF-01 | Phase 1 | Pending |
| SCAF-02 | Phase 1 | Pending |
| SCAF-03 | Phase 1 | Pending |
| SCAF-04 | Phase 1 | Pending |
| MODL-01 | Phase 1 | Pending |
| MODL-02 | Phase 1 | Pending |
| MODL-03 | Phase 1 | Pending |
| PRMT-01 | Phase 1 | Pending |
| PRMT-02 | Phase 1 | Pending |
| PRMT-03 | Phase 1 | Pending |
| GEN-01 | Phase 1 | Pending |
| GEN-02 | Phase 1 | Pending |
| GEN-03 | Phase 1 | Pending |
| GEN-04 | Phase 1 | Pending |
| VALD-01 | Phase 1 | Pending |
| VALD-02 | Phase 1 | Pending |
| VALD-03 | Phase 1 | Pending |
| VALD-04 | Phase 1 | Pending |
| VALD-05 | Phase 1 | Pending |
| ERR-01 | Phase 1 | Pending |
| ERR-02 | Phase 1 | Pending |
| ERR-03 | Phase 1 | Pending |
| ERR-04 | Phase 1 | Pending |
| CLI-01 | Phase 1 | Pending |
| CLI-02 | Phase 1 | Pending |
| CLI-03 | Phase 1 | Pending |
| TEST-01 | Phase 1 | Pending |
| TEST-02 | Phase 1 | Pending |
| LOG-01 | Phase 2 | Pending |
| LOG-02 | Phase 2 | Pending |

**Coverage:**
- v1 requirements: 28 total
- Mapped to phases: 28
- Unmapped: 0 ✓

---
*Requirements defined: 2026-09-01*
*Last updated: 2026-09-01 after roadmap creation*
