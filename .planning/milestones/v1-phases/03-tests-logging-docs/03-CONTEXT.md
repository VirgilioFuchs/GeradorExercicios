# Phase 3: Tests, Logging & Docs - Context

**Gathered:** 2026-09-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Entregar cobertura pytest do validador (e contratos adjacentes sem LLM real), logs de desenvolvimento sem segredos, e README de setup/execução — requisitos TEST-01, TEST-02, LOG-01, LOG-02, SCAF-04.

**In scope:** suite pytest durável; fixtures/factories estáticas; testes de VALD + ERR relevantes (incluindo anti-vazamento de chave); eventos de log início/params/sucesso/falha; redaction de segredos nos logs `[API:*]`; README com setup, env vars e como rodar.

**Out of scope nesta fase:** retry/failover (RELY-*), argparse CLI (CLI-04), Phoenix/Langfuse, GitHub Actions CI (opcional futuro), validação matemática (MATH-01), microserviços, UI.

</domain>

<decisions>
## Implementation Decisions

### Suite de testes
- **D-01:** Colocar testes em `exercise-ai/tests/` com `conftest.py` e `sys.path`/imports alinhados ao pacote local — **Reversibility:** reversible
- **D-02:** Preferir factories Pydantic em fixtures pytest (dados em código) + opcionalmente JSON estático em `exercise-ai/tests/fixtures/` só se ajudar legibilidade — **Reversibility:** reversible
- **D-03:** Cobertura mínima = casos TEST-02 (válido, inválido/estrutura, chave ausente, campo faltando/whitespace, quantidade errada, lista vazia) **mais** remediação EVAL-REVIEW: mappers OpenAI/Gemini parametrizados, stdout purity do `run_demo` com mocks, e teste anti-vazamento de API key em stderr — sem chamadas reais ao LLM — **Reversibility:** costly — forma a base de regressão do MVP
- **D-04:** Comando canônico: `pytest exercise-ai -q` (ou equivalente documentado no README) a partir da raiz do repo

### Logging
- **D-05:** Manter a camada de log detalhado existente (`[VALIDAÇÃO]`, `[API:openai|gemini]`) e adicionar eventos LOG-01 via `logging` stdlib (ou helper fino) em stderr: início da geração, parâmetros sem segredos, sucesso/falha, motivo de validação — **Reversibility:** reversible
- **D-06:** LOG-02 obrigatório: nunca logar valores de `LLM_API_KEY` / `GEMINI_API_KEY`; sanitizar `str(exc)` nos mappers (corrigir WR-01: logar tipo + status/code, não corpo bruto com chave) — **Reversibility:** costly — contrato de segurança do projeto
- **D-07:** Não introduzir arquivos de log persistentes nem Phoenix nesta fase (alinhado a deferral Phase 2)

### README / docs
- **D-08:** Criar `README.md` na **raiz** do repositório em português — **Reversibility:** reversible
- **D-09:** README cobre: o que é o projeto, setup (`pip install -r exercise-ai/requirements.txt`), variáveis `.env` (`LLM_API_KEY`, `GEMINI_API_KEY`, `LLM_PROVIDER`), como executar (`python exercise-ai/main.py`), como rodar testes (`pytest …`), nota de stdout JSON vs stderr

### CI
- **D-10:** Nesta fase **não** adicionar GitHub Actions — só documentar o comando pytest no README; CI fica deferred

### the agent's Discretion
- Nomes exatos dos arquivos de teste (`test_validator.py`, `test_generators.py`, …)
- Nível de detalhe do helper de logging (módulo `logging` vs função wrapper)
- Se incluir um exemplo mínimo de saída JSON no README
- Ordem das tasks no plano (tests → logging/redaction → README é a ordem natural sugerida)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — TEST-01, TEST-02, LOG-01, LOG-02, SCAF-04
- `.planning/ROADMAP.md` — Phase 3 success criteria

### Prior phase decisions & gaps
- `.planning/phases/02-validation-error-handling/02-CONTEXT.md` — D-01–D-15 (duas camadas stderr, fail-fast, report mode)
- `.planning/phases/02-validation-error-handling/02-LEARNINGS.md` — harness OpenAI, str(exc) leakage, verifies efêmeros
- `.planning/phases/02-validation-error-handling/02-EVAL-REVIEW.md` — remediação must-fix (dataset, pytest, secret leakage)
- `.planning/phases/02-validation-error-handling/02-REVIEW.md` — WR-01–WR-04 (redaction, empty choices, Gemini transport)
- `.planning/phases/02-validation-error-handling/02-01-PLAN.md` — asserts automatizados a promover para suite durável
- `.planning/phases/01-project-setup-llm-pipeline/01-LEARNINGS.md` — multi-path `.env`, estrutura `exercise-ai/`

### Project constraints
- `AGENTS.md` / `.planning/PROJECT.md` — sem agent frameworks; API keys nunca no código/logs
- `exercise-ai/requirements.txt` — já lista `pytest>=8.0.0`

### Code to extend
- `exercise-ai/validator.py` — alvo principal TEST-*
- `exercise-ai/main.py` — eventos LOG-01 + stdout purity tests
- `exercise-ai/generator.py` / `generator_gemini.py` — mappers + redaction LOG-02

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `validate_exercise_batch(batch, request)` — contrato semântico completo a cobrir com pytest
- `map_openai_error` / `map_gemini_error` — helpers testáveis sem rede
- `main.run_demo` — mockável para stdout/stderr/exit
- Plan Task 1/2 verify scripts (efêmeros) — blueprint dos asserts a commitarem

### Established Patterns
- Erros config/validação → `ValueError`; API → `RuntimeError`
- Mensagens PT; `print(str(err))` sem wrappers no main
- Prefixo detalhado `[VALIDAÇÃO]` / `[API:…]` em stderr
- Imports via `sys.path` + diretório `exercise-ai/`

### Integration Points
- Suite deve importar módulos como nos verifies Phase 2 (`sys.path.insert(0, 'exercise-ai')` ou package layout equivalente)
- Redaction altera `generator.py` / `generator_gemini.py` no caminho de log, não a mensagem PT ao usuário
- README na raiz referencia `exercise-ai/` como app

</code_context>

<specifics>
## Specific Ideas

- Usuário delegou todas as gray areas ao padrão recomendado do agente (sem discussão interativa)
- Incorporar remediação EVAL-REVIEW (secret leakage + fixtures + suite) como parte de TEST/LOG desta fase, sem expandir para CI/Phoenix

</specifics>

<deferred>
## Deferred Ideas

- GitHub Actions / CI pipeline (`pytest` em PR)
- Phoenix / Langfuse / structured log files (LOG-* avançado)
- Retry automático e failover (RELY-*, v2)
- argparse CLI (CLI-04)
- Validação matemática (MATH-01)
- Fix WR-03/WR-04 (empty choices / Gemini transport) — nice-to-have se couber sem estourar escopo; senão backlog pós-MVP

</deferred>

---

*Phase: 3-Tests, Logging & Docs*
*Context gathered: 2026-09-04*
