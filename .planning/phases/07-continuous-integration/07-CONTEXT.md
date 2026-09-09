# Phase 7: Continuous Integration - Context

**Gathered:** 2026-09-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Entregar **um** workflow GitHub Actions mínimo que, em push/PR, instala deps e roda a suíte pytest do `exercise-ai` **sem LLM live e sem secrets de API** — check verde/vermelho visível no PR (CI-01, CI-02).

**In scope:** CI-01, CI-02; arquivo(s) sob `.github/workflows/`; alinhar comando ao README; nota curta no README sobre CI.
**Out of scope:** Failover (Phase 8); lint/coverage/matrix multi-OS; packaging (poetry/uv); branch protection obrigatória via API; BNCC; MySQL; polish debt.

**Princípio do operador (esta discussão):** começar o mais básico possível neste lab pequeno; ver até onde chega; **não** copiar “CI de empresa / tendências”.

</domain>

<decisions>
## Implementation Decisions

### Filosofia (lab pequeno)
- **D-01:** CI = **um job**, um arquivo de workflow, o mínimo para regressão confiante — sem “plataforma de CI” — **Reversibility:** reversible
- **D-02:** Preferir o que o README **já documenta** (install + `pytest`) em vez de inventar tooling novo nesta fase
- **D-03:** Explicitamente **não** nesta fase: matrix de OS, matrix de várias Pythons, ruff/mypy gates, coverage %, Docker, tox, pre-commit no Actions, cache obrigatório, release/publish, concurrency fancy — **Reversibility:** reversible (podem entrar depois se doer)

### Triggers
- **D-04:** Disparar em **`push`** e **`pull_request`** na branch default **`master`** (remote HEAD atual do repo) — cobre PR aberto (#3) e pushes na linha principal
- **D-05:** Não expandir triggers para `workflow_dispatch` / tags / todas as branches nesta fase (YAGNI)

### Runtime / install / comando
- **D-06:** Runner **`ubuntu-latest`** apenas
- **D-07:** **Uma** versão Python: **`3.11`** (piso do PROJECT “3.11+”; estável no Actions; evita surpresa do 3.14 local no CI) — **Reversibility:** reversible — bump/matrix depois se precisar
- **D-08:** Install: `pip install -r exercise-ai/requirements.txt` (mesmo contrato do README)
- **D-09:** Teste canônico: **`pytest exercise-ai -q`** a partir da **raiz do checkout** (mesmo Phase 3 D-04 / README) — **Reversibility:** costly — regressão e docs apontam para este comando
- **D-10:** Não exigir `pyproject.toml` / packaging install nesta fase

### Secrets / LLM live (CI-01)
- **D-11:** Workflow **não** declara nem injeta `LLM_API_KEY`, `GEMINI_API_KEY`, nem outros secrets de LLM — **Reversibility:** costly — contrato de segurança CI-01
- **D-12:** Confiar na suite existente (mocks/dados estáticos; 73 tests collected localmente sem live LLM). Não adicionar job de “smoke live API”
- **D-13:** Opcional (discretion): `env:` vazio ou unset explícito das chaves se o planner quiser cinto-e-suspenders — não obrigatório se o job nunca as passa

### Check vermelho / “bloqueia merge” (CI-02)
- **D-14:** Sucesso = job passa; falha de pytest = job falha → check **vermelho** no PR (comportamento padrão do Actions)
- **D-15:** Nome do workflow/job **claro e estável** (ex. `CI` / `test`) para o operator reconhecer no PR
- **D-16:** **Não** automatizar branch protection / required checks via API nesta fase — repo pequeno; “bloqueia merge confiante” = status **visível** + operator pode marcar required check manualmente no GitHub se quiser — **Reversibility:** reversible
- **D-17:** README: uma linha apontando que push/PR rodam Actions; não precisa tutorial de branch protection

### Docs / superfície
- **D-18:** Atualizar README “Como testar” (ou seção curta CI) com o fato do workflow; manter comando local idêntico ao do job
- **D-19:** Não criar docs de “CI strategy” separados — YAGNI

### Claude's Discretion
- Nome exato do arquivo (`.github/workflows/ci.yml` vs `test.yml`) e `name:` do workflow
- Usar ou não `actions/setup-python` cache pip (nice-to-have; não requisito)
- `permissions: contents: read` mínimo se o planner achar útil
- Formatação YAML / `defaults.run.working-directory` vs paths absolutos a partir da raiz

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap / requirements
- `.planning/ROADMAP.md` — Phase 7 goal + success criteria 1–4
- `.planning/REQUIREMENTS.md` — CI-01, CI-02
- `.planning/PROJECT.md` — Python 3.11+, YAGNI, API keys nunca no código/logs; milestone v1.2 Ops & Resilience

### Prior phase context (tests / no live LLM)
- `.planning/milestones/v1-phases/03-tests-logging-docs/03-CONTEXT.md` — D-01–D-04 suite; D-04 comando `pytest exercise-ai -q`; D-10 CI adiado (agora Phase 7)
- `.planning/milestones/v1.1-phases/05-reliability-error-edges/05-CONTEXT.md` — D-17 sem secrets em logs (alinha CI)

### Code / docs
- `README.md` — Setup (`pip install -r exercise-ai/requirements.txt`), Como testar (`pytest exercise-ai -q`), env vars (não usar no CI)
- `exercise-ai/requirements.txt` — deps incluindo pytest
- `exercise-ai/tests/conftest.py` — path grounding; suite sem LLM live
- `exercise-ai/tests/` — cobertura atual (validator, generators, reliability, math, logging, main)

### Repo facts (scout)
- Default branch remota: **`master`**
- Sem `.github/` hoje — greenfield de workflow
- Sem `pyproject.toml` — install via requirements.txt

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Suite pytest em `exercise-ai/tests/` (~73 testes) — já roda sem LLM live
- `README.md` já documenta install + comando de teste — espelhar no workflow
- `exercise-ai/requirements.txt` — única fonte de deps para o job

### Established Patterns
- Testes usam mocks/`monkeypatch` e factories; não dependem de `.env` real
- Comando canônico desde Phase 3: `pytest exercise-ai -q` na raiz
- Segurança: nunca logar/expor `LLM_API_KEY` / `GEMINI_API_KEY`

### Integration Points
- Novo artefato: `.github/workflows/*.yml` (único ponto de integração com GitHub)
- Touch leve: `README.md` (mencionar CI)
- Sem mudanças no pipeline Python (`main` / generators / reliability) nesta fase

</code_context>

<specifics>
## Specific Ideas

- Operador pediu explicitamente: **sem tendências**; adaptar ao **projeto pequeno**; **começar básico** e ver até onde vai.
- Pesquisa das áreas cinzentas (resolvidas acima, não reabrir sem motivo):
  1. Triggers → só `master` push+PR
  2. Python → uma versão (3.11), sem matrix
  3. Install/comando → espelhar README
  4. Secrets → nenhum no job
  5. CI-02 → check visível; branch protection manual/opcional
  6. Extras “enterprise” → deferred

</specifics>

<deferred>
## Deferred Ideas

- Matrix Python 3.11/3.12/3.13 ou multi-OS — se CI começar a falhar por versão
- pip cache / concurrency groups — polish se o job ficar lento
- Ruff / typecheck / coverage gate — só se o lab pedir qualidade de estilo
- Required status checks via GitHub Rulesets — config de repo, não código desta fase
- `workflow_dispatch` / CI em todas as branches
- Provider failover — Phase 8
- BNCC (SEED-001), MySQL/analytics — fora de v1.2

</deferred>

---

*Phase: 7-Continuous Integration*
*Context gathered: 2026-09-09*
*Gray areas researched against repo + operator preference (basic lab CI); decisions locked for plan-phase*
