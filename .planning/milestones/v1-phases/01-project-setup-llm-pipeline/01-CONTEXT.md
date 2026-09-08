# Phase 1: Project Setup & LLM Pipeline - Context

**Gathered:** 2026-09-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Estabelecer a estrutura modular do projeto Python e implementar o pipeline de geração LLM end-to-end: entrada com parâmetros (matéria, tópico, dificuldade, quantidade) → prompt estruturado → chamada API → JSON tipado → saída CLI. Validação estrutural completa e testes ficam para a Fase 2; logging avançado para Fase 3.

**In scope:** SCAF-*, MODL-*, PRMT-*, GEN-*, CLI-* (16 requisitos)
**Out of scope nesta fase:** Validador dedicado com testes (Fase 2), retry automático, argparse, MySQL, agente
</domain>

<decisions>
## Implementation Decisions

### LLM Provider & Output Format
- **D-01:** Usar OpenAI API com Structured Outputs (`chat.completions.parse` + Pydantic) — **Reversibility:** costly — trocar provider exige refatorar `generator.py`
- **D-02:** Modelo padrão `gpt-4o-mini` (custo baixo, suporta schema strict) — **Reversibility:** reversible
- **D-03:** Variável de ambiente `LLM_API_KEY` via `python-dotenv` — **Reversibility:** reversible

[auto] LLM Provider — Q: "Which provider?" → Selected: "OpenAI with Structured Outputs" (recommended default)
[auto] Output format — Q: "Structured Outputs or prompt-only?" → Selected: "Structured Outputs" (recommended default)

### Data Models
- **D-04:** Pydantic v2 para `Exercise`, `ExerciseBatch`, `GenerationRequest` — **Reversibility:** costly — models são contrato central
- **D-05:** Campos em português no JSON de saída: `enunciado`, `resposta`, `explicacao`, `exercicios` — **Reversibility:** one-way — contrato público de saída
- **D-06:** `dificuldade` como enum: `facil`, `medio`, `dificil` — **Reversibility:** reversible

[auto] Model library — Q: "Pydantic, dataclass, or TypedDict?" → Selected: "Pydantic" (recommended default)

### Project Structure
- **D-07:** Código em diretório `exercise-ai/` na raiz do repositório conforme AGENT.md — **Reversibility:** reversible
- **D-08:** Arquivos: `main.py`, `generator.py`, `validator.py` (stub mínimo), `prompts.py`, `models.py`, `requirements.txt`, `.env.example`, `README.md` — **Reversibility:** reversible
- **D-09:** `validator.py` nesta fase pode ser pass-through ou validação mínima inline em `main.py`; validação completa é Fase 2 — **Reversibility:** reversible

[auto] Directory layout — Q: "Flat root or exercise-ai/ subfolder?" → Selected: "exercise-ai/ subfolder" (AGENT.md default)

### CLI & Input
- **D-10:** Entrada hardcoded/demonstração em `main.py` para MVP (exemplo do AGENT.md: equação 1º grau, fácil, quantidade 3) — **Reversibility:** reversible
- **D-11:** Saída: JSON impresso em stdout — **Reversibility:** reversible
- **D-12:** argparse fica para v2 (RELY/CLI-04) — **Reversibility:** reversible

[auto] Input method — Q: "CLI args or demo input?" → Selected: "Demo/hardcoded input" (MVP default per AGENT.md)

### Prompts
- **D-13:** Template centralizado em `prompts.py` com instruções em português — **Reversibility:** reversible
- **D-14:** Prompt exige quantidade exata, tópico restrito, somente JSON — **Reversibility:** reversible

### Error Handling (básico nesta fase)
- **D-15:** Tratar ausência de API key e erros de API no `generator.py`/`main.py` com mensagens claras — **Reversibility:** reversible
- **D-16:** Não silenciar exceções — **Reversibility:** reversible

### the agent's Discretion
- Escolha de timeout do cliente HTTP e mensagens de erro exatas
- Se `validator.py` faz pass-through ou checagem mínima de tipo até Fase 2

### Folded Todos
(none)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project specification
- `AGENT.md` — estrutura de arquivos, fluxo, regras de implementação, critério de pronto
- `.planning/PROJECT.md` — contexto, core value, constraints
- `.planning/REQUIREMENTS.md` — requisitos SCAF-*, MODL-*, PRMT-*, GEN-*, CLI-* da Fase 1
- `.planning/research/STACK.md` — stack recomendada (OpenAI + Pydantic)
- `.planning/research/ARCHITECTURE.md` — responsabilidades por módulo

### External
- OpenAI Structured Outputs — `response_format` com schema strict via Pydantic `.parse()`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Nenhum — projeto greenfield; apenas `AGENT.md` como spec

### Established Patterns
- Pipeline linear: entrada → prompt → LLM → JSON → (validação futura) → saída
- YAGNI: sem frameworks de agente

### Integration Points
- `main.py` orquestra `prompts` → `generator` → stdout
- `generator.py` depende de `models.py` e `prompts.py`

</code_context>

<specifics>
## Specific Ideas

- Exemplo de entrada do AGENT.md:
  ```json
  {"materia": "Matemática", "topico": "Equação do primeiro grau", "dificuldade": "facil", "quantidade": 3}
  ```
- Exemplo de saída esperada com `exercicios[]` contendo `enunciado`, `resposta`, `explicacao`
- Exercícios em português brasileiro

</specifics>

<deferred>
## Deferred Ideas

- Validação estrutural completa com testes → Fase 2
- Retry automático (1–2 tentativas) → v2 / Fase 2+
- argparse CLI → v2
- Validação matemática → milestone futuro
- MySQL, analytics, agente → roadmap v2+

</deferred>

---

*Phase: 1-Project Setup & LLM Pipeline*
*Context gathered: 2026-09-01*
