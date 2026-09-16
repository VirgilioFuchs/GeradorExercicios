# Phase 11: Service Layer Extraction - Context

**Gathered:** 2026-09-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Expor o gerador como biblioteca embutível in-process: `service.generate_batch(request) -> ExerciseBatch` (ou erro discriminável), sem `sys.exit` / print de exercício / arquivo de saída no caminho de biblioteca. `main.run()` vira adapter CLI (print, `--out`, fail logs, `sys.exit`); wizard `gerar` continua entrando por `main.run`. Inclui bound 1–40 no domínio, restauração de env, timeout Gemini, endurecimento de encoding cp1252, e documentação curta do contrato no README. Não inclui demo (Phase 12), packaging/rename, print→logging mecânico, nem alargamento do tipo de retorno.

</domain>

<decisions>
## Implementation Decisions

### Assinatura e retorno
- **D-01:** `generate_batch(request: GenerationRequest) -> ExerciseBatch` — **somente** `request` nesta fase. Sem kwargs `max_retries` / `provider` / `reasoning`. — **Reversibility:** costly — adicionar kwargs depois é compatível; alargar o *retorno* depois quebra o host
- **D-02:** Tipo de retorno permanece `ExerciseBatch` (não `GenerationResult` com usage). Uso/`run_id` ficam para próximo pass de harden (OBS-01). — **Reversibility:** one-way — alargar retorno após o host integrar é breaking change

### Contrato de erro
- **D-03:** Hierarquia por subclasses dos tipos já levantados: `ConfigError(ValueError)`, `InvalidRequestError(ValueError)`, `GenerationFailedError(RuntimeError)` (nomes finais a critério do planner, desde que preservem `except ValueError` / `except RuntimeError` do CLI e dos testes). — **Reversibility:** costly — vira API pública do host
- **D-04:** Atributos ricos nas exceptions para log detalhado (ex.: `kind`, e onde já existirem `retriable` / `api_error_kind` / provider / attempts). Mensagens humanas continuam em PT.
- **D-05:** Logging detalhado = atributos na exception + `logger` no **service e/ou adapter CLI**. Os ~33 `print(..., file=sys.stderr)` nos módulos internos **não** são convertidos nesta fase (débito LOG-01; host pode `redirect_stderr`).

### Side-effects de filesystem (agent discretion — necessário, sem atoa)
- **D-06:** No caminho do **service**: não escrever postmortem nem fail-error-log (permanecem responsabilidade do adapter CLI / `run()`).
- **D-07:** Flush de token usage permanece no lifecycle da fronteira (como hoje no `finally` de `run`), mas **sempre guardado** (`try/except OSError`) para nunca mascarar a exceção em voo. Sem flag/env nova nesta fase. — **Reversibility:** reversible

### Env e config
- **D-08:** Restaurar `LLM_PROVIDER` (e qualquer override de reasoning feito via env nesta chamada) com scoped save/restore em **toda** chamada — inclusive quando o failover muta o env sem o caller pedir. Sem objeto `Settings`.
- **D-09:** Bound `quantidade` `Field(ge=1, le=40)` (+ `topico` não-vazio) em `GenerationRequest`. Manter `_positive_quantidade` no argparse (exit 2 + mensagem PT) — não deletar. — **Reversibility:** reversible

### Encoding e timeout
- **D-10:** Endurecer encoding Windows (cp1252): diagnósticos ASCII-safe onde setas/glifos quebram (`→` → `->`); streams CLI `reconfigure(encoding="utf-8", errors="replace")` onde aplicável; evitar dump de lote com math glyphs para streams cp1252 no caminho que dispara regeneração paga.
- **D-11:** Client Gemini com timeout HTTP finito (alinhar ordem de grandeza ao OpenAI `30s`); documentar pior caso curto para o host no README.

### Documentação (EMBED-07)
- **D-12:** Seção curta no **README** (não arquivo CONTRACT.md separado): assinatura `generate_batch`, shape JSON do lote, tabela de erros (as três subclasses), lista de nomes de módulo reservados (detecção; packaging parkado), contrato sequencial (1 geração por vez / processo).

### Sequenciamento e regressão
- **D-13:** Primeiro commit/plano = *pure move* (`service.py` + `run()` delega; suite verde). Depois: env restore, subclasses de erro, encoding, timeout, README. Não misturar comportamento novo no move puro.
- **D-14:** Zero regressão CLI/wizard: wizard continua em `main.run`; ~25 testes de `SystemExit` em `run()` permanecem válidos; reapontar os 3 testes pinados a internals de `main` (incl. asserção de source-text `generate_with_failover`).
- **D-15:** `service.py` não importa `main` (evita `load_dotenv` / `sys.path` de import-time no host). Direção: `main → service → pipeline`.

### Agent Discretion
- Nomes exatos dos módulos/classes de erro e se `kind` ride junto como atributo string além da classe.
- Valor numérico exato do timeout Gemini e texto do “worst case” no README — confirmar contra SDK no plan-phase (research flag leve).
- Escopo mínimo do “name-collision self-check” (lista no README vs helper de aviso); packaging permanece parkado.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone / requirements
- `.planning/REQUIREMENTS.md` — EMBED-01..07 (v2.0)
- `.planning/ROADMAP.md` — Phase 11 goal, success criteria, notes (pure move first)
- `.planning/PROJECT.md` — Current Milestone v2.0; Out of Scope (Settings, packaging, concurrency)
- `.planning/research/SUMMARY.md` — cross-researcher resolutions (print deferral, return type, packaging park, encoding/Gemini in Phase 11)
- `.planning/research/ARCHITECTURE.md` — seam placement, import direction, build order
- `.planning/research/PITFALLS.md` — SystemExit, cp1252, env restore, finally-masking, flat-module collision
- `.planning/research/FEATURES.md` — TS-01..11 table stakes; AF anti-features
- `.planning/seeds/SEED-003-host-embed-images-storytelling.md` — Slice A only this phase

### Prior phase decisions (carry forward)
- `.planning/milestones/v1.2-phases/08-provider-failover/08-CONTEXT.md` — failover OpenAI↔Gemini only; env switch pattern (must restore now)
- `.planning/milestones/v1.2-phases/09-token-usage-observability/09-CONTEXT.md` — single flush site / collector lifecycle
- `.planning/milestones/v1.2-phases/10-interactive-cli-wizard/10-CONTEXT.md` — wizard enters via `main.run` (peer of CLI, not of service)

### Project rules
- `AGENT.md` / `AGENTS.md` — KISS/YAGNI, no agent frameworks
- `.cursor/rules/10-python.mdc` — SoC, no global mutable state abuse
- `.cursor/rules/20-ai-engineering.mdc` — provider/client/service boundaries; timeouts centralized

### Implementation touchpoints
- `exercise-ai/main.py` — `run()`, `sys.exit`, `load_dotenv` import-time, `_positive_quantidade`
- `exercise-ai/failover.py` — `_default_switch_provider` mutates `LLM_PROVIDER`
- `exercise-ai/models.py` — `GenerationRequest.quantidade` currently `gt=0`
- `exercise-ai/generator_gemini.py` — client sem timeout
- `exercise-ai/token_usage/collector.py` — module-level collector + flush writes
- `exercise-ai/validator.py` — stderr dump on validation failure (encoding risk)
- `README.md` — destination for EMBED-07 contract section

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `GenerationRequest` / `Exercise` / `ExerciseBatch` (Pydantic) — public contract shape already exists
- `generate_with_failover` + `generate_validated_batch` — pipeline to call from service after lifecycle setup
- `resolve_max_retries` — stays reachable from CLI adapter; service uses env/default path only (no kwargs)
- `begin_run` / `flush_token_usage` — lifecycle hooks to own at the service boundary
- Existing `logging` setup in `main._configure_logging` — pattern for adapter; service uses namespaced logger + rich exception attrs

### Established Patterns
- Flat modules + `sys.path.insert` in `main`/conftest (packaging parked — service must not depend on importing `main`)
- Failures today: bare `ValueError` / `RuntimeError` + monkey-patched `retriable` / `api_error_kind`
- CLI owns presentation: stdout text, `--out` JSON, fail logs, `sys.exit(1)`
- Failover writes `os.environ["LLM_PROVIDER"]` without restore (Phase 8 D-07); Phase 11 must restore

### Integration Points
- New: `exercise-ai/service.py` with `generate_batch`
- Modify: `main.run()` delegates to service then prints/writes/exits
- Modify: config raise sites → subclasses; `models.py` bounds; `generator_gemini.py` timeout; ASCII-safe diagnostics
- Tests: re-point 3 main-internal pins; keep SystemExit assertions on `run()`
- Docs: README section for host contract

</code_context>

<specifics>
## Specific Ideas

- Operator: “quanto mais detalhado o log, melhor” → interpretado como atributos ricos + logger no service/adapter, **não** como conversão mecânica dos prints internos nesta fase.
- FS: “não quero algo atoa mas o necessário” → service sem postmortem/fail-log; flush NDJSON guardado.
- Assinatura mínima agora; kwargs só se o projeto evoluir.
- Doc no README (não arquivo separado).

</specifics>

<deferred>
## Deferred Ideas

- **PKG-01** — packaging `pyproject.toml` + rename `exercise_ai/` (lead do próximo milestone)
- **OBS-01** — usage/custo/`run_id` devolvidos junto com o lote
- **LOG-01** — print→logging nos ~33 sites
- **kwargs** `max_retries` / `provider` / `reasoning` em `generate_batch` — quando o projeto evoluir
- Phase 12 demo; SEED-003 B/C; SEED-005; SEED-006

</deferred>

---

*Phase: 11-Service Layer Extraction*
*Context gathered: 2026-09-16*
