# Phase 7: Continuous Integration - Research

**Researched:** 2026-09-11
**Domain:** Minimal GitHub Actions CI for offline pytest (no LLM secrets)
**Confidence:** HIGH

## Summary

Phase 7 is a greenfield GitHub Actions workflow: one job on `ubuntu-latest`, Python 3.11, `pip install -r exercise-ai/requirements.txt`, then `pytest exercise-ai -q` from the repo root on `push`/`pull_request` to `master`. No matrix, lint, coverage, Docker, or branch-protection API. The existing suite already collects **73 tests** without live LLM; CI must not declare `LLM_API_KEY` / `GEMINI_API_KEY`.

Official Actions docs and action READMEs prescribe `actions/checkout` + `actions/setup-python` + pip + pytest. Latest majors verified from GitHub Releases: **checkout v7**, **setup-python v7** (published 2026-07-20). Some Context7-indexed GitHub tutorials still show older majors (`checkout@v6`, `setup-python@v5`) — prefer the action repo majors for this plan.

**Primary recommendation:** Add `.github/workflows/ci.yml` with `name: CI`, job `test`, `permissions: contents: read`, pin `actions/checkout@v7` + `actions/setup-python@v7` (`python-version: '3.11'`), install from `exercise-ai/requirements.txt`, run `pytest exercise-ai -q` at checkout root, omit all LLM secrets; add one README line under “Como testar”.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Filosofia (lab pequeno)
- **D-01:** CI = **um job**, um arquivo de workflow, o mínimo para regressão confiante — sem “plataforma de CI” — **Reversibility:** reversible
- **D-02:** Preferir o que o README **já documenta** (install + `pytest`) em vez de inventar tooling novo nesta fase
- **D-03:** Explicitamente **não** nesta fase: matrix de OS, matrix de várias Pythons, ruff/mypy gates, coverage %, Docker, tox, pre-commit no Actions, cache obrigatório, release/publish, concurrency fancy — **Reversibility:** reversible (podem entrar depois se doer)

#### Triggers
- **D-04:** Disparar em **`push`** e **`pull_request`** na branch default **`master`** (remote HEAD atual do repo) — cobre PR aberto (#3) e pushes na linha principal
- **D-05:** Não expandir triggers para `workflow_dispatch` / tags / todas as branches nesta fase (YAGNI)

#### Runtime / install / comando
- **D-06:** Runner **`ubuntu-latest`** apenas
- **D-07:** **Uma** versão Python: **`3.11`** (piso do PROJECT “3.11+”; estável no Actions; evita surpresa do 3.14 local no CI) — **Reversibility:** reversible — bump/matrix depois se precisar
- **D-08:** Install: `pip install -r exercise-ai/requirements.txt` (mesmo contrato do README)
- **D-09:** Teste canônico: **`pytest exercise-ai -q`** a partir da **raiz do checkout** (mesmo Phase 3 D-04 / README) — **Reversibility:** costly — regressão e docs apontam para este comando
- **D-10:** Não exigir `pyproject.toml` / packaging install nesta fase

#### Secrets / LLM live (CI-01)
- **D-11:** Workflow **não** declara nem injeta `LLM_API_KEY`, `GEMINI_API_KEY`, nem outros secrets de LLM — **Reversibility:** costly — contrato de segurança CI-01
- **D-12:** Confiar na suite existente (mocks/dados estáticos; 73 tests collected localmente sem live LLM). Não adicionar job de “smoke live API”
- **D-13:** Opcional (discretion): `env:` vazio ou unset explícito das chaves se o planner quiser cinto-e-suspenders — não obrigatório se o job nunca as passa

#### Check vermelho / “bloqueia merge” (CI-02)
- **D-14:** Sucesso = job passa; falha de pytest = job falha → check **vermelho** no PR (comportamento padrão do Actions)
- **D-15:** Nome do workflow/job **claro e estável** (ex. `CI` / `test`) para o operator reconhecer no PR
- **D-16:** **Não** automatizar branch protection / required checks via API nesta fase — repo pequeno; “bloqueia merge confiante” = status **visível** + operator pode marcar required check manualmente no GitHub se quiser — **Reversibility:** reversible
- **D-17:** README: uma linha apontando que push/PR rodam Actions; não precisa tutorial de branch protection

#### Docs / superfície
- **D-18:** Atualizar README “Como testar” (ou seção curta CI) com o fato do workflow; manter comando local idêntico ao do job
- **D-19:** Não criar docs de “CI strategy” separados — YAGNI

### Claude's Discretion
- Nome exato do arquivo (`.github/workflows/ci.yml` vs `test.yml`) e `name:` do workflow
- Usar ou não `actions/setup-python` cache pip (nice-to-have; não requisito)
- `permissions: contents: read` mínimo se o planner achar útil
- Formatação YAML / `defaults.run.working-directory` vs paths absolutos a partir da raiz

### Deferred Ideas (OUT OF SCOPE)
- Matrix Python 3.11/3.12/3.13 ou multi-OS — se CI começar a falhar por versão
- pip cache / concurrency groups — polish se o job ficar lento
- Ruff / typecheck / coverage gate — só se o lab pedir qualidade de estilo
- Required status checks via GitHub Rulesets — config de repo, não código desta fase
- `workflow_dispatch` / CI em todas as branches
- Provider failover — Phase 8
- BNCC (SEED-001), MySQL/analytics — fora de v1.2
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CI-01 | Em push/PR no GitHub, Actions instala deps e roda `pytest` no pacote `exercise-ai` sem chamar LLM live (sem secrets de API no job) | Single-job workflow: checkout → setup-python 3.11 → `pip install -r exercise-ai/requirements.txt` → `pytest exercise-ai -q`; no `env`/`secrets` for LLM keys; suite is mock-based (73 collected) |
| CI-02 | Falha de testes deixa o check vermelho e bloqueia merge confiante (status visível no PR) | Default Actions status check on PR when job fails; stable `name: CI` / job `test`; no branch-protection API (D-16) — visibility is the deliverable |
</phase_requirements>

## Project Constraints (from .cursor/rules/)

From `10-python.mdc` + `20-ai-engineering.mdc` + `skills/python-ai-engineering/SKILL.md`:

| Directive | Implication for Phase 7 |
|-----------|-------------------------|
| YAGNI / KISS / smallest correct change | One workflow file, one job; mirror README; no new tooling |
| Never hardcode API secrets; keys via `.env` only | Workflow must not inject `LLM_API_KEY` / `GEMINI_API_KEY` |
| Prefer Context7 for SDK/framework APIs | Used for GitHub Actions / setup-python / checkout docs |
| Serena for non-trivial symbol/refactor work | Used to inspect `conftest.py` and secret/env patterns |
| Semgrep when changes involve secrets/env/network | Attempted for secret-handling surfaces; inform CI-01 threat model |
| Deterministic verification over LLM judgment | CI gate is pytest exit code |
| Fail Fast / explicit errors | Let pytest failure fail the job (no `continue-on-error`) |

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Trigger CI on push/PR to `master` | CDN / Static (GitHub platform) | — | Workflow YAML in repo; executed by GitHub Actions runners |
| Install Python deps + run pytest | API / Backend (CI runner as batch host) | — | Ephemeral `ubuntu-latest` VM; not app runtime |
| Offline test correctness (mocks) | API / Backend (`exercise-ai/tests`) | — | Existing suite; CI only invokes it |
| Secret non-injection (CI-01) | CDN / Static (workflow config) | API / Backend (app code) | Job YAML must omit secrets; app already redacts keys in logs |
| PR check visibility (CI-02) | CDN / Static (GitHub Checks UI) | — | Platform default; no app code |
| README CI note | CDN / Static (docs) | — | Operator discoverability |

## Standard Stack

### Core

| Library / Action | Version | Purpose | Why Standard |
|------------------|---------|---------|--------------|
| GitHub Actions workflow | YAML under `.github/workflows/` | CI orchestration | Native to GitHub; no third-party CI host [CITED: docs.github.com/en/actions] |
| `actions/checkout` | **v7** (latest release `v7.0.1`, 2026-07-20) | Clone repo into `$GITHUB_WORKSPACE` | Official checkout action; README uses `@v7` [VERIFIED: github.com/actions/checkout/releases/latest] |
| `actions/setup-python` | **v7** (latest release `v7.0.0`, 2026-07-20) | Install Python 3.11 on runner | Official setup action; README uses `@v7` [VERIFIED: github.com/actions/setup-python/releases/latest] |
| Python | **3.11** (pinned in workflow) | Runtime for tests | Locked D-07; PROJECT.md “3.11+” [VERIFIED: .planning/PROJECT.md Current State] |
| pip + `exercise-ai/requirements.txt` | as committed | Install openai, google-genai, pydantic, python-dotenv, pytest | Locked D-08; README Setup [VERIFIED: README.md:7-9] [VERIFIED: exercise-ai/requirements.txt:1-5] |
| pytest | `>=8.0.0` (via requirements.txt) | Test runner | Already in deps; README command [VERIFIED: exercise-ai/requirements.txt:5] [VERIFIED: README.md:59-65] |

### Supporting

| Library / Pattern | Version | Purpose | When to Use |
|-------------------|---------|---------|-------------|
| `permissions: contents: read` | workflow syntax | Least-privilege `GITHUB_TOKEN` | Recommended (discretion) [CITED: docs.github.com/en/actions — permissions] |
| `cache: pip` on setup-python | optional input | Speed installs | Discretion only; **not** required (D-03) [CITED: /actions/setup-python README] |
| `python -m pip install --upgrade pip` | optional step | Fresher pip on runner | Nice-to-have; GitHub Python tutorial often includes it [CITED: docs.github.com/en/actions/tutorials/build-and-test-code/python] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Single Python 3.11 job | Matrix 3.11–3.13 | Deferred (D-03); local is 3.14 — CI pin avoids 3.14 surprises |
| `actions/setup-python@v7` | `@v5` from older tutorials | Tutorials lag; releases show v7 current |
| Root `pytest exercise-ai -q` | `cd exercise-ai && pytest` | Breaks D-09 / README / Phase 3 contract |
| No secrets in job | Repo Actions secrets for LLM | Violates CI-01 / D-11 |
| Visible check only | Branch protection API | Out of scope D-16 |

**Installation (CI job steps — not a local npm/pip add):**

```bash
# On the Actions runner after checkout + setup-python 3.11:
python -m pip install --upgrade pip
pip install -r exercise-ai/requirements.txt
pytest exercise-ai -q
```

**Version verification:**
- `actions/checkout` latest: **v7.0.1** [VERIFIED: github.com/actions/checkout/releases/latest]
- `actions/setup-python` latest: **v7.0.0** [VERIFIED: github.com/actions/setup-python/releases/latest]
- No new PyPI packages introduced this phase (reuse `exercise-ai/requirements.txt`).

## Package Legitimacy Audit

> Phase installs **no new PyPI packages**. Runtime deps already declared. New artifacts are first-party workflow YAML + official GitHub-owned actions.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| actions/checkout | GitHub Actions Marketplace / org `actions` | years (v7.0.1 Jul 2026) | N/A (official) | github.com/actions/checkout | OK | Approved — pin `@v7` |
| actions/setup-python | GitHub Actions Marketplace / org `actions` | years (v7.0.0 Jul 2026) | N/A (official) | github.com/actions/setup-python | OK | Approved — pin `@v7` |
| (existing) pytest, pydantic, openai, google-genai, python-dotenv | PyPI via requirements.txt | pre-existing | N/A this phase | various | OK | No new install — already in repo |

**Packages removed due to [SLOP] verdict:** none  
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```text
[git push / pull_request → master]
            │
            ▼
┌───────────────────────────────┐
│ GitHub Actions (ubuntu-latest)│
│ workflow: CI / job: test      │
└───────────────┬───────────────┘
                │
        ┌───────┴────────┐
        ▼                ▼
 actions/checkout@v7   (no LLM secrets)
        │
        ▼
 actions/setup-python@v7  python-version: '3.11'
        │
        ▼
 pip install -r exercise-ai/requirements.txt
        │
        ▼
 pytest exercise-ai -q   ← cwd = $GITHUB_WORKSPACE (repo root)
        │
   ┌────┴────┐
   ▼         ▼
 exit 0    exit ≠0
 check ✓   check ✗ (PR red)
```

### Recommended Project Structure

```text
.github/
└── workflows/
    └── ci.yml          # sole CI artifact (discretion: ci.yml)
README.md               # one-line CI note under “Como testar”
exercise-ai/
├── requirements.txt    # unchanged install contract
└── tests/              # existing suite — unchanged this phase
```

### Pattern 1: Minimal Python pytest CI (locked decisions)

**What:** One job; checkout; setup Python 3.11; pip install requirements path; pytest from root.  
**When to use:** Always for this phase (locked D-01–D-09).  
**Example:**

```yaml
# Source: composed from Context7 /actions/setup-python + /actions/checkout @v7
# + locked CONTEXT D-04–D-09; branches: master (not main)
name: CI

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r exercise-ai/requirements.txt
      - name: Run tests
        run: pytest exercise-ai -q
```

### Pattern 2: Path grounding via conftest (why root pytest works)

**What:** `conftest.py` inserts `exercise-ai/` onto `sys.path` so imports resolve when pytest is invoked from repo root.  
**When to use:** Do not change for CI; do not `cd exercise-ai` unless changing D-09 (out of scope).

Verbatim from repo [VERIFIED: exercise-ai/tests/conftest.py:10-13]:

```python
_PACKAGE_DIR = Path(__file__).resolve().parents[1]
if str(_PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_DIR))
```

### Anti-Patterns to Avoid

- **`main` instead of `master`:** Remote HEAD is `master` [VERIFIED: `git remote show origin` → HEAD branch: master]. Wrong branch filter → CI never runs on PRs.
- **`working-directory: exercise-ai` + `pytest` without path:** Diverges from README/`pytest exercise-ai -q`.
- **Injecting `secrets.LLM_API_KEY`:** Violates CI-01 / D-11.
- **Matrix / coverage / ruff in this PR:** Deferred D-03.
- **`continue-on-error: true` on pytest:** Would leave CI-02 green on failure.
- **Relying on local Python 3.14 for CI:** Local probe showed 3.14.0; pin 3.11 in Actions (D-07).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Clone repo in CI | Custom git script | `actions/checkout@v7` | Handles PR refs, tokens, cleanup [CITED: /actions/checkout] |
| Install Python on runner | apt/pyenv DIY | `actions/setup-python@v7` | Versioned, cache-capable, maintained [CITED: /actions/setup-python] |
| CI host / dashboard | Jenkins/self-hosted | GitHub Actions | Repo already on GitHub; YAGNI |
| Force merge block via API | Scripts calling branch protection API | Visible check + optional manual required status | Locked D-16 |
| Live LLM smoke in CI | Second job with API keys | Existing mock suite | Locked D-12 |

**Key insight:** The hard problem (offline, trustworthy tests) is already solved in `exercise-ai/tests/`. CI only needs to invoke the documented command on a clean runner.

## Common Pitfalls

### Pitfall 1: Wrong default branch in `on:` filters
**What goes wrong:** Workflow never runs on PRs targeting `master`.  
**Why it happens:** Tutorials default to `main`.  
**How to avoid:** Use `branches: [master]` for both `push` and `pull_request` (D-04).  
**Warning signs:** PR shows no checks; Actions tab empty for PR events.

### Pitfall 2: Wrong working directory / pytest path
**What goes wrong:** `ModuleNotFoundError` or zero tests collected.  
**Why it happens:** `cd exercise-ai` without updating import grounding, or `pytest` with wrong path.  
**How to avoid:** Run `pytest exercise-ai -q` from `$GITHUB_WORKSPACE` root (D-09).  
**Warning signs:** Collection count ≠ 73; import errors for `models`.

### Pitfall 3: LLM secrets in workflow
**What goes wrong:** Keys exposed in logs/fork PRs; CI-01 fails intent.  
**Why it happens:** Copy-paste “real” deploy workflows with `env: API_KEY: ${{ secrets.* }}`.  
**How to avoid:** Omit `secrets` / LLM `env` entirely (D-11). Optional belt: do not set those vars.  
**Warning signs:** Workflow YAML contains `LLM_API_KEY` or `GEMINI_API_KEY`.

### Pitfall 4: Stale action majors from tutorials
**What goes wrong:** Plan pins `@v5`/`@v6` while `@v7` is current.  
**Why it happens:** Context7 GitHub site docs still show older examples alongside newer action READMEs.  
**How to avoid:** Prefer `actions/*/releases/latest` + action README (`@v7`).  
**Warning signs:** Mismatch between research table and GitHub “latest” tag.

### Pitfall 5: Assuming `.env` is required for pytest
**What goes wrong:** Unnecessary secret setup; or CI fails waiting for env files.  
**Why it happens:** `main.py` calls `load_dotenv` at import [VERIFIED: exercise-ai/main.py:19-23], but tests use mocks/`monkeypatch` and factories in conftest — suite runs without real keys (README “Como testar”).  
**How to avoid:** Do not commit `.env`; do not create secrets in Actions for tests.  
**Warning signs:** Job steps that copy `.env.example` with fake production keys.

### Pitfall 6: Interpreting “bloqueia merge” as requiring Rulesets API
**What goes wrong:** Scope creep into repo admin automation.  
**Why it happens:** CI-02 wording.  
**How to avoid:** Deliver red/green check; document optional manual required check (D-16/D-17).

## Code Examples

### Recommended workflow skeleton (discretion filled)

```yaml
# Source: Context7 /actions/checkout@v7 + /actions/setup-python@v7
# Locked: master, ubuntu-latest, 3.11, requirements path, pytest from root
name: CI

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - name: Set up Python
        uses: actions/setup-python@v7
        with:
          python-version: '3.11'
          # cache: 'pip'  # optional; not required (D-03)
          # cache-dependency-path: exercise-ai/requirements.txt

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r exercise-ai/requirements.txt

      - name: Run tests
        run: pytest exercise-ai -q
```

### README note (D-18)

Under “Como testar”, after the local pytest command, add one sentence such as:

> Em push/PR para `master`, o workflow GitHub Actions `CI` executa o mesmo comando.

Keep the local command identical: `pytest exercise-ai -q` [VERIFIED: README.md:59-65].

### requirements.txt contract (verbatim)

[VERIFIED: exercise-ai/requirements.txt:1-5]

```text
openai>=1.50.0
google-genai>=1.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
pytest>=8.0.0
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual local pytest only | GitHub Actions on push/PR | Phase 7 (this) | Regression visible on PRs |
| `actions/checkout@v3`–`v4` era examples | `@v7` | 2026 major line | Use current major |
| `setup-python@v4`/`v5` in many tutorials | `@v7` | 2026-07 | Prefer releases over stale tutorials |
| Enterprise CI (matrix, coverage, required rulesets) | Single job, visible check | Operator preference / CONTEXT | Stay minimal |

**Deprecated/outdated:**
- Pinning `setup-python@v5` solely because the “Building and testing Python” tutorial snippet still shows it — superseded by action v7 releases [ASSUMED: tutorial lag vs release cadence].

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Tutorial docs lag behind action majors; `@v7` remains correct through planning window (~30d) | Standard Stack | Executor may need minor pin bump |
| A2 | Optional `permissions: contents: read` is sufficient for checkout+pytest (no packages write) | Discretion / Security | Rare need for extra scopes — unlikely for this job |
| A3 | Fork PRs from public forks will not receive repo secrets (platform default) — reinforces omitting secrets | Security | If secrets were added later, fork risk rises — don't add them |
| A4 | Operator may manually set required check named after workflow/job after first green run | CI-02 / D-16 | Merge “confidence” stays social/process until then |

**If empty cells were expected:** A1–A4 are the only assumed claims; all locked decisions and repo facts were verified or cited.

## Open Questions (RESOLVED)

1. **Exact workflow filename / display name** — **RESOLVED**
   - What we know: Discretion allows `ci.yml` vs `test.yml`; suggest `ci.yml` + `name: CI` + job `test`.
   - **RESOLVED (07-01-PLAN discretion):** `.github/workflows/ci.yml`; workflow `name: CI`; job id `test` (D-15).

2. **pip cache on/off** — **RESOLVED**
   - What we know: Optional; D-03 says not required.
   - **RESOLVED (07-01-PLAN discretion):** Omit `cache: pip` / `cache-dependency-path` in MVP; polish later if slow (D-03).

3. **Belt-and-suspenders unset of LLM env vars (D-13)** — **RESOLVED**
   - What we know: Unnecessary if never injected.
   - **RESOLVED (07-01-PLAN discretion):** Skip explicit env unset; never inject secrets → unset unnecessary (D-11 / D-13 skip).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| GitHub Actions (hosted) | CI-01/02 | ✓ (repo on GitHub) | N/A | — |
| Default branch `master` | Triggers D-04 | ✓ | HEAD = master | — |
| Python on runner via setup-python | Job runtime | ✓ (Actions) | pin 3.11 | — |
| Local Python (dev probe) | Local verify only | ✓ | 3.14.0 | Not used in CI |
| pytest + deps (requirements.txt) | Test step | ✓ | pytest≥8 in requirements | — |
| `.github/workflows/` today | Greenfield | ✗ (absent) | — | Create in execution |
| `pyproject.toml` | Packaging | ✗ | — | Not required (D-10) |
| Knowledge graph `.planning/graphs/graph.json` | Research enrichment | ✗ | — | Skipped |

**Missing dependencies with no fallback:** none for planning — GitHub-hosted runners provide the execution environment once workflow is merged.

**Missing dependencies with fallback:** local 3.14 ≠ CI 3.11 (intentional).

## Validation Architecture

> `workflow.nyquist_validation` is `true` in `.planning/config.json` [VERIFIED: .planning/config.json:11].

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest ≥8.0.0 (`exercise-ai/requirements.txt`) |
| Config file | none (conftest path grounding only) |
| Quick run command | `pytest exercise-ai -q` |
| Full suite command | `pytest exercise-ai -q` (same; 73 tests) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| CI-01 | Suite runs without live LLM / without API secrets in job | existing unit/integration suite + workflow review | `pytest exercise-ai -q` (local proxy); CI job must not reference LLM secrets | ✅ suite exists; ❌ workflow Wave 0 |
| CI-02 | Nonzero pytest exit → failed check | platform behavior + smoke after first push | Push failing commit or rely on Actions semantics | ❌ needs first workflow run on GitHub |

### Sampling Rate

- **Per task commit:** `pytest exercise-ai -q` (local)
- **Per wave merge:** same + YAML review (no secrets; correct branches)
- **Phase gate:** Workflow file present; suite green locally; after push to GitHub, Actions run visible green/red

### Wave 0 Gaps

- [ ] `.github/workflows/ci.yml` — does not exist yet (greenfield)
- [ ] README CI one-liner — not present yet
- [ ] Framework install: N/A — pytest already in requirements.txt
- [ ] No new pytest files required for CI-01 offline guarantee — existing 73 tests cover app behavior; CI is orchestration

**Local probe this session:** `python -m pytest exercise-ai --collect-only -q` → `73 tests collected in 2.13s` [VERIFIED: shell collect-only].

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no (CI job has no user auth) | — |
| V3 Session Management | no | — |
| V4 Access Control | partial | `permissions: contents: read`; no branch-protection API |
| V5 Input Validation | no new app inputs | — |
| V6 Cryptography | no | — |
| Secrets management (V2-adjacent) | **yes** | Never inject LLM API keys into workflow; do not commit `.env` |

### Known Threat Patterns for GitHub Actions + LLM CLI

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| LLM API key in workflow `env`/`secrets` | Information Disclosure | Omit keys entirely (D-11); suite uses mocks |
| Secrets logged by app during CI | Information Disclosure | Existing redaction in generators; tests in `test_logging_security.py` |
| Over-privileged `GITHUB_TOKEN` | Elevation of Privilege | `permissions: contents: read` |
| `pull_request_target` with untrusted code | Tampering / RCE | Do not use `pull_request_target`; use `pull_request` (D-04) |
| Wrong-branch silent skip | Denial of availability (no CI) | Filter `master` correctly |

Serena search confirmed keys are read via `os.getenv` / documented in `.env.example`, and tests inject **dummy** keys via `monkeypatch` — not production secrets in CI. Semgrep custom probe on snippets confirmed `os.getenv("LLM_API_KEY")` / `load_dotenv` usage patterns (INFO-level; no hardcoded live secrets in scanned snippets).

## Sources

### Primary (HIGH confidence)

- Context7 `/websites/github_en_actions` — workflow templates, triggers, permissions, Python build/test tutorial
- Context7 `/actions/setup-python` — v7 usage, optional pip cache
- Context7 `/actions/checkout` — basic `@v7` checkout
- GitHub Releases: `actions/checkout` v7.0.1, `actions/setup-python` v7.0.0 (2026-07-20)
- Repo: `07-CONTEXT.md`, `README.md`, `exercise-ai/requirements.txt`, `exercise-ai/tests/conftest.py`, `exercise-ai/main.py`, `.planning/config.json`
- Shell: default branch `master`; pytest collect-only 73 tests; local Python 3.14.0

### Secondary (MEDIUM confidence)

- Serena `search_for_pattern` across `exercise-ai` for env/secret usage
- Semgrep `semgrep_scan_with_custom_rule` on secret-related snippets (default `semgrep_scan` RPC failed twice)

### Tertiary (LOW confidence)

- Assumption that GitHub tutorial snippets will continue to lag action majors (A1)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — locked CONTEXT + verified action releases + Context7
- Architecture: HIGH — single job mapping is trivial and constrained
- Pitfalls: HIGH — branch name, cwd, secrets are the classic failure modes and were checked against this repo

**Research date:** 2026-09-11  
**Valid until:** ~2026-10-11 (30 days; action majors may bump)

## Research Tool Evidence

Tools/MCPs personally invoked in this execution only:

### Serena — AVAILABLE
- **Calls:** `activate_project` (GeradorExercicios path); `get_symbols_overview` on `exercise-ai/tests/conftest.py`; `search_for_pattern` for `LLM_API_KEY|GEMINI_API_KEY|load_dotenv|os.environ|getenv` under `exercise-ai`
- **Obtained:** Project activated with Python LS; conftest symbols `_PACKAGE_DIR`, `make_request`, `make_exercise`, `make_batch`; env/secret usage map across `main.py`, generators, tests, `.env.example`
- **Influenced:** Path-grounding pattern; Pitfall 5 (no `.env` required for tests); Security Domain secret non-injection; CI-01 research support

### Context7 — AVAILABLE
- **Calls:** `resolve-library-id` (GitHub Actions; actions/setup-python); `query-docs` on `/websites/github_en_actions` (Python CI workflow, permissions, pytest tutorial); `query-docs` on `/actions/setup-python` (v7 + pip cache); `query-docs` on `/actions/checkout` (basic `@v7`)
- **Obtained:** Workflow YAML patterns; `permissions` least privilege; confirmation that some GH tutorials still show older majors while action docs show `@v7`
- **Influenced:** Standard Stack, Code Examples, Architecture Patterns, Don't Hand-Roll, Pitfall 4

### Semgrep — AVAILABLE (partial)
- **Calls:** `semgrep_scan` on `conftest.py` / `main.py` / `generator.py` — **failed twice** (`RPC server may not be running: Connection lost`); `get_supported_languages` — **succeeded** (python supported); `semgrep_scan_with_custom_rule` on secret/env snippets — **succeeded** (INFO matches on `os.getenv` / `load_dotenv`; no hardcoded live key values in provided snippets)
- **Obtained:** Default file scan unavailable via RPC; custom-rule path works; confirms getenv/dotenv patterns without evidence of hardcoded production secrets in snippets
- **Influenced:** Security Domain; Research Tool Evidence honesty about `semgrep_scan` failure

### Built-in tools used
- **GetDynamicTools:** Discovered `serena`, `context7`, `semgrep` namespaces ready
- **Read:** CONTEXT, agent contract, README, PROJECT, requirements.txt, conftest, main.py (dotenv), rules, skill, config.json
- **Grep:** REQUIREMENTS CI-01/02; ROADMAP Phase 7; env key usage
- **Glob:** confirmed no `.github/**` yet; listed phase dir
- **WebFetch:** `actions/checkout` and `actions/setup-python` `/releases/latest` → v7.0.1 / v7.0.0
- **Shell:** `git remote show origin` (HEAD `master`); `pytest --collect-only` (73 tests); Python 3.14.0; graph.json absent
- **Write:** this `07-RESEARCH.md` (full overwrite)
