# Roadmap: Gerador de Exercícios com IA

**Created:** 2026-09-01
**Core Value:** Gerar exercícios de matemática confiáveis e estruturados com validação de formato
**Granularity:** Coarse (3 phases)
**Mode:** Vertical MVP slices

## Overview

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | Project Setup & LLM Pipeline | Estrutura modular e geração via LLM funcionando | SCAF-*, MODL-*, PRMT-*, GEN-*, CLI-* | 5 |
| 2 | Validation & Error Handling | Respostas validadas e erros tratados explicitamente | VALD-*, ERR-* | 4 |
| 3 | Tests, Logging & Docs | Qualidade verificável e projeto documentado | TEST-*, LOG-*, SCAF-04 | 4 |

**Total:** 3 phases | 28 v1 requirements | 100% coverage ✓

---

## Phase Details

### Phase 1: Project Setup & LLM Pipeline
**Goal:** Estabelecer estrutura do projeto e pipeline de geração LLM end-to-end com saída JSON
**Mode:** mvp
**Requirements:** SCAF-01, SCAF-02, SCAF-03, MODL-01, MODL-02, MODL-03, PRMT-01, PRMT-02, PRMT-03, GEN-01, GEN-02, GEN-03, GEN-04, CLI-01, CLI-02, CLI-03

**Success Criteria:**
1. Executar `python main.py` produz JSON com lista `exercicios` contendo enunciado, resposta e explicação
2. Módulos separados existem (`main`, `generator`, `prompts`, `models`) com responsabilidades distintas
3. Chave de API lida de `LLM_API_KEY` em `.env`; `.env.example` presente sem segredos
4. Prompt centralizado instrui tópico, dificuldade, quantidade e formato JSON exclusivo
5. Gerador usa SDK OpenAI com Structured Outputs ou parsing tipado equivalente

### Phase 2: Validation & Error Handling
**Goal:** Garantir que apenas saídas estruturalmente válidas são aceitas, com erros claros
**Mode:** mvp
**Requirements:** VALD-01, VALD-02, VALD-03, VALD-04, VALD-05, ERR-01, ERR-02, ERR-03, ERR-04

**Success Criteria:**
1. Validador rejeita JSON inválido, chave `exercicios` ausente, quantidade incorreta e campos vazios
2. Cada falha de validação retorna mensagem específica identificando o problema
3. Ausência de `LLM_API_KEY` produz erro claro antes da chamada à API
4. Erros de rede, timeout e rate limit são capturados e reportados sem silenciar exceções

### Phase 3: Tests, Logging & Docs
**Goal:** Cobertura de testes do validador, observabilidade básica e documentação de uso
**Mode:** mvp
**Requirements:** TEST-01, TEST-02, LOG-01, LOG-02, SCAF-04

**Success Criteria:**
1. `pytest` passa com casos: JSON válido, inválido, chave ausente, campo faltando, quantidade errada, lista vazia
2. Testes não fazem chamadas reais ao LLM (mocks ou dados estáticos)
3. Logs registram início, parâmetros (sem segredos), sucesso/falha e motivo de validação
4. `README.md` documenta setup, variáveis de ambiente e como executar o projeto

---

## Future Milestones (v2+)

Not in current roadmap — tracked in REQUIREMENTS.md v2 section:

- **Reliability:** Retry automático (RELY-01, RELY-02), argparse CLI (CLI-04)
- **Math Validation:** Verificação matemática de respostas (MATH-01)
- **Persistence:** MySQL para alunos e tentativas (DB-01)
- **Analytics:** Análise de desempenho por tópico (ANLY-01)
- **Personalization:** Contexto do histórico do aluno (PERS-01)
- **Agent:** Loop de decisão com ferramentas (AGNT-01)

---

## Phase Ordering Rationale

1. **Phase 1 first:** Core value requires working generation before validation polish
2. **Phase 2 second:** Validator depends on generator output format from Phase 1
3. **Phase 3 last:** Tests target validator; logging/doc wrap up quality gates

---
*Roadmap created: 2026-09-01*
