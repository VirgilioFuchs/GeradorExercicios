# Phase 7: Continuous Integration - Research

**Researched:** 2026-09-11
**Domain:** GitHub Actions minimal Python CI (pytest, no LLM secrets)
**Confidence:** HIGH

## Summary

Phase 7 is a greenfield GitHub Actions workflow: one job on `ubuntu-latest`, Python 3.11, install from `exercise-ai/requirements.txt`, run `pytest exercise-ai -q` from the repo root on `push`/`pull_request` to `master`. No new PyPI packages. No matrix, lint, coverage, Docker, or branch-protection API.

The existing suite already collects **73 tests** without live LLM calls; `conftest.py` only grounds `sys.path` and factories — secrets are never required for a green suite. CI-02 is satisfied by Actions’ built-in check runs on the PR Checks tab; making a check *required* for merge is optional GitHub UI config (out of scope for this phase’s automation).

**Primary recommendation:** Add `.github/workflows/ci.yml` with `name: CI`, job `test`, `permissions: contents: read`, `actions/checkout@v7` + `actions/setup-python@v7` (`python-version: '3.11'`, optional `cache: pip` + `cache-dependency-path: exercise-ai/requirements.txt`), install/test commands mirroring README, **no** `LLM_*` / `GEMINI_*` secrets or `env` injection — then one short README CI note.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
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
| CI-01 | Em push/PR no GitHub, Actions instala deps e roda `pytest` no pacote `exercise-ai` sem chamar LLM live (sem secrets de API no job) | Workflow YAML mirrors README install/test; no secrets block; suite already mock-based (73 collected); `pytest` in `requirements.txt` |
| CI-02 | Falha de testes deixa o check vermelho e bloqueia merge confiante (status visível no PR) | Actions auto-creates check runs on PR Checks tab; red = job failure; required-check enforcement is optional UI (D-16), not API in this phase |
</phase_requirements>

## Project Constraints (from .cursor/rules/)

From `.cursor/rules/10-python.mdc` and `.cursor/rules/20-ai-engineering.mdc` (via `skills/python-ai-engineering/SKILL.md`):

| Directive | Implication for Phase 7 |
|-----------|-------------------------|
| YAGNI / KISS / smallest correct change | One workflow file, one job; no CI platform sprawl |
| Never hardcode API secrets; keys via `.env` only | Workflow must not declare/inject `LLM_API_KEY` / `GEMINI_API_KEY` |
| LLM output is not evidence — deterministic verification | Trust pytest exit code; no live-API smoke job |
| Prefer Context7 for framework/SDK docs | Used for Actions / setup-python / checkout |
| Semgrep when changes involve secrets / auth | Scan workflow for accidental secret refs if editing secrets surface |
| Serena before non-trivial Python refactors | N/A — this phase is YAML + README only |
| Fail fast / verify with evidence | Local `pytest exercise-ai -q` before/after; first Actions run as proof |

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Workflow definition (triggers, job, steps) | Repo config (Git) | — | Versioned YAML under `.github/workflows/`; no app runtime |
| Dependency install + pytest execution | CI runner (GitHub-hosted) | — | `ubuntu-latest` executes install/test; app code unchanged |
| No-live-LLM guarantee | Test suite (app) | CI config | Mocks/factories already own this; CI must not inject secrets |
| Status visibility (green/red on PR) | GitHub Checks UI | — | Actions emits check runs automatically |
| Optional merge gate (required check) | Repo settings (human) | — | D-16: operator may enable in UI; not automated here |
| Operator docs (README note) | Docs / Static | — | D-17/D-18: one short note; same local command |

## Standard Stack

### Core

| Library / Action | Version | Purpose | Why Standard |
|------------------|---------|---------|--------------|
| GitHub Actions workflow | YAML under `.github/workflows/` | CI orchestration | Native GitHub CI; zero new deps [CITED: docs.github.com/en/actions] |
| `actions/checkout` | **v7** (current major) | Checkout repo into `$GITHUB_WORKSPACE` | Official checkout action; README shows `@v7` [CITED: github.com/actions/checkout] |
| `actions/setup-python` | **v7** (current major; release `v7.0.0` 2026-07-20) | Install Python 3.11 + optional pip cache | Official setup action [CITED: github.com/actions/setup-python/releases/latest] |
| Python | **3.11** (job pin) | Runtime for suite | Locked D-07; PROJECT floor “3.11+” [VERIFIED: .planning/PROJECT.md:17] quote: `Python 3.11+` |
| pip + `exercise-ai/requirements.txt` | as in repo | Install deps including pytest | Locked D-08; README Setup [VERIFIED: README.md:7-9] |
| pytest | `>=8.0.0` (from requirements) | Test runner | Already in requirements [VERIFIED: exercise-ai/requirements.txt:5] quote: `pytest>=8.0.0` |

### Supporting

| Item | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `cache: pip` + `cache-dependency-path` | setup-python input | Speed repeated installs | Discretion — recommended for nested `exercise-ai/requirements.txt` [CITED: github.com/actions/setup-python README] |
| `permissions: contents: read` | workflow key | Least-privilege `GITHUB_TOKEN` | Discretion — recommended; checkout docs show this pattern [CITED: github.com/actions/checkout README] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Single Python 3.11 job | Matrix 3.11–3.13 / multi-OS | Broader coverage; **deferred** (D-03) |
| `pip install -r …` | poetry / uv / `pip install -e .` | Packaging not in repo; **deferred** (D-10) |
| Visible Checks only | Branch protection API / Rulesets | True merge block; **deferred** (D-16) |
| GitHub Actions | other CI (Azure, Circle) | Extra accounts; not requested |

**Installation (CI job steps — not local PyPI adds):**

```bash
python -m pip install --upgrade pip
pip install -r exercise-ai/requirements.txt
pytest exercise-ai -q
```

**Version verification notes:**
- Local machine probed this session: Python **3.14.0**, pytest **9.0.3** — reinforces D-07 pin to **3.11** on CI so runner ≠ local surprise. [VERIFIED: shell `python --version` / `pip show pytest`]
- GitHub **tutorial** still shows `checkout@v6` / `setup-python@v5` in places [CITED: docs.github.com/en/actions/tutorials/build-and-test-code/python]; action repos are ahead at **v7**. Prefer **v7** majors from action READMEs/releases for the plan skeleton.
- No new PyPI packages → no `pip index` legitimacy gate required for installs.

## Package Legitimacy Audit

> **None — Actions only.** This phase adds workflow YAML + a README note. It does **not** introduce new PyPI/npm/crates packages.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| — | — | — | — | — | N/A | No new packages |

**Packages removed due to [SLOP] verdict:** none  
**Packages flagged as suspicious [SUS]:** none  

Third-party **Actions** used (not PyPI): `actions/checkout`, `actions/setup-python` — official `actions/*` orgs; pin major tags `@v7`.

## Architecture Patterns

### System Architecture Diagram

```text
push / pull_request → master
        │
        ▼
┌───────────────────────────┐
│  GitHub Actions           │
│  workflow: CI             │
│  permissions: contents:read│
└───────────┬───────────────┘
            │
            ▼
┌───────────────────────────┐
│  Job: test                │
│  runs-on: ubuntu-latest   │
└───────────┬───────────────┘
            │
     ┌──────┼──────────────────────┐
     ▼      ▼                      ▼
 checkout  setup-python 3.11    (no secrets)
     │      │
     └──────┤
            ▼
   pip install -r exercise-ai/requirements.txt
            │
            ▼
   pytest exercise-ai -q   ◄── mocks/factories (no live LLM)
            │
     ┌──────┴──────┐
     ▼             ▼
  exit 0        non-zero
  (success)     (failure)
     │             │
     └──────┬──────┘
            ▼
   Check run on PR Checks tab
   (green / red) — CI-02 visible
```

### Recommended Project Structure

```text
.github/
└── workflows/
    └── ci.yml              # sole workflow (discretion: ci.yml recommended)
README.md                   # short CI note under Como testar
exercise-ai/
├── requirements.txt        # unchanged — pytest already listed
└── tests/                  # unchanged — mock suite
```

No `.github/` exists today — greenfield. [VERIFIED: shell listing → `NO_.github`]  
Default remote branch: **master**. [VERIFIED: `git remote show origin` → `HEAD branch: master`]

### Pattern 1: Minimal single-job Python CI
**What:** checkout → setup-python → pip install → pytest; one `runs-on`.  
**When to use:** Lab/MVP regression (this phase).  
**Example:** See Code Examples below (adapted from official Python CI tutorial + locked paths).

### Pattern 2: Nested requirements + pip cache
**What:** `cache: pip` with explicit `cache-dependency-path: exercise-ai/requirements.txt` because the file is not at repo root.  
**When to use:** Optional speed-up (discretion). Without `cache-dependency-path`, cache key may miss nested file. [CITED: github.com/actions/setup-python docs]

### Pattern 3: PR status without protection API
**What:** Rely on automatic check runs; document visibility; leave required-check toggle to human.  
**When to use:** CI-02 + D-16. [CITED: docs.github.com … about-status-checks]

### Anti-Patterns to Avoid
- **Matrix / coverage / lint gates now:** Violates D-03 / YAGNI.
- **`working-directory: exercise-ai` + `pytest -q`:** Breaks canonical root command D-09 / README.
- **`secrets.LLM_API_KEY` in workflow:** Violates CI-01 / D-11.
- **Triggering only `main`:** Remote default is `master` — wrong branch filter = silent no-runs. [VERIFIED: remote HEAD master]
- **`pull_request_target` for fork CI:** Unnecessary privilege; not needed for this lab.
- **Tutorial copy-paste with matrix + artifact upload:** Overkill vs D-01.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Checkout repo on runner | Custom git clone scripts | `actions/checkout@v7` | Auth, sparse, PR merge refs handled |
| Install Python on runner | apt/pyenv scripts | `actions/setup-python@v7` | Version pin + cache hooks |
| Publish PR status | Manual Commit Status API | Actions check runs (automatic) | Built-in Checks tab |
| Enforce required checks in code | REST Rulesets/branch-protection API | Operator UI (optional) | D-16 / deferred |
| Detect “no live LLM” in CI | Custom network firewall job | Existing mock suite | Suite already guarantees offline |

**Key insight:** The hard work (offline, reliable tests) already shipped in Phases 3–6; Phase 7 only wires the same command into Actions.

## Common Pitfalls

### Pitfall 1: Wrong working directory
**What goes wrong:** Job cds into `exercise-ai/` and runs `pytest -q` or `pytest tests` — drifts from README / D-09.  
**Why it happens:** Package layout looks like a subproject.  
**How to avoid:** Keep default GITHUB_WORKSPACE root; run `pytest exercise-ai -q` and `pip install -r exercise-ai/requirements.txt`.  
**Warning signs:** “file or directory not found”, different local vs CI commands.

### Pitfall 2: Branch name `main` vs `master`
**What goes wrong:** Workflow never runs on PRs/pushes.  
**Why it happens:** Templates default to `main`.  
**How to avoid:** `branches: [master]` for both `push` and `pull_request` (D-04).  
**Warning signs:** No workflow runs; Checks tab empty / pending forever if required later.

### Pitfall 3: Missing pytest / wrong requirements path
**What goes wrong:** `pytest: command not found` or empty env.  
**Why it happens:** Installs root `requirements.txt` that doesn’t exist; or forgets install step.  
**How to avoid:** Exact path `exercise-ai/requirements.txt` which includes `pytest>=8.0.0`. [VERIFIED: exercise-ai/requirements.txt:5]

### Pitfall 4: Accidental LLM secrets
**What goes wrong:** CI-01 fails intent; risk of live calls or key leakage in logs.  
**Why it happens:** Copy-paste from deploy workflows; repo secrets auto-mapped.  
**How to avoid:** No `env:` / `secrets:` for LLM keys; do not add repository secrets for this job. Suite uses `monkeypatch.setenv` with dummy values only inside tests. [VERIFIED: exercise-ai/tests/test_logging_security.py:18-24] quote: `DUMMY_LLM_KEY = "sk-TEST-LEAK-LLM-KEY-9f3a2b1c"` / `monkeypatch.setenv("LLM_API_KEY", DUMMY_LLM_KEY)`.  
**Warning signs:** Workflow YAML contains `LLM_API_KEY` or `secrets.`.

### Pitfall 5: Assuming branch protection = CI-02
**What goes wrong:** Planner adds API automation or marks phase incomplete without UI toggle.  
**Why it happens:** “bloqueia merge” wording.  
**How to avoid:** Per D-14–D-16, success = **visible** red/green check; required-check is optional human step. [CITED: docs.github.com … about-status-checks — required protected branch is separate]

### Pitfall 6: Skipped workflow leaves Pending
**What goes wrong:** If later required, skip instructions / branch filters leave checks Pending and block merges.  
**Why it happens:** Path/branch filters or `[skip ci]`.  
**How to avoid:** Don’t add skip-heavy filters this phase; keep triggers simple. [CITED: docs.github.com workflow-syntax branches note]

### Pitfall 7: Stale action majors from old tutorials
**What goes wrong:** Plan pins `@v4`/`@v5` unnecessarily or mixes incompatible docs.  
**How to avoid:** Prefer current major **v7** from action repos; note tutorial lag. [CITED: setup-python releases v7.0.0]

## Code Examples

### Recommended workflow (planner skeleton)

```yaml
# Source: adapted from docs.github.com Python CI tutorial + locked CONTEXT D-01…D-15
# Actions majors: checkout/setup-python @v7 per action READMEs/releases (2026)
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
          cache: 'pip'
          cache-dependency-path: exercise-ai/requirements.txt

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r exercise-ai/requirements.txt

      - name: Run tests
        run: pytest exercise-ai -q
```

**Discretion notes baked in:** filename `ci.yml`; `name: CI`; job id `test`; pip cache on; `permissions: contents: read`; paths from repo root (no `defaults.run.working-directory`).

**Do not include** (CI-01):

```yaml
# ANTI-PATTERN — never in this phase
env:
  LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

### README note (D-17 / D-18)

Under `## Como testar`, after the existing command block [VERIFIED: README.md:59-65], add ~1–2 lines, e.g.:

> Em push/PR para `master`, o GitHub Actions roda o mesmo comando (`pytest exercise-ai -q`) sem secrets de LLM.

Keep the local bash block unchanged:

```bash
pytest exercise-ai -q
```

### Suite offline grounding

`conftest.py` only adjusts `sys.path` and provides factories — no dotenv load: [VERIFIED: exercise-ai/tests/conftest.py:10-20]

```text
_PACKAGE_DIR = Path(__file__).resolve().parents[1]
if str(_PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_DIR))
```

Collect evidence this session: `73 tests collected`. [VERIFIED: shell `pytest exercise-ai --collect-only -q`]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual local pytest only (Phase 3 D-10 deferred CI) | Minimal Actions workflow | Phase 7 | Regression on every push/PR |
| `checkout@v3`/`setup-python@v4` blog posts | `@v7` majors | 2026 action releases | Prefer current majors |
| Commit Status API integrations | Actions **checks** | Actions era | Checks tab detail + logs |
| Enterprise matrices day-one | Single job YAGNI | Lab preference | Faster to ship; expand later |

**Deprecated/outdated:**
- Copying multi-OS matrix + coverage artifact workflows for this lab (D-03).
- Assuming default branch is `main` without checking remote HEAD.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | First Actions run on this repo will succeed with the skeleton above without extra apt packages | Code Examples / Validation | Executor may need one fix-up commit (e.g. PATH); low likelihood on `ubuntu-latest` + pip |
| A2 | Check name shown on PR will be recognizable as `CI` / `test` (GitHub formats `Workflow / job`) | CI-02 / Discretion | Operator may need one glance at Checks tab naming — still meets D-15 if `name:`/`job` clear |
| A3 | Optional belt-and-suspenders `env: LLM_API_KEY: ''` is unnecessary if secrets are never referenced | Pitfalls / D-13 | None if D-11 held; empty env is harmless if planner adds it |

**If wrong:** Planner keeps Wave 0 / verify-work path for A1; A2–A3 are cosmetic.

## Open Questions

1. **Exact action major tags in the committed YAML**
   - What we know: Action READMEs/releases show **v7**; GitHub Python tutorial still shows older majors in places.
   - What's unclear: Whether org policy prefers SHA-pinning (not required by CONTEXT).
   - Recommendation: Pin `@v7` majors (not full SHAs) for readability in this lab.

2. **Enable pip cache on day one?**
   - What we know: Not required (D-03); nested path needs `cache-dependency-path`.
   - Recommendation: **Yes** include cache — cheap, reversible; omit if planner wants absolute minimal first commit.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| GitHub-hosted `ubuntu-latest` | CI job | ✓ (remote) | GitHub-managed | — |
| Python 3.11 on runner | setup-python | ✓ (via action) | 3.11 | — |
| Local Python | Dev verification | ✓ | 3.14.0 (local) | Use CI pin 3.11; don’t require local 3.11 for planning |
| pytest (local) | Pre-push check | ✓ | 9.0.3 | From requirements |
| `.github/` tree | Workflow file | ✗ (absent) | — | Create on implement |
| Graphify graph | Cross-doc intel | ✗ | — | Skipped — no `.planning/graphs/graph.json` |

**Missing dependencies with no fallback:** none for planning (Actions runs in GitHub cloud).

**Missing dependencies with fallback:** local graphify — research proceeded via docs + repo reads.

## Validation Architecture

> `workflow.nyquist_validation` is **true** in `.planning/config.json` — section required.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (`pytest>=8.0.0` in requirements; local 9.0.3) |
| Config file | none — discovery via `exercise-ai/tests/` + `conftest.py` |
| Quick run command | `pytest exercise-ai -q` |
| Full suite command | `pytest exercise-ai -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| CI-01 | Suite runs without LLM secrets / live calls | existing unit (suite) | `pytest exercise-ai -q` | ✅ `exercise-ai/tests/*` |
| CI-01 | Workflow has no LLM secret injection | review / grep | `rg "LLM_API_KEY\|GEMINI_API_KEY\|secrets\." .github/workflows` after add | ❌ Wave 0: workflow not yet created |
| CI-02 | Failed pytest → failed job → red check | manual / GitHub UI | Push failing commit on branch OR rely on Actions semantics | ❌ manual after first workflow push |
| CI-02 | Check visible on PR | manual UAT | Open PR Checks tab | ❌ post-implement |

### Sampling Rate
- **Per task commit:** `pytest exercise-ai -q`
- **Per wave merge:** `pytest exercise-ai -q`
- **Phase gate:** Full suite green locally + at least one successful Actions run on `master`/PR; confirm Checks tab shows workflow name; confirm workflow YAML has no LLM secrets

### Wave 0 Gaps
- [ ] `.github/workflows/ci.yml` — does not exist yet (implementation deliverable, not a pytest file)
- [ ] No separate `test_ci_workflow.py` needed — YAML validated by Actions run + static review
- [ ] Framework install: already covered by `exercise-ai/requirements.txt`

*(App-level gaps: none — existing 73-test suite covers CI-01 offline behavior.)*

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A — no app auth in CI job |
| V3 Session Management | no | N/A |
| V4 Access Control | partial | `permissions: contents: read` on `GITHUB_TOKEN` |
| V5 Input Validation | no | Workflow not parsing untrusted app input beyond PR code under normal `pull_request` |
| V6 Cryptography | no | N/A |
| Secrets management | **yes** | Never inject/store LLM API keys in workflow; keep keys in local `.env` only |

### Known Threat Patterns for GitHub Actions + LLM labs

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Secret exfiltration via workflow `env`/`secrets` | Information Disclosure | Omit LLM secrets entirely (D-11) |
| Live API spend / flaky CI from real LLM | Tampering / DoS (cost) | Mock-only suite; no smoke-live job (D-12) |
| Over-privileged `GITHUB_TOKEN` | Elevation of Privilege | `permissions: contents: read` |
| Supply-chain malicious Action | Tampering | Use official `actions/*` @ major pins |
| `pull_request_target` pwn request | Elevation of Privilege | Do not use; stick to `pull_request` |

## Sources

### Primary (HIGH / MEDIUM via classify-confidence)
- Context7 `/websites/github_en_actions` — Python CI tutorial (`checkout`, `setup-python`, pip, pytest); workflow `permissions`; PR branch filters / Pending checks
- Context7 `/actions/setup-python` — pip `cache` + `cache-dependency-path`
- Context7 `/actions/checkout` — `@v7`, `permissions: contents: read`
- [CITED: https://github.com/actions/setup-python/releases/latest] — `v7.0.0` (2026-07-20)
- [CITED: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks] — Actions generates checks; Checks tab; required checks vs protected branches
- Repo: `07-CONTEXT.md`, `ROADMAP.md`, `REQUIREMENTS.md`, `PROJECT.md`, `README.md`, `exercise-ai/requirements.txt`, `exercise-ai/tests/conftest.py`, `.cursor/rules/*`, `.planning/config.json`

### Secondary
- Shell probes: no `.github/`, remote `master`, 73 tests collected, local Python 3.14 / pytest 9.0.3
- gsd-tools `classify-confidence --provider context7 --verified` → **MEDIUM** (used for docs-backed claims)

### Tertiary
- None material; A1–A3 logged as assumptions

## Metadata

**Confidence breakdown:**
- Standard stack: **HIGH** — official Actions docs + action releases + locked CONTEXT commands
- Architecture: **HIGH** — trivial single-job pipeline; greenfield `.github/`
- Pitfalls: **HIGH** — branch name, cwd, secrets, and CI-02 visibility confirmed against docs + repo facts
- Package legitimacy: **N/A** — no new packages

**Research date:** 2026-09-11  
**Valid until:** ~2026-10-11 (Actions majors move periodically; re-check `@v7` if planning delayed >30 days)

**Discretion recommendations (for planner):**
1. File: `.github/workflows/ci.yml` · `name: CI` · job: `test`
2. Include pip cache + `cache-dependency-path: exercise-ai/requirements.txt`
3. Include `permissions: contents: read`
4. Do **not** set `defaults.run.working-directory`; keep root-relative paths
5. Skip empty `env:` unset unless executor wants belt-and-suspenders (D-13 optional)
