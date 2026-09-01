# Gerador de Exercícios com IA

## What This Is

Uma aplicação Python simples que gera exercícios de matemática via LLM, recebendo parâmetros (matéria, tópico, dificuldade, quantidade) e retornando JSON estruturado com enunciado, resposta e explicação para cada exercício. O projeto é um laboratório incremental para estudar chamadas a LLM, prompt engineering, structured output, validação e confiabilidade — sem frameworks de agentes na primeira versão.

## Core Value

O usuário consegue gerar exercícios de matemática confiáveis e estruturados a partir de parâmetros simples, com validação que garante formato correto antes de usar o resultado.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Gerar exercícios de matemática via LLM com entrada: matéria, tópico, dificuldade, quantidade
- [ ] Retornar JSON estruturado com enunciado, resposta e explicação por exercício
- [ ] Validar estrutura da resposta (JSON válido, campos obrigatórios, quantidade correta)
- [ ] Separar responsabilidades: geração, prompts, modelos, validação
- [ ] Tratar erros de API, rede, timeout, rate limit e respostas inválidas
- [ ] Configurar chave de API via variável de ambiente (nunca hardcoded)
- [ ] Testes unitários do validador (sem chamadas reais ao LLM)
- [ ] Logs simples de desenvolvimento (sem segredos)

### Out of Scope

- LangChain, CrewAI, AutoGen e frameworks multiagente — complexidade desnecessária no MVP
- RAG, banco vetorial, filas, microsserviços — YAGNI para v1
- MySQL e persistência — etapa futura (v2+)
- Análise de desempenho do aluno — etapa futura
- Agente com ciclo de decisão e ferramentas — somente após etapas anteriores
- Validação matemática profunda — preparar estrutura, implementar depois

## Context

O projeto nasce como implementação didática de IA aplicada à educação. A arquitetura inicial segue um pipeline linear:

```
Entrada do usuário → Prompt estruturado → LLM → JSON estruturado → Validação → Exercícios
```

A evolução planejada (após MVP): validação matemática → MySQL (alunos, exercícios, notas) → análise de desempenho → personalização → agente com loop de decisão.

O documento `AGENT.md` na raiz define regras de implementação, estrutura de arquivos sugerida e critérios de pronto.

## Constraints

- **Tech stack**: Python, sem frameworks de agentes no MVP
- **Simplicidade**: YAGNI — cada arquivo com responsabilidade única
- **Segurança**: API keys em `.env`, nunca no código ou logs
- **Confiabilidade**: LLM não é fonte de verdade; validação estrutural obrigatória
- **Retries**: Máximo 1–2 tentativas de regeneração; sem loop infinito
- **Testabilidade**: Validador testável sem dependência de API externa

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pipeline simples (prompt → LLM → validação) sem agente | Entender fundamentos antes de abstrações; AGENT.md proíbe chamar v1 de "agente" | — Pending |
| Estrutura modular: main, generator, validator, prompts, models | Separação clara de responsabilidades; fácil evoluir | — Pending |
| Preferir Structured Outputs da API quando disponível | Reduz parsing frágil e texto fora do JSON | — Pending |
| dataclass/TypedDict/Pydantic — escolher o mais simples no MVP | Legibilidade didática sobre sofisticação | — Pending |
| Português nos exercícios; código e docs técnicos em inglês onde convencional | Alinhado ao público-alvo (educação em português) | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-09-01 after initialization*
