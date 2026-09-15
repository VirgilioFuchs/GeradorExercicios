# Phase 7: Continuous Integration - Pattern Map

**Mapped:** 2026-09-11
**Files analyzed:** 5 (2 touch + 3 read-only contracts)
**Analogs found:** 2 / 2 touch targets (workflow = greenfield; README = self)
**Source:** CONTEXT.md + RESEARCH.md + codebase

## File Classification

Implied from CONTEXT (D-01–D-19) and RESEARCH recommended structure. Phase is CI greenfield: **no Python pipeline changes**.

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `.github/workflows/ci.yml` (new) | config / orchestration | event → install → batch (pytest) → exit status | **GREENFIELD** — no `.github/` in repo; behavioral contract = README Setup + Como testar | greenfield |
| `README.md` (modify) | docs | operator discovery | itself — section `## Como testar` | exact |

**Read-only contracts (do not modify this phase):**

| File | Role | Why relevant |
|------|------|--------------|
| `exercise-ai/requirements.txt` | config / deps | D-08 install path; sole dep source for the job |
| `exercise-ai/tests/conftest.py` | test bootstrap | Path grounding enables root `pytest exercise-ai -q` (D-09) |
| `exercise-ai/tests/` (suite) | test | Offline mocks; CI-01 relies on existing ~73 tests |

**Not in scope:** `main.py` / generators / `reliability.py` / `validator.py`; matrix, lint, coverage, Docker, branch-protection API, new pytest files, `pyproject.toml`.

---

## Pattern Assignments

### `.github/workflows/ci.yml` (config / orchestration) — NEW — GREENFIELD

**Analog:** None in-repo (scout: no `.github/`). Closest **behavioral** analogs are README install + test commands and RESEARCH Pattern 1 skeleton.

**Secondary analogs (command contract only):**
- `README.md` Setup → `pip install -r exercise-ai/requirements.txt`
- `README.md` Como testar → `pytest exercise-ai -q`
- `exercise-ai/tests/conftest.py` → why root invocation works

**Locked shape (D-01, D-04–D-09, D-11, D-15):**
- One file, one job (`test`), workflow `name: CI`
- Triggers: `push` + `pull_request` on **`master`** only (not `main`)
- Runner: `ubuntu-latest`; Python **`3.11`** via `actions/setup-python@v7`
- Checkout: `actions/checkout@v7`
- No `LLM_API_KEY` / `GEMINI_API_KEY` / other LLM secrets
- No `continue-on-error` on pytest (CI-02)
- No matrix / ruff / coverage / `workflow_dispatch` (D-03, D-05)

**Recommended skeleton** (from RESEARCH; discretion filled: `ci.yml`, `permissions: contents: read`, no pip cache):

```yaml
# Source: RESEARCH Pattern 1 + CONTEXT D-04–D-11
# Branches: master (repo HEAD — not main)
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
          # cache: 'pip'  # optional; omit for MVP (D-03)

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r exercise-ai/requirements.txt

      - name: Run tests
        run: pytest exercise-ai -q
```

**Data flow:**
```text
push|PR → master
  → checkout ($GITHUB_WORKSPACE = repo root)
  → setup-python 3.11
  → pip install -r exercise-ai/requirements.txt
  → pytest exercise-ai -q   # cwd = root; no LLM env
  → exit 0 → check green | exit ≠0 → check red (CI-02)
```

**Install contract** — mirror README / requirements verbatim:

From `README.md` (Setup):
```bash
pip install -r exercise-ai/requirements.txt
```

From `exercise-ai/requirements.txt`:
```text
openai>=1.50.0
google-genai>=1.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
pytest>=8.0.0
```

**Test contract** — mirror README / Phase 3 D-04:

From `README.md` (Como testar):
```bash
pytest exercise-ai -q
```

**Path grounding** — do **not** `cd exercise-ai` or set `defaults.run.working-directory: exercise-ai` for the pytest step (D-09). Root works because:

From `exercise-ai/tests/conftest.py` (10–13):
```python
_PACKAGE_DIR = Path(__file__).resolve().parents[1]
if str(_PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_DIR))
```

**Secrets pattern (CI-01 / D-11):** omit entirely — do not declare:

```yaml
# ANTI-PATTERN — never for this phase
env:
  LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

Suite already injects **dummy** keys only inside tests when needed (not production secrets):

From `exercise-ai/tests/test_logging_security.py` (22–24):
```python
def test_openai_mapper_auth_stderr_never_contains_key(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", DUMMY_LLM_KEY)
    monkeypatch.setenv("GEMINI_API_KEY", DUMMY_GEMINI_KEY)
```

From `exercise-ai/tests/test_main.py` (181–184):
```python
def test_cli_provider_override_sets_env(demo_batch, tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    monkeypatch.setenv("GEMINI_API_KEY", "AIza-test")
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
```

App loads `.env` at import for CLI usage — **irrelevant to CI** if secrets are never injected:

From `exercise-ai/main.py` (19–23):
```python
env_path = current_dir / ".env"
if not env_path.exists():
    env_path = current_dir.parent / ".env"
load_dotenv(dotenv_path=env_path)
```

Do not copy `.env.example` into the job or create Actions secrets for keys listed there (`LLM_API_KEY`, `GEMINI_API_KEY`).

**Discretion (planner may choose without checkpoint):**
- Filename: prefer `ci.yml` (RESEARCH recommendation)
- Optional `cache: pip` + `cache-dependency-path: exercise-ai/requirements.txt` — omit for MVP
- Optional D-13 explicit unset of LLM env — skip unless documenting absence
- Prefer paths from repo root over `working-directory: exercise-ai`

**Don't hand-roll:** custom git clone, apt/pyenv Python, Jenkins, branch-protection API, live-LLM smoke job.

---

### `README.md` (docs) — MODIFY

**Analog:** itself — `## Como testar` (lines 59–65).

**Current pattern:**
```markdown
## Como testar

A suite usa mocks e dados estáticos — **não** chama LLMs reais:

```bash
pytest exercise-ai -q
```
```

**Apply (D-17, D-18):** after the local pytest command, add **one** short sentence that push/PR to `master` run the GitHub Actions workflow `CI` with the **same** command. Do not add a separate “CI strategy” doc (D-19). Do not change the local command string.

**Suggested one-liner** (RESEARCH; planner may tweak wording):
> Em push/PR para `master`, o workflow GitHub Actions `CI` executa o mesmo comando.

**Keep identical:**
- Install: `pip install -r exercise-ai/requirements.txt`
- Test: `pytest exercise-ai -q`
- Env vars section stays documentation for local CLI — not CI setup

---

## Anti-Patterns (from RESEARCH + CONTEXT)

| Anti-pattern | Why wrong | Correct |
|--------------|-----------|---------|
| `branches: [main]` | Remote HEAD is `master` — CI never fires on PRs | `branches: [master]` |
| `working-directory: exercise-ai` + bare `pytest` | Breaks D-09 / README contract | `pytest exercise-ai -q` at root |
| Inject `secrets.*` LLM keys | Violates CI-01 / D-11 | Omit secrets/env for keys |
| Matrix / ruff / coverage / Docker | Deferred D-03 | Single job only |
| `continue-on-error: true` on pytest | Green check on failure — breaks CI-02 | Let nonzero exit fail job |
| Pin stale `@v5`/`@v6` from tutorials | Releases are `@v7` (2026-07) | `checkout@v7`, `setup-python@v7` |
| `pull_request_target` | Untrusted code + elevated token risk | Use `pull_request` (D-04) |
| Branch-protection Rulesets via API | Out of scope D-16 | Visible check only |
| New pytest files for “CI tests” | Suite already offline | Orchestrate existing suite |

---

## Integration Points

| From | To | Mechanism |
|------|----|-----------|
| GitHub `push`/`pull_request` on `master` | `.github/workflows/ci.yml` | Workflow `on:` filters |
| CI install step | `exercise-ai/requirements.txt` | `pip install -r …` |
| CI test step | `exercise-ai/tests/` via conftest | `pytest exercise-ai -q` |
| CI status | PR Checks UI | Default Actions check (CI-02) |
| Operator docs | `README.md` Como testar | One-line CI note |

**No integration with:** Python generation pipeline, live providers, repo Rulesets API.

---

## Verification Hints (for planner / executor)

- Local proxy for job: `pytest exercise-ai -q` from repo root (~73 collected)
- YAML review: no `LLM_API_KEY` / `GEMINI_API_KEY` / `secrets.` for LLM
- After first push: Actions run named `CI` / job `test` visible green/red on PR
- Optional operator follow-up (not code): mark required check manually in GitHub settings

---

*Phase: 7-Continuous Integration*
*Pattern map: 2026-09-11*
*Label: generalPurpose workaround for gsd-pattern-mapper*
