# Phase 2: Validation & Error Handling - Context

**Gathered:** 2026-09-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Garantir que apenas saídas estruturalmente válidas são aceitas, com erros claros e documentados. Expandir `validator.py` e tratamento de erros em `generator.py` / `main.py` para cumprir VALD-01–VALD-05 e ERR-01–ERR-04.

**In scope:** validação semântica pós-parse (quantidade, campos vazios, tipos), mensagens de falha específicas, erros de API/config unificados em português, logs detalhados com prefixos e dados brutos, labels de etapa em stderr.

**Out of scope nesta fase:** retry automático (RELY-*), failover entre APIs, barra de progresso com %, microserviços/escala, argparse CLI, testes pytest (Fase 3), logging estruturado persistente (LOG-* Fase 3).
</domain>

<decisions>
## Implementation Decisions

### Profundidade da validação
- **D-01:** Validar no objeto `ExerciseBatch` já parseado pelo Pydantic/Structured Outputs; regras semânticas (quantidade, campos, lista) em `validator.py` — **Reversibility:** costly — contrato central de validação
- **D-02:** Quantidade exata: `len(exercicios)` deve igualar `request.quantidade` (VALD-03)
- **D-03:** Campos `enunciado`, `resposta`, `explicacao` com `.strip()` — string só-whitespace conta como vazio (VALD-04)
- **D-04:** Em falha de validação, registrar JSON bruto no stderr junto à mensagem (camada de log detalhado para documentação/debug)

### Formato das mensagens de erro
- **D-05:** Mensagem ao usuário em stderr = texto direto em português, sem prefixos; camada de log detalhado adiciona prefixos (`[VALIDAÇÃO]`, `[API]`, etc.) e dados brutos
- **D-06:** Mensagens de validação indicam caminho do campo (ex.: `exercicios[1].resposta`) — VALD-05
- **D-07:** Incluir valores esperado vs recebido quando aplicável (ex.: "esperado 3 exercícios, recebido 2")
- **D-08:** Modo de reporte configurável por **constante no código** (não env var nesta fase): listar todos os erros de validação OU parar no primeiro exercício com falha — usuário escolhe via constante editável no fonte

### Erros de API (OpenAI + Gemini)
- **D-09:** Mensagem ao usuário: unificada em PT, só o necessário; logs distinguem provedor (OpenAI/Gemini) e incluem detalhes técnicos
- **D-10:** Ausência de chave: mensagem orienta sobre `GEMINI_API_KEY` e `LLM_API_KEY` no `.env` (ERR-01)
- **D-11:** Mapear tipos distintos: timeout, rate limit, erro de conexão, autenticação — mensagens específicas (ERR-02)
- **D-12:** Resposta vazia ou não parseável da API → `RuntimeError` com mensagem clara + log detalhado (ERR-03)

### Comportamento ao falhar
- **D-13:** Abortar imediatamente em falha de validação ou API — stderr + exit code 1; sem retry nesta fase
- **D-14:** Em sucesso, stdout contém **apenas** JSON UTF-8 formatado (`ensure_ascii=False`) — sem logs misturados
- **D-15:** Labels simples de etapa em stderr durante execução (ex.: "Gerando…", "Validando…") — alternativa leve à barra de progresso; sem percentual nesta fase

### the agent's Discretion
- Implementação interna de helpers de log (função única vs módulo `logging` leve) desde que respeite D-05/D-09 (duas camadas: usuário vs log detalhado)
- Estrutura exata da constante de modo de reporte (nome, localização em `validator.py` ou `config.py` interno)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — VALD-01–VALD-05, ERR-01–ERR-04
- `.planning/ROADMAP.md` — Phase 2 success criteria

### Prior phase context
- `.planning/phases/01-project-setup-llm-pipeline/01-CONTEXT.md` — decisões de pipeline, Pydantic, stderr
- `.planning/phases/01-project-setup-llm-pipeline/01-LEARNINGS.md` — padrões error boundary, validador stub

### Project spec
- `AGENT.md` — tratamento de erro esperado, variáveis de ambiente, formato JSON

### Code to extend
- `exercise-ai/validator.py` — expandir validação semântica
- `exercise-ai/main.py` — orquestração, labels de etapa, stdout/stderr
- `exercise-ai/generator.py` — erros de API OpenAI, dispatch multi-provedor
- `exercise-ai/generator_gemini.py` — erros de API Gemini
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `validate_exercise_batch()` em `validator.py` — stub com type-check e lista não vazia; expandir in-place
- Error boundary em `main.py` — `ValueError` / `RuntimeError` / genérico → stderr + exit 1
- `_resolve_provider()` em `generator.py` — já detecta chaves OpenAI/Gemini
- `json.dumps(..., ensure_ascii=False)` — UTF-8 na saída já implementado

### Established Patterns
- Erros de config/validação → `ValueError`; erros de execução/API → `RuntimeError`
- Mensagens em português em `stderr`; pipeline linear sem retry
- Pydantic v2 como fonte de verdade do schema após parse do LLM

### Integration Points
- `main.run_demo()` chama `generate_exercises` → `validate_exercise_batch` — inserir labels de etapa entre chamadas
- Validador recebe `(batch, request)` — request traz `quantidade` para VALD-03
- Geradores devem propagar erros mapeados antes do validador rodar
</code_context>

<specifics>
## Specific Ideas

- "Tudo que o usuário fizer tem que ser documentado" — priorizar logs detalhados com JSON bruto e prefixos na camada de log, mantendo mensagem principal legível
- Saída final formatada UTF-8 para o usuário em caso de sucesso
- Preferência por constante no código (não env var) para alternar modo de listagem de erros de validação

</specifics>

<deferred>
## Deferred Ideas

- **Microserviços / arquitetura escalável** para volume de exercícios — milestone v2+
- **Barra de progresso com percentual** por etapa do pipeline — nova capacidade de UX; labels simples em stderr cobrem MVP desta fase
- **Não encerrar até entregar todas as atividades** — implica retry/persistência (RELY-01/02, v2)
- **API reserva / failover automático** entre provedores sem gastar tokens à toa — v2; Fase 2 só reporta erros claramente
- **Retry em falha de validação ou API** — RELY-* fora do escopo MVP

</deferred>

---

*Phase: 02-validation-error-handling*
*Context gathered: 2026-09-02*
