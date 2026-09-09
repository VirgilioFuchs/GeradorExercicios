# Phase 5: Reliability & Error Edges - Context

**Gathered:** 2026-09-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Entregar regeneração limitada após falhas retriáveis (validação estrutural e resposta LLM inválida/parse), log agregado de duração das chamadas LLM, e unificação dos edges WR-03/WR-04 (ERR-05) no mesmo caminho de erro tipado — sem failover de provider, sem validação matemática (Phase 6), sem reestruturação de prompt “repair”.

**In scope:** RELY-01, RELY-02, ERR-05 (fecha WR-03/WR-04); hook de regeneração reutilizável pela Phase 6 (MATH-02).
**Out of scope:** Math quality (Phase 6); provider failover; prompt repair/feedback ao modelo; BNCC; DB; agente; CI.

</domain>

<decisions>
## Implementation Decisions

### Limite e contagem (RELY-01)
- **D-01:** Default de regenerações via env `RELY_MAX_RETRIES`; override por CLI `--max-retries` — **Reversibility:** costly — vira contrato público CLI/README/.env.example
- **D-02:** Hierarquia **CLI > env > default**; se env ausente, default **`1`** regeneração
- **D-03:** Semântica do valor = **número de regenerações após a primeira tentativa** (não o total de chamadas LLM). Total LLM = `1 + N`
- **D-04:** Faixa válida **`0|1|2|3`** para CLI e env (`0` = fail-fast como v1 Phase 2). Amplia o teto textual do PROJECT “1–2” para permitir até **3** regenerações

### O que dispara regeneração
- **D-05:** Regenerar em: falha de **validação estrutural** (`ValueError` do validator) e **resposta LLM inválida/parse** (ex. empty `choices`, parsed None, unparseable após ERR-05)
- **D-06:** **Não** regenerar em erros “permanentes” de API: auth, timeout, rate-limit (e equivalentes mapeados)
- **D-07:** O loop desta fase é o **hook** que Phase 6 (math) deve reusar — falha matemática futura entra no mesmo caminho — **Reversibility:** costly — contrato entre fases 5 e 6

### Onde vive o loop
- **D-08:** Módulo dedicado (ex. `exercise-ai/reliability.py`); `main` apenas orquestra (chama o wrapper; argparse/`--out`/texto permanecem em `main`) — **Reversibility:** costly — novo módulo no boundary do pipeline
- **D-09:** Não colocar o loop em `generate_exercises` nem no `validator`

### Prompt na regeneração
- **D-10:** Em toda regeneração, usar o **mesmo prompt** da primeira tentativa — **não** alterar `prompts.py` nesta fase
- **D-11:** Prompt “repair” / apêndice com erro de validação → **deferred** para milestone futuro (se precisar)

### UX stderr / stdout / `--out`
- **D-12:** Stderr mostra o fluxo: `Gerando…` → `Validando…`; em regeneração: **`1ª Regeneração`**, **`2ª Regeneração`**, … (contagem a partir das regenerações, não da 1ª tentativa)
- **D-13:** Mensagem de **erro** (motivo da falha) só quando as tentativas/regenerações **esgotarem** — PT clara com o último motivo
- **D-14:** **Stdout** (texto D-15 Phase 4) e escrita **`--out`** somente no **sucesso final**
- **D-15:** LOG-01 de desenvolvimento pode continuar (sem segredos), sem substituir o contrato de UX acima

### Log de duração (RELY-02)
- **D-16:** Log **agregado no fim** (sucesso ou falha final): duração total + número de chamadas LLM (ex. `total_ms` / equivalente e `chamadas=N`) — sem obrigação de logar duração por chamada intermediária nesta fase
- **D-17:** Sem segredos no log (alinha LOG-02)

### ERR-05 / WR-03 / WR-04
- **D-18:** Empty OpenAI `choices` / parsed ausente / unparseable e falhas Gemini fora de `APIError` usam o **mesmo caminho tipado** (RuntimeError PT + detalhe `[API:openai|gemini]` sanitizado)
- **D-19:** Esses edges contam como **resposta inválida → retriáveis** (D-05); auth/timeout/rate-limit permanecem não retriáveis (D-06)
- **D-20:** Preferir helpers/mapper unificados + testes parametrizados cobrindo WR-03 e WR-04

### CLI / env surface (complemento)
- **D-21:** Documentar `RELY_MAX_RETRIES` e `--max-retries` no README e `.env.example` (nomes sem valores secretos)
- **D-22:** Preservar contrato Phase 4: dual-output texto + `--out`; não regressar para JSON-only stdout

### Discretion
- Nome exato do módulo (`reliability.py` vs `retry.py`) e formulação precisa das strings PT de regeneração/duração — planner/executor
- Unidade de duração (`ms` vs `s`) desde que agregada e sem segredos

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap / requirements
- `.planning/ROADMAP.md` — Phase 5 goal e success criteria (RELY-01, RELY-02, ERR-05)
- `.planning/REQUIREMENTS.md` — RELY-01, RELY-02, ERR-05; MATH-01/02 dependem do hook desta fase
- `.planning/PROJECT.md` — Constraints: retries limitados; validação obrigatória; YAGNI

### Prior phase context
- `.planning/phases/04-cli-argparse/04-CONTEXT.md` — D-14/D-15 dual-output; `run(request)`; sem mudança de prompt na Phase 4
- `.planning/milestones/v1-phases/02-validation-error-handling/02-REVIEW.md` — WR-03 (empty choices), WR-04 (Gemini non-APIError)
- `.planning/milestones/v1-phases/02-validation-error-handling/02-CONTEXT.md` — D-13 fail-fast (superseded for retriable paths by this phase)

### Code
- `exercise-ai/main.py` — `run`, argparse, dual-output
- `exercise-ai/generator.py` / `exercise-ai/generator_gemini.py` — generate + mappers
- `exercise-ai/validator.py` — `validate_exercise_batch`
- `exercise-ai/tests/test_main.py` / `test_generators.py` / `test_logging_security.py` — contratos a estender

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `main.run(request, out_path)` — ponto de orquestração; deve delegar ao módulo de reliability
- `generate_exercises` / `validate_exercise_batch` — chamadas internas do loop (sem retry embutido nelas)
- `map_openai_error` / `map_gemini_error` + LOG-02 redaction — base para ERR-05

### Established Patterns
- Erros de usuário: PT em stderr; exit 1
- Estágios: `Gerando…` / `Validando…` em stderr
- Testes com mocks; sem LLM live

### Integration Points
- Argparse: adicionar `--max-retries`
- dotenv / env: `RELY_MAX_RETRIES`
- Phase 6: falha math deve plugar no mesmo loop/module

</code_context>

<specifics>
## Specific Ideas

- Labels de regeneração exatamente no espírito: **`1ª Regeneração`**, **`2ª Regeneração`**, … (não “Tentativa N” genérico para a 1ª geração)
- Usuário **não** vê o texto do erro até esgotar regenerações; o fluxo de estágios permanece visível
- Prompt repair explicitamente adiado (“próximo milestone se precisar”)

</specifics>

<deferred>
## Deferred Ideas

- Estruturação de prompt / apêndice de erro / “repair prompt” na regeneração — milestone futuro
- Provider failover automático — já fora de v1.1
- Validação matemática — Phase 6 (reusa hook RELY)
- Duração por chamada intermediária — não exigida por D-16 nesta fase

</deferred>

---

*Phase: 5-Reliability & Error Edges*
*Context gathered: 2026-09-08*
