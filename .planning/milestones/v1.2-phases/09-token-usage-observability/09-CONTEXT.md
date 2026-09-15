# Phase 9: Token Usage Observability - Context

**Gathered:** 2026-09-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver quantitative LLM token/cost observability for the exercise generator lab: in-memory accumulation of per-request usage records during a CLI run, stderr visibility (input/output tokens, totals, duration, USD), and end-of-run flush to **day-partitioned NDJSON** under `exercise-ai/token-usage/`, with **separate files per provider**. Cover success, RELY attempts, and errors. No live LLM in tests. Does **not** implement failover (Phase 8) or product embed/storytelling (SEED-003).

</domain>

<decisions>
## Implementation Decisions

### Persistência / layout
- **D-01:** Formato = **NDJSON** (uma linha JSON por evento), **append** — nunca substituir histórico do dia. — **Reversibility:** costly — muda contrato de arquivos já gravados no lab.
- **D-02:** Partição por **dia civil** no filesystem: pasta `exercise-ai/token-usage/{YYYY-MM-DD}/`. Data = **fuso local da máquina** do operator (documentar no README).
- **D-03:** **Providers separados**: um arquivo NDJSON por provider no dia, ex. `openai.ndjson`, `gemini.ndjson`, `grok.ndjson` (só cria/abre o do provider usado).
- **D-04:** Flush em disco **apenas no final da run** (sucesso ou falha do pipeline). Acúmulo em memória durante a run; se o processo crashar mid-run, dados da run atual podem se perder (aceitável no lab MVP desta fase).

### Módulo / pasta
- **D-05:** Pacote/módulo sob `exercise-ai/token_usage/` (código Python com underscore) + diretório de dados `exercise-ai/token-usage/` (hífen, só artefatos). Código nunca mistura lógica de pricing/flush dentro de `validator`/`math_check`.
- **D-06:** Adicionar `exercise-ai/token-usage/` (conteúdo gerado) ao `.gitignore`, no mesmo espírito de `math_postmortem.jsonl`. Manter pasta rastreável via `.gitkeep` ou README curto se útil.

### Stderr / campos visíveis
- **D-07:** Stderr por evento relevante (e resumo no fim): **entrada** (prompt/input tokens), **saída** (completion/output tokens), **consumo final** (total da request e/ou da run), **tempo de execução** (ms da request e aggregate já existente `total_ms`/`chamadas`), **preço** (USD quando calculável). Tag sugerida `[USAGE]` — sem secrets, sem corpo de prompt/resposta.
- **D-08:** “Entrada/saída” = **contagens de tokens**, não texto de prompt/completion (LOG-02 / anti-leakage).

### Usage ausente
- **D-09:** Se o provider não expuser usage (ou campo faltar): gravar e exibir literal **`indisponível`** (string PT) — **não** inventar `0`. Mesmo para USD quando não houver taxa/custo.

### Providers
- **D-10:** Nesta fase: **OpenAI, Gemini e Grok** — mesmo schema de evento; extratores específicos por SDK; arquivos NDJSON separados (D-03).
- **D-11:** Extrair usage das respostas reais quando existirem:
  - OpenAI / Grok (OpenAI-compatible): `completion.usage` → `prompt_tokens`, `completion_tokens`, `total_tokens` [CITED: OpenAI chat completion usage].
  - Grok USD: preferir `usage.cost_in_usd_ticks / 1e10` quando presente [CITED: docs.x.ai cost tracking].
  - Gemini: `response.usage_metadata` → `prompt_token_count`, `candidates_token_count`, `total_token_count` [CITED: google-genai usage_metadata].

### Tentativas / erros / sucessos
- **D-12:** Registrar **tentativas RELY, erros e sucessos** como eventos distintos (`status`: `success` | `error` | `attempt` — nomes finais no plan). Incluir motivo curto tipado (classe/mensagem PT já usada) **sem** bodies de API que possam embutir keys.
- **D-13:** Integrar no caminho `generate_validated_batch` / generators para cada chamada LLM (não só o resultado final validado).

### Tokens + USD
- **D-14:** Sempre persistir tokens (ou `indisponível`). Persistência USD:
  - Grok: custo da API (`cost_in_usd_ticks`) quando disponível.
  - OpenAI/Gemini: **tabela local de taxas** (USD / 1M tokens input+output) versionada no módulo `token_usage`, por `model` string; se modelo sem taxa → USD `indisponível`.
- **D-15:** Moeda = **USD** apenas. Sem FX. Sem billing live da conta OpenAI/Google Admin APIs nesta fase.

### the agent's Discretion (researched / locked for planner)
- **D-16:** Schema mínimo de linha NDJSON (campos; tipos no plan): `ts`, `provider`, `model`, `status`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `duration_ms`, `usd`, `usd_source` (`api`|`rate_table`|`indisponivel`), `error_kind` (opcional), `run_id` (uuid curto por invocação CLI).
- **D-17:** Taxas OpenAI/Gemini: valores iniciais documentados no código/README com comentário “aproximado / atualizar manualmente”; **não** scrape de pricing pages em runtime.
- **D-18:** Resumo de fim de run em stderr: totais por provider + USD da run (somando só valores numéricos; `indisponível` não entra na soma — indicar quantos eventos sem preço).
- **D-19:** Testes: mocks de `usage` / `usage_metadata` / ticks; assert NDJSON append; assert redaction; CI sem LLM e sem depender de arquivos locais de usage.
- **D-20:** KISS: um collector injetável (path override para testes), sem DB, sem dashboard, sem Phoenix.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Product / phase
- `.planning/ROADMAP.md` — Phase 9 goal + success criteria
- `.planning/REQUIREMENTS.md` — TOKEN-01, TOKEN-02, TOKEN-03
- `.planning/seeds/SEED-002-token-usage-json.md` — original operator intent
- `.planning/PROJECT.md` — constraints (YAGNI, no secrets in logs)

### Engineering rules
- `.cursor/rules/20-ai-engineering.mdc` — cost controls, logging, Context7/Serena/Semgrep
- `.cursor/rules/10-python.mdc` — KISS/YAGNI/DRY, pathlib, type hints
- `skills/python-ai-engineering/SKILL.md` — if present in workspace

### Code integration
- `exercise-ai/generator.py` — OpenAI/Grok parse path; attach usage from completion
- `exercise-ai/generator_gemini.py` — Gemini generate; `usage_metadata`
- `exercise-ai/reliability.py` — RELY loop + `total_ms`/`chamadas` aggregate (extend, don’t replace)
- `exercise-ai/main.py` — run lifecycle / flush hook
- `.gitignore` — mirror postmortem ignore pattern for token-usage data

### External docs (research already cited)
- OpenAI Chat Completions `usage.prompt_tokens|completion_tokens|total_tokens`
- Gemini `GenerateContentResponse.usage_metadata` token count fields
- xAI cost tracking: `cost_in_usd_ticks / 1e10` → USD

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `reliability.generate_validated_batch` — already counts `calls` and prints duration aggregate in `finally`
- `[API:*]` stderr mappers — pattern for sanitized provider tags
- Injectable `POSTMORTEM_PATH` pattern — reuse for `TOKEN_USAGE_DIR` / collector path in tests

### Established Patterns
- Dual output: stdout human + `--out` JSON exercises; stderr for ops
- No live LLM in pytest; mock clients
- Env keys never logged (`_redact_env_secrets`)

### Integration Points
- After each LLM round-trip in OpenAI/Grok/Gemini generators → record event
- End of `main.run` / reliability `finally` → flush NDJSON + print USAGE summary
- Do not block exercise `--out` JSON schema with usage fields (keep usage orthogonal)

</code_context>

<specifics>
## Specific Ideas

Operator (verbatim intent locked):
1. NDJSON append, separated by day
2. Write at end of run
3. `exercise-ai/token-usage/{date separation}`
4. Stderr: entrada/saída, consumo final, tempo, preço
5. Missing → `indisponível`
6. Separate providers
7. Register attempts, errors, and successes
8. Tokens **and** USD

</specifics>

<deferred>
## Deferred Ideas

- Live Admin Usage APIs / org billing dashboards
- Multi-currency / BRL conversion
- Streaming token deltas mid-request
- Automatic scrape of public pricing pages
- Shipping token metrics into Phase 8 failover decisioning
- SEED-003 host embed / images / storytelling
- Phoenix / full persistent observability platform (PROJECT deferred)

</deferred>

---

*Phase: 9-Token Usage Observability*
*Context gathered: 2026-09-11*
