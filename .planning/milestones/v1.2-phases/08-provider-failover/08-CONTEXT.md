# Phase 8: Provider Failover - Context

**Gathered:** 2026-09-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Se o provider primário falhar com erro de API elegível (indisponibilidade / timeout / rate / conexão / erro genérico de API), o sistema tenta automaticamente o outro do par **OpenAI ↔ Gemini**, reusando `generate_validated_batch` (sem inventar segundo loop math/RELY) e deixando claro no stderr qual provider foi tentado/usado — sem secrets. Testes só com mocks. Não implementa wizard (Phase 10), nem usa métricas de token para decidir failover.

</domain>

<decisions>
## Implementation Decisions

### Gatilho do failover
- **D-01:** Failover **só** em falhas de API do primário que hoje são “permanentes” para o RELY: timeout, connection, rate limit, e erro genérico de API / indisponibilidade. — **Reversibility:** reversible
- **D-02:** **Não** faz failover em: auth (chave inválida/ausente do primário), recusa do modelo, resposta inválida tipada (`retriable=True`), nem falha de validação/math (RELY/exhaustion). Auth = problema de config do operator, não de disponibilidade. — **Reversibility:** reversible
- **D-03:** Se a chave do secundário não existir, falha com mensagem PT clara (sem tentar “meio failover”). — **Reversibility:** reversible

### Primário e par
- **D-04:** Par de failover = **somente OpenAI ↔ Gemini** (FAILOVER-01). **Grok fora** da cadeia nesta fase (já adiado no quick Grok). — **Reversibility:** costly — mudar o par toca CLI, docs e testes
- **D-05:** Primário = `--provider` / `LLM_PROVIDER` se explícito `openai` ou `gemini`; senão a resolução atual de `_resolve_provider`. Secundário = o outro do par. — **Reversibility:** reversible
- **D-06:** Se o primário resolvido for **Grok**, Phase 8 **não** aplica failover (comportamento atual de um provider); documentar. — **Reversibility:** reversible

### Envelope vs RELY
- **D-07:** Envelope fino: chamar `generate_validated_batch` no primário; se a falha for elegível (D-01), logar failover, apontar provider secundário (env), e chamar **de novo** o mesmo `generate_validated_batch` com o **mesmo** `request` e `max_retries`. Sem loop aninhado novo — só reuso do caminho existente. — **Reversibility:** costly — contrato do envelope define a fase
- **D-08:** Falha de validação/math no primário **não** troca de provider (mesmo conteúdo, outro LLM não é o objetivo KISS desta fase). — **Reversibility:** reversible
- **D-09:** No máximo **uma** troca de provider por run CLI (primário → secundário). Se o secundário também falhar, propaga o erro (já com logs de ambos). — **Reversibility:** reversible

### CLI e logs
- **D-10:** `--provider openai|gemini` **não** desliga o failover — ainda pode cair para o outro do par (lab = resiliência). Grok / ausência de secundário: D-03/D-06. — **Reversibility:** reversible
- **D-11:** Stderr com tag clara, ex.: `[FAILOVER] openai → gemini (timeout)` (ou motivo curto do mapper), **sem** secrets / bodies. Logs também devem indicar provider usado na geração quando aplicável (alinhar a padrões `[API:…]` existentes). — **Reversibility:** reversible
- **D-12:** Testes offline com mocks/fakes cobrindo: failover em timeout/rate/conn; sem failover em auth/math; Grok sem failover; secundário sem key; sucesso no secundário escreve `--out` normalmente. — **Reversibility:** reversible

### Agent Discretion
- Onde encaixar o envelope (ex. `main.run` vs wrapper em `reliability`) fica para research/plan — desde que D-07..D-09 sejam respeitados.
- Texto exato da mensagem PT e naming do helper: planner/executor.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements / roadmap
- `.planning/REQUIREMENTS.md` — FAILOVER-01..03
- `.planning/ROADMAP.md` — Phase 8 goal + success criteria
- `.planning/PROJECT.md` — v1.2 failover bullet; constraints YAGNI / no agent frameworks

### Prior phase context (do not contradict)
- `.planning/phases/09-token-usage-observability/09-CONTEXT.md` — deferred: token metrics must not drive failover
- `.planning/quick/260911-fvq-add-grok-provider-for-exercise-generatio/260911-fvq-SUMMARY.md` — Grok shipped; Phase 8 wiring deferred

### Code (integration)
- `exercise-ai/generator.py` — `_resolve_provider`, permanent vs retriable API mappers
- `exercise-ai/generator_gemini.py` — Gemini mappers / `generate_exercises`
- `exercise-ai/reliability.py` — single `generate_validated_batch` RELY loop
- `exercise-ai/main.py` — CLI `--provider`, `run()` orchestration

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `generate_validated_batch` — caminho único de regen/math a reusar no secundário
- `_permanent_api_error` / `is_permanent_api_error` — base para classificar gatilho (D-01); auth precisa ser distinguida (D-02)
- `_resolve_provider` + `LLM_PROVIDER` / `--provider` — seleção de primário
- Tags `[API:openai|gemini|grok]` e redaction de keys — padrão de log sanitizado

### Established Patterns
- RELY: `retriable=True` só resposta inválida; auth/timeout/rate/conn = `retriable=False` (não regenera no mesmo provider)
- Failover é orthogonal: usa falhas “permanentes” de API (exceto auth) para trocar provider, não para reiniciar math loop
- Testes sem LLM live (mocks) — Phase 7 CI / lab rule

### Integration Points
- Envelope em torno de `generate_validated_batch` (preferência KISS) ou imediatamente em `main.run` antes/depois do call
- Troca via `os.environ["LLM_PROVIDER"]` (ou parâmetro injetável se o plan preferir testabilidade) apontando secundário
- Token usage (Phase 9) continua observando ambos providers se ambos forem chamados — sem usar usage para decidir

</code_context>

<specifics>
## Specific Ideas

Operator pediu decisões **KISS** alinhadas ao projeto atual (sem round longo de Q&A). Preferência implícita: lab simples, resiliência OpenAI↔Gemini, Grok fora do failover por enquanto.

</specifics>

<deferred>
## Deferred Ideas

- Cadeia / failover envolvendo **Grok** (3º provider)
- Failover também em falhas de math/validação (“outro modelo pode acertar”)
- Flag CLI `--no-failover` / trava estrita quando `--provider` é passado
- Usar métricas de token/custo para escolher secundário (explicitamente fora — Phase 9 CONTEXT)

</deferred>

---

*Phase: 8-Provider Failover*
*Context gathered: 2026-09-15*
