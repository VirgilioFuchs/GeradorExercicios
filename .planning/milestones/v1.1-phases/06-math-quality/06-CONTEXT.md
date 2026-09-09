# Phase 6: Math Quality - Context

**Gathered:** 2026-09-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Entregar validação matemática **básica** (sem CAS completo): rejeitar inconsistências claras em aritmética e equações lineares `ax+b=c`; mensagem distinta da falha estrutural; falha matemática reutiliza o hook de regeneração da Phase 5 (`generate_validated_batch`). Casos não interpretáveis **não** falham o lote — registram-se para postmortem na falha final (insumo futuro para melhorar a LLM).

**In scope:** MATH-01, MATH-02 (via RELY).
**Out of scope:** CAS completo; frações/radicais/sistemas/inequações/geometria (exceto % simples se cair em aritmética); fine-tune/treino de modelo; prompt repair; failover de provider.

</domain>

<decisions>
## Implementation Decisions

### Escopo dos casos básicos (MATH-01)
- **D-01:** Casos básicos = **aritmética** + **equações lineares simples** (`ax + b = c`) — **Reversibility:** costly — define a superfície de checagem e fixtures da fase
- **D-02:** Se a checagem **não conseguir interpretar** enunciado/resposta: **não falha** o lote (passa); **registra** o caso para postmortem (melhoria futura da LLM). Inconsistência **clara** → rejeita como falha matemática
- **D-03:** Mensagem lista **todos** os exercícios matematicamente inconsistentes; o lote ainda falha (alinha report “all”)
- **D-04:** Estrito **moderado**: templates conhecidos + contradições óbvias; priorizar poucos falsos positivos

### Estratégia de checagem
- **D-05:** Estratégia **híbrida**: fixtures table-driven (regressão) + heurísticas para padrões abertos (aritmética / `ax+b=c`)
- **D-06:** Se research exigir biblioteca: escolher versão **estável**, **pinar** e **vendorar** no repo para o projeto funcionar mesmo se o pacote sumir do registry — **Reversibility:** costly — vendor vira artefato de build/repo
- **D-07:** Onde vive o código: **conforme a arquitetura existente** — checagem no caminho único de `validate_exercise_batch` / hook Phase 5; **sem** segundo loop de retry (planner escolhe módulo vs extensão de `validator.py`)
- **D-08:** Postmortem gerado **somente na falha final** do lote (não em sucesso)
- **D-09:** Preferir **stdlib**; lib só se research mostrar que equações lineares não fecham sem ela (aí aplica D-06)

### Mensagem de erro matemática (MATH-02 UX)
- **D-10:** Dois canais: stderr `[MATH]` detalhado com **prefixo + índice**; ao final **raise PT curto** ao usuário
- **D-11:** Raise = mensagem **mínima**; detalhes (índice, tipo de checagem, esperado vs obtido, etc.) no **postmortem/log**
- **D-12:** Raise **truncado**; conteúdo completo só no postmortem/log — sem segredos (LOG-02)
- **D-13:** Após esgotar regenerações: prefixo **`após N regenerações:`** + motivo math (respeita D-13 Phase 5: erro só no esgotamento)

### Tipos de exercício cobertos
- **D-14:** Aritmética MVP: operações `+ − × ÷` com **inteiros e decimais simples**
- **D-15:** Equações MVP: **somente** `ax + b = c` com `a,b,c` inteiros e `a ≠ 0`
- **D-16:** Explicitamente fora: frações, radicais, sistemas, inequações, geometria; **porcentagem simples pode** se reduzir a aritmética
- **D-17:** Testes sem LLM: **fixtures mínimas** nomeadas agora; geradores property-style **deferred**

### Discretion
- Nome/local exato do módulo math vs extensão de `validator.py` (desde que D-07)
- Formato concreto do arquivo/conteúdo do postmortem (jsonl vs txt) — desde que só na falha final (D-08) e sem segredos
- Heurísticas de parse (regex/`ast`/etc.) — research/planner

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap / requirements
- `.planning/ROADMAP.md` — Phase 6 goal e success criteria (MATH-01, MATH-02)
- `.planning/REQUIREMENTS.md` — MATH-01, MATH-02; Out of Scope: CAS completo
- `.planning/PROJECT.md` — Constraints: validação obrigatória; retries limitados; YAGNI; testabilidade sem API

### Prior phase context
- `.planning/phases/05-reliability-error-edges/05-CONTEXT.md` — D-05/D-07 hook `generate_validated_batch`; D-10 mesmo prompt; D-13 erro só no esgotamento; math via `ValueError` / `retriable`
- `.planning/phases/04-cli-argparse/04-CONTEXT.md` — dual-output; `run(request)`

### Code
- `exercise-ai/validator.py` — validação estrutural atual; ponto natural de extensão
- `exercise-ai/reliability.py` — `generate_validated_batch` (Phase 6 hook)
- `exercise-ai/models.py` — `Exercise` / `ExerciseBatch`
- `exercise-ai/tests/test_validator.py` — padrão de testes sem LLM

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `validate_exercise_batch`: já agrega erros estruturais e levanta `ValueError` — math deve entrar no mesmo contrato para RELY regenerar
- `VALIDATION_REPORT_MODE = "all"`: alinha com D-03 (reportar todos)
- `generate_validated_batch`: já regenera em `ValueError` de validação

### Established Patterns
- Mensagens PT no raise; detalhe técnico sanitizado em stderr (`[VALIDAÇÃO]`, `[API:*]`)
- Testes unitários com fixtures/`make_exercise` sem chamadas LLM

### Integration Points
- Após checks estruturais (ou módulo chamado por eles) → checks math → raise mínimo + log/postmortem na falha final
- Não alterar o loop de retry em `reliability.py` além do necessário para prefixo `após N regenerações` (D-13)

</code_context>

<specifics>
## Specific Ideas

- Postmortem existe para **procurar soluções e treinar/melhorar a LLM** depois — nesta fase só o artefato de diagnóstico na falha final, não o pipeline de treino
- Mistura “passar se não interpretar” + “registrar para postmortem” é intencional (D-02)

</specifics>

<deferred>
## Deferred Ideas

- Pipeline de fine-tune / treino LLM a partir do postmortem
- Geradores property-style de casos `ax+b=c` nos testes
- Frações, radicais, sistemas, inequações, geometria; CAS completo
- Prompt repair com feedback do erro math ao modelo

</deferred>

---

*Phase: 6-Math Quality*
*Context gathered: 2026-09-08*
