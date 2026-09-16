# Stack Research

**Domain:** Embedding an existing Python LLM pipeline as an in-process library + a throwaway stdlib demo page
**Researched:** 2026-09-16
**Confidence:** HIGH

---

## Headline

**For v2.0 the correct stack addition is: nothing.** No new runtime dependency, no `pyproject.toml`, no rename, no web framework. The milestone's value — `service.py` as a pure boundary — is entirely achievable on the current stack, and the demo is achievable with `http.server` alone.

But one finding materially changes the *parked* packaging decision, so it is recorded here in full:

> **The `sys.path.insert` embed strategy is not "worse" than packaging — it is broken.** It was tested against this repo's real `exercise-ai/` directory and it fails in both import orders. See [Finding 1](#finding-1-the-syspath-embed-strategy-is-empirically-broken). This does not make packaging a v2.0 task; it makes packaging the **precondition for the host integration actually shipping**, and it should be un-parked the moment the host's stack is known.

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.11 (CI pin) | Runtime | Already pinned in `.github/workflows/ci.yml`. Everything below is verified on 3.11+ and re-verified on 3.14. No reason to move. |
| `http.server` (stdlib) | stdlib | Serve the `demo/` page | Zero new dependency — the hard constraint. `ThreadingHTTPServer` + `SimpleHTTPRequestHandler` covers a static demo completely. |
| `socket` (stdlib) | stdlib | IPv6 loopback bind for `http://[::1]:8642/` | `HTTPServer.address_family` defaults to `AF_INET`; `socket.AF_INET6` is the one-line fix. Verified working on this Windows box. |
| `json` (stdlib) | stdlib | Serialize the contract JSON the demo displays | Already the serialization path in `main.run()` (`model_dump()` → `json.dumps`). Reuse it; do not introduce a second serializer. |
| `functools.partial` (stdlib) | stdlib | Pin `SimpleHTTPRequestHandler(directory=...)` | `directory=` kwarg exists since 3.7. Avoids `os.chdir`, which is process-global and would be a landmine if the demo ever shares a process. |

**Nothing is added to `exercise-ai/requirements.txt` for this milestone.**

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| — | — | — | None needed. The existing set (`openai`, `google-genai`, `pydantic`, `python-dotenv`, `pytest`) already covers v2.0. |

### Deferred — Packaging Toolchain (for the LATER decision, NOT v2.0)

| Tool | Current version | Purpose | Notes |
|------|-----------------|---------|-------|
| `hatchling` | 1.32.0 | PEP 517 build backend | **Recommended over setuptools** for this repo's shape — see [Finding 3](#finding-3-hatchling-over-setuptools-for-this-specific-repo-shape). |
| `setuptools` | 84.0.0 | Alternative build backend | Viable, but needs more explicit config here, not less. |
| `pip install -e .` | — | Editable install into the host's venv | The delivery mechanism once packaged. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `pytest` 9.x (repo pins `>=8.0.0`) | Existing 133-test offline suite | CI runs `pytest exercise-ai -q`. Keep `demo/` **outside** `exercise-ai/` and CI needs zero change — see [Integration Points](#integration-points-with-the-existing-layout). |
| GitHub Actions (`actions/checkout@v7`, `actions/setup-python@v7`) | Existing CI | Untouched by v2.0 if the demo lives at repo root. |

---

## Installation

```bash
# v2.0 adds nothing. This is the existing, unchanged install:
pip install -r exercise-ai/requirements.txt

# The demo runs with no install step at all:
python demo/serve.py        # → http://[::1]:8642/
```

---

## Finding 1: The `sys.path` embed strategy is empirically broken

**Confidence: HIGH — directly executed against this repo's `exercise-ai/` directory, not inferred.**

The question was how real the collision risk is for generic names like `models`, `prompts`, `validator`. It is not a theoretical risk; it is a guaranteed failure whenever the host has any module of the same name, and Python's module cache makes it unfixable from the library side.

### Test A — host imports its own `models` first, then the library loads

A throwaway host package with a trivial `models.py` was put on `sys.path` and imported. Then the library directory was inserted at **position 0** of `sys.path` (exactly what `main.py` lines 15–17 and `tests/conftest.py` lines 11–13 do) and `from models import GenerationRequest` was attempted:

```
host imported models from: ...\collide\host\models.py
after lib path insert, 'models' resolves to: ...\collide\host\models.py
same object (cached in sys.modules)? True
GenerationRequest import FAILED: ImportError cannot import name 'GenerationRequest'
    from 'models' (...\collide\host\models.py)
```

**`sys.path.insert(0, ...)` does not help.** Once `sys.modules["models"]` is populated, `sys.path` is never consulted again for that name. The library gets the host's module and raises `ImportError`.

### Test B — library loads first, then the host imports its own `models`

Same setup, reversed order:

```
lib imported models from: ...\exercise-ai\models.py
host now gets 'models' from: ...\exercise-ai\models.py
HOST_MARKER present? False
```

**This is the dangerous direction.** The host's own `models` module is silently replaced by ours. The host does not get an import error at the seam — it gets *our* module, and fails later somewhere unrelated, in its own production code. A generator library that corrupts the host's model layer is a far worse outcome than one that refuses to import.

### How likely is a collision, concretely?

Seven of the eight current top-level module names are real published PyPI distributions, which is a decent proxy for "this name is generic enough that someone else already used it":

| Module | Exists as a PyPI distribution? |
|--------|-------------------------------|
| `models` | yes (0.9.7) |
| `prompts` | yes (0.0.1) |
| `validator` | yes (0.7.1) |
| `wizard` | yes (0.1.dev) |
| `generator` | yes (0.1-alpha) |
| `reliability` | yes (0.9.0) |
| `reasoning` | yes (0.1.0) |
| `failover` | no |

And `models.py` specifically is close to a convention in Django/SQLAlchemy/FastAPI codebases — the most likely shape for "another already-in-production system". `service.py`, the new v2.0 module, is in the same generic-name family.

### What this means for the three options in the question

| Option | Verdict | What actually breaks |
|--------|---------|----------------------|
| Host does `sys.path.insert` | **Does not work.** Not "risky" — broken in both import orders (Tests A and B). | `ImportError` at our seam, or silent replacement of the host's modules. Unfixable from our side because `sys.modules` is a single flat global namespace. |
| Host vendors the `exercise-ai/` folder | **Does not work as-is.** | Vendoring copies the *same* flat top-level names into the host tree — identical collision. It also cannot be imported as a package at all: `exercise-ai` contains a hyphen, so `import exercise-ai` is a **syntax error**. Vendoring only works if the host renames on copy, which is a rename the host now owns and must redo on every update. |
| `pyproject.toml` + rename to `exercise_ai/` + `pip install -e .` | **The only option that works.** | Nothing breaks structurally; the migration cost is listed in [Finding 4](#finding-4-what-the-rename-actually-costs-inventory-for-the-later-decision). All modules become `exercise_ai.models`, `exercise_ai.service`, etc. — one namespace the host can't collide with. |

**Constraint check — no contradiction.** Packaging is parked for v2.0 and this research does not ask to un-park it. `service.py` as a clean function boundary is valuable and rename-independent: the rename changes *how the host reaches* `service.generate(...)`, never *what it is*. Building the boundary first and packaging second is the correct order. What this finding changes is only the framing of the parked item: it is not an optional nicety to adopt "if the host prefers", it is required for in-process embedding to function at all.

---

## Finding 2: Minimal correct `pyproject.toml` shape (for the later decision)

**Confidence: HIGH — shapes verified via Context7 against pypa/setuptools and pypa/hatch docs; versions verified against PyPI on 2026-09-16.**

### Recommended shape — hatchling + src-layout

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "exercise-ai"
version = "2.0.0"
description = "Gerador de exercícios de matemática via LLM"
requires-python = ">=3.11"
dependencies = [
    "openai>=1.50.0",
    "google-genai>=1.0.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.scripts]
exercise-ai = "exercise_ai.main:main"

[tool.hatch.build.targets.wheel]
packages = ["src/exercise_ai"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Note the distribution name (`exercise-ai`, hyphen, what you `pip install`) and the import name (`exercise_ai`, underscore, what you `import`) are allowed to differ, and conventionally do. The hyphenated *directory* is the problem; a hyphenated *distribution name* is fine.

### Why src-layout (`src/exercise_ai/`) and not flat (`exercise_ai/` at root)

This is the single highest-value detail in this section, because it defends against exactly the bug class in Finding 1. With a flat layout, the package is importable from the repo root **whether or not it is installed** — so tests and the demo pass locally by accidentally importing the source tree, and the packaging breakage only surfaces in the host's environment. `src/` makes the repo root non-importable, which forces every test run to exercise the real installed package. PyPA's own guidance says the same, noting src-layout "prevents accidental distribution of unrelated files" and "requires an editable install to run the package directly from the project root."

It also removes an auto-discovery headache: this repo root contains `skills/`, `.planning/`, `demo/`, and `capturar_saida_erros.py`. Under flat-layout auto-discovery those are all candidates a backend has to be told to ignore.

### Why the console script needs zero code changes

`main.main()` is already written correctly for this:

```261:265:C:\Users\Anglo\documents\cursor\GeradorExercicios\exercise-ai\main.py
def main(argv: list[str] | None = None) -> None:
    """Parse CLI args and run the generation pipeline."""
    if argv is None:
        argv = sys.argv[1:]
```

A console script entry point calls `main()` with no arguments, and `main()` already falls back to `sys.argv[1:]`. So `[project.scripts] exercise-ai = "exercise_ai.main:main"` works as-is, and the wizard dispatch on `argv[0] == "gerar"` (line 267) is preserved automatically.

The CLI surface maps like this:

| Today | After packaging |
|-------|-----------------|
| `python exercise-ai/main.py gerar` | `exercise-ai gerar` |
| `python exercise-ai/main.py --out x.json` | `exercise-ai --out x.json` |
| — (fallback, no install needed) | `python -m exercise_ai.main gerar` |

One cosmetic follow-up: `build_parser()` hardcodes `prog="main.py"`, so `--help` would still print `usage: main.py ...` under the new entry point. Drop the `prog=` and argparse derives it from `sys.argv[0]` correctly for both invocations.

---

## Finding 3: hatchling over setuptools, for this specific repo shape

**Confidence: HIGH for the mechanics, MEDIUM for the recommendation (a judgement call, not a fact).**

Both backends work. The tiebreaker is that this repo's package will **not** sit in a location either backend auto-discovers, so the question is which one expresses "the package is over there" most briefly and least ambiguously.

- **hatchling** — one line: `packages = ["src/exercise_ai"]`. No `setup.py`/`setup.cfg` legacy surface to be tempted by. It is the backend PyPA's own packaging tutorial uses, so newcomers to the repo find matching examples.
- **setuptools** — needs `[tool.setuptools.packages.find]` with an explicit `where`/`include`, and setuptools' flat-layout auto-discovery deliberately *refuses* to guess when it sees multiple top-level candidates (a safety measure against publishing maintenance scripts). Given `skills/`, `demo/`, and `capturar_saida_erros.py` at the root, that refusal would have to be configured around.

"setuptools is already installed" is not an argument in either direction: PEP 517 builds in an isolated environment and fetch the declared backend regardless.

**Choose setuptools instead if** the host team's existing repos standardise on it — backend consistency across a company's repos is worth more than the two lines of config saved here.

---

## Finding 4: What the rename actually costs (inventory for the later decision)

**Confidence: HIGH — derived by reading the repo, not estimated.**

This is the concrete change list so the operator can price the parked decision rather than guess at it.

| # | Change | Where | Notes |
|---|--------|-------|-------|
| 1 | `exercise-ai/` → `src/exercise_ai/`, add `__init__.py` | directory | The hyphen is the blocker; a hyphenated dir can never be a package. |
| 2 | Bare imports → package-qualified | every module (`from models import ...` → `from exercise_ai.models import ...`) | Prefer **absolute** package imports over relative (`from .models import`). PEP 8 prefers absolute, they stay greppable, and they work identically under `python -m`. |
| 3 | Delete the `sys.path.insert` block | `main.py` lines 14–17 | Becomes dead and actively harmful once packaged. |
| 4 | Delete the `sys.path.insert` block | `tests/conftest.py` lines 10–13 | Same. |
| 5 | **Rework `.env` discovery** | `main.py` lines 19–23 | **The non-obvious breakage.** `current_dir = Path(__file__).resolve().parent` becomes a path inside the host's `site-packages`, so `current_dir/.env` and `current_dir.parent/.env` both point into the install tree. The host's `.env` will never be found. Fix: resolve from CWD or an explicit env var, not from `__file__`. Under `pip install -e .` this stays accidentally working, which is precisely why it would be missed until a non-editable install. |
| 6 | `token_usage/` moves to `src/exercise_ai/token_usage/` | directory | Already a real package, so this is a plain move. |
| 7 | CI: add `pip install -e .`, change test command | `.github/workflows/ci.yml` | `pytest exercise-ai -q` → `pytest -q` (with `testpaths` set). |
| 8 | `requirements.txt` → `[project.dependencies]` | `pyproject.toml` | Keep `requirements.txt` as a thin `-e .` pointer if CI habits depend on it. |
| 9 | Drop `prog="main.py"` | `main.py` line 131 | Cosmetic; fixes `--help` under the console script. |

Items 1–4 and 6 are mechanical. **Item 5 is the one that bites**, and it is worth writing down now while it is fresh.

---

## Finding 5: Serving the demo page with stdlib only

**Confidence: HIGH — pattern read from CPython source; behaviour executed and confirmed on this Windows machine.**

### Current best practice, from CPython's own `http.server.__main__`

The canonical pattern (CPython `Lib/http/server.py`) is:

1. `ThreadingHTTPServer`, never bare `HTTPServer`. The stdlib's own rationale: browsers pre-open sockets, "on which HTTPServer would wait indefinitely." A demo on plain `HTTPServer` appears to hang in a real browser.
2. Resolve the address family from `getaddrinfo` and assign it to the **server class** before instantiating.
3. Pass the served directory via the handler's `directory=` kwarg, bound with `functools.partial` — not `os.chdir`.
4. Bracket the host in the URL when it contains a colon: `http://[::1]:8642/`.

### The IPv6 bind — minimal correct form

`HTTPServer.address_family` is `AF_INET` (value `2`), confirmed at runtime. Because it is a **class attribute consulted during `__init__`**, it must be set on the class before the server is constructed — this is why the stdlib writes `ServerClass.address_family, addr = _get_best_family(bind, port)` rather than configuring an instance.

For a fixed `::1` target, the minimal correct form is a two-line subclass:

```python
import functools, socket
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

HOST, PORT = "::1", 8642
DEMO_DIR = Path(__file__).resolve().parent

class DemoServer(ThreadingHTTPServer):
    address_family = socket.AF_INET6

handler = functools.partial(SimpleHTTPRequestHandler, directory=str(DEMO_DIR))
with DemoServer((HOST, PORT), handler) as httpd:
    print(f"Demo em http://[{HOST}]:{PORT}/  (Ctrl+C para parar)")
    httpd.serve_forever()
```

Verified end to end on Windows 10.0.22631:

```
bound: ('::1', 8642, 0, 0) family: 23
GET /index.html -> 200
IPv4 127.0.0.1: NOT reachable -> URLError
```

Note the socket reports a 4-tuple `('::1', 8642, 0, 0)` (flowinfo/scope_id) while a 2-tuple `("::1", 8642)` was passed in — that is fine, `getaddrinfo` fills the rest. No need to construct the 4-tuple by hand.

### Three things not to cargo-cult from the stdlib snippet

1. **Do not import `_get_best_family`.** It is private (leading underscore) with no stability guarantee. If dynamic family resolution is ever wanted, the four-line public equivalent is `socket.getaddrinfo(host, port, type=socket.SOCK_STREAM, flags=socket.AI_PASSIVE)[0]` and take `family` / `sockaddr` from it. For a fixed `::1` demo, the hardcoded `AF_INET6` above is simpler and is the better call.
2. **Do not copy the `DualStackServer` / `IPV6_V6ONLY = 0` block.** That exists in `__main__` for the `--bind ::` (all interfaces) case. Bound to `::1` specifically it buys nothing — the probe confirms `127.0.0.1` remains unreachable either way, because `::1` is the IPv6 loopback, not a dual-stack wildcard. Copying it adds a `setsockopt` inside a bare `contextlib.suppress(Exception)`, i.e. silent noise.
3. **Do not use `--cgi` / `CGIHTTPRequestHandler`.** Deprecated, with `remove=(3, 15)` in the source, and it carries a `SECURITY WARNING: DON'T USE THIS CODE UNLESS YOU ARE INSIDE A FIREWALL` banner. Irrelevant to this demo anyway.

### Static-first, and why

**Recommendation: serve pre-generated files with `SimpleHTTPRequestHandler`; do not write a `do_POST` that calls the LLM.**

The demo's stated job is showing the flow and the JSON the host consumes. A static `index.html` plus a `contrato.json` produced by the existing CLI (`--out`) does that with no API key in the loop, no cost per page refresh, no latency, and no request-handling code to review. If live generation is genuinely wanted later, it is one `do_GET` branch on a `BaseHTTPRequestHandler` subclass calling `service.generate(...)` — but that turns the throwaway demo into something with an error contract, and that is a different conversation.

### Windows-specific notes for the demo

| Note | Detail | Mitigation |
|------|--------|------------|
| UTF-8 / PT-BR content | `mimetypes.guess_type` returns no charset parameter, and `mimetypes` reads the Windows registry, so per-machine extension mappings can vary. On this box `.html`→`text/html`, `.js`→`text/javascript`, `.json`→`application/json` all resolve correctly. | Put `<meta charset="utf-8">` in `index.html` and write demo files as UTF-8 **without BOM**. A BOM was the cause of a `UnicodeEncodeError` during probing — a real trap given `cp1252` consoles on pt-BR Windows. |
| `allow_reuse_address` | `HTTPServer.allow_reuse_address` is `True`, and on Windows `SO_REUSEADDR` permits a *second* process to bind an in-use port (unlike Linux). | Irrelevant for a loopback demo; noted so nobody debugs a phantom "two servers" case. `allow_reuse_port` is `False`, which is correct. |
| Local interpreter drift | The default `python` on this machine is **3.14.0**, while CI pins **3.11**. | The demo code above uses nothing newer than 3.7. But `demo/` should stay out of CI regardless. |

---

## Integration Points with the Existing Layout

| Concern | Recommendation | Why |
|---------|----------------|-----|
| Where `demo/` lives | **Repo root** (`GeradorExercicios/demo/`), not inside `exercise-ai/` | CI runs `pytest exercise-ai -q`, which is already scoped. A root-level `demo/` is invisible to CI with **zero workflow changes** — satisfying "fora do CI" for free. Putting it inside `exercise-ai/` would require a new ignore rule. |
| How `demo/serve.py` reaches the library | `sys.path.insert` is **acceptable here** | This is the one place the anti-pattern is safe: the demo owns its entire process, there is no host, and there are no competing top-level names. The distinction that matters is *who owns the process* — fatal for the host embed (Finding 1), harmless for a throwaway script we launch ourselves. |
| Where `service.py` lives | Alongside the other flat modules in `exercise-ai/` | Consistent with the current layout, and moves cleanly under the rename later. |
| `main.run()` as adapter | Keep `sys.exit`/`print` in `main.run()`, keep them **out** of `service.py` | Already the milestone's stated design and it is the right one: the `sys.exit(1)` calls at `main.py` lines 238/246/254 are exactly what must not reach a host process. |
| `token_usage/` | Leave as-is | Already a real package with `__init__.py`; the only current name that would survive `sys.path` injection intact, and it moves cleanly under a rename. |
| CI | No changes for v2.0 | `pytest exercise-ai -q` covers the new `service.py` tests automatically and ignores `demo/`. |
| Port `8642` | Fine | Unprivileged, unregistered, no conflicts observed. |

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| `http.server` (stdlib) | FastAPI / Flask / Streamlit | Never, for this milestone — violates the zero-new-dependency constraint. Reconsider only if the demo becomes a real product surface with auth, routing, and concurrency, which is explicitly out of scope. |
| `ThreadingHTTPServer` | `HTTPServer` | Never here. `HTTPServer` blocks indefinitely on browser pre-opened sockets; a demo opened in a real browser will look broken. |
| Static demo (`SimpleHTTPRequestHandler` + pre-generated JSON) | Live `do_POST` calling `service.generate()` | Only if the demo must prove end-to-end latency/failover live. Costs an API key per demo run and an HTTP error contract. Defer. |
| Hardcoded `address_family = AF_INET6` | `getaddrinfo`-based family resolution | If the bind address becomes configurable (e.g. `--bind` flag). For a fixed `::1` demo, hardcoding is clearer. |
| hatchling (deferred) | setuptools (deferred) | If the host team's repos already standardise on setuptools. |
| src-layout (deferred) | flat-layout | Only if `src/` is a hard blocker for the host's tooling. Costs you the "accidental import from CWD" protection that this project specifically needs. |
| Do nothing now (packaging parked) | Rename in v2.0 | If the host's stack becomes known mid-milestone **and** the host's codebase contains a top-level `models`/`service`/`validator`. Then packaging stops being deferrable, because the integration cannot ship without it. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| FastAPI / Flask / Streamlit for the demo | Violates the zero-new-dependency constraint; adds an install step and a server lifecycle for a throwaway page | `http.server.ThreadingHTTPServer` |
| Host-side `sys.path.insert` as the embed contract | **Empirically broken in both import orders** (Finding 1). Fails with `ImportError`, or worse, silently replaces the host's own modules | `service.generate(...)` behind a proper package once packaging is un-parked |
| Vendoring `exercise-ai/` into the host tree | Same flat-name collision, plus `exercise-ai` is not a legal identifier (hyphen), so it can never be imported as a package | Same as above |
| `http.server._get_best_family` | Private API, no stability guarantee | `socket.getaddrinfo(..., flags=socket.AI_PASSIVE)`, or hardcode `socket.AF_INET6` |
| `DualStackServer` / `IPV6_V6ONLY = 0` | Only meaningful when binding `::` (all interfaces). No effect when binding `::1` — verified | Plain `address_family = socket.AF_INET6` |
| `CGIHTTPRequestHandler` / `--cgi` | Deprecated with `remove=(3, 15)`; carries an explicit stdlib security warning | `SimpleHTTPRequestHandler` |
| `os.chdir()` to set the served directory | Process-global mutation; corrupts relative paths elsewhere (this project resolves `.env` and `exercicios-gerados/` relatively) | `functools.partial(SimpleHTTPRequestHandler, directory=...)` |
| Binding `0.0.0.0` or `::` for the demo | Exposes an unauthenticated file server to the LAN; stdlib docs note it implements only basic security checks | `::1` (loopback only) |
| A `Settings` object | Explicitly rejected this milestone; env vars remain the config source | `os.getenv` as today |
| LangChain / CrewAI / AutoGen / RAG / vector DB / queues | Out of scope per project rules; nothing in this milestone needs them | The existing direct-SDK pipeline |
| New generic top-level module names | Each one adds collision surface (`service` is in the same family as `models`/`validator`) | Accept for v2.0 — the rename fixes all of them at once. Just do not add more than necessary. |

---

## Stack Patterns by Variant

**If the host's stack turns out to have no top-level `models` / `service` / `validator` / `prompts`:**
- `sys.path` injection will *appear* to work
- Treat that as luck, not a decision. It breaks the first time either codebase adds such a file, and the failure mode (Test B: silent replacement of host modules) surfaces far from the cause.

**If the host's stack is Django / FastAPI / SQLAlchemy (very likely to have a top-level `models`):**
- Un-park packaging immediately; it is the precondition for the integration, not a polish item
- Ship `src/exercise_ai/` + hatchling + `pip install -e .` before the first real host integration attempt

**If the demo must eventually show live generation:**
- Add one `do_GET` branch on a `BaseHTTPRequestHandler` subclass calling `service.generate(...)`
- Still stdlib-only, still `::1`, still out of CI
- Budget for an error contract (what HTTP status for a provider failure?), which is why static-first is recommended now

**If the host cannot accept a `src/` layout:**
- Flat `exercise_ai/` at repo root with `packages = ["exercise_ai"]` works
- You lose the "accidental import from CWD" protection, so compensate by running CI tests against an installed (non-editable) wheel at least once

---

## Version Compatibility

| Package | Compatible with | Notes |
|---------|-----------------|-------|
| Python 3.11 (CI pin) | everything recommended here | `SimpleHTTPRequestHandler(directory=)` needs 3.7+; `ThreadingHTTPServer` needs 3.7+. Large margin. |
| Python 3.14.0 (local default on this machine) | same | The `_get_best_family` / `address_family` pattern verified unchanged from 3.11 through 3.14. Local/CI drift exists but does not affect anything in this milestone. |
| `hatchling` 1.32.0 | Python 3.11+ | Deferred. |
| `setuptools` 84.0.0 | Python 3.11+ | Deferred. Auto-discovery behaviour referenced here is 61.0.0+. |
| `pydantic` 2.13.5 (repo pins `>=2.0.0`) | current code | No v2.0 change. `model_dump()` is the serialization path the demo JSON reuses. |
| `openai` 3.14.1 (repo pins `>=1.50.0`) | current code | **Out of scope for v2.0, flagged only.** The pin is `>=1.50.0` and the published major is now 3.x, so a fresh `pip install` resolves across two major boundaries. Not a v2.0 task — but it is an unbounded pin on the critical path and belongs in the backlog. |
| `google-genai` 2.23.0 (repo pins `>=1.0.0`) | current code | Same unbounded-pin observation, one major boundary. |
| `python-dotenv` 1.2.3 | current code | Fine. |
| `pytest` 9.1.1 (repo pins `>=8.0.0`) | 133-test suite | Major boundary crossed by the pin; CI is currently green so no action, noted for awareness. |

---

## Sources

- **Executed locally on Windows 10.0.22631** — IPv6 `::1` bind, 200 response, IPv4 unreachability, `address_family` default, `allow_reuse_address`/`allow_reuse_port`, `mimetypes` resolution, and both module-shadowing probes against this repo's real `exercise-ai/` — HIGH
- **CPython `Lib/http/server.py` (3.13 branch, read in full)** — `_get_best_family`, `test()`, `DualStackServer`, `ThreadingHTTPServer` rationale, `CGIHTTPRequestHandler` deprecation `remove=(3, 15)`, CGI security banner — HIGH
- **Context7 `/websites/python_3_library`** — `http.server` CLI surface (`--bind`, `--directory`, `--protocol`), `ThreadingHTTPServer` docs, `socket.has_dualstack_ipv6`, `socket.create_server` — HIGH
- **Context7 `/pypa/setuptools`** — `pyproject.toml` shape, `[project.scripts]`, package discovery, flat-layout vs src-layout, editable install modes and limitations — HIGH
- **Context7 `/pypa/hatch`** — hatchling `[build-system]`, full `pyproject.toml` example, `[tool.hatch.build.targets.wheel] packages` path anchoring — HIGH
- **PyPI JSON API, queried 2026-09-16** — current versions of setuptools/hatchling/pydantic/openai/google-genai/pytest/python-dotenv, and existence of the eight generic module names as distributions — HIGH
- **Repo files read** — `.planning/PROJECT.md`, `exercise-ai/main.py`, `exercise-ai/tests/conftest.py`, `.github/workflows/ci.yml`, `exercise-ai/requirements.txt`, directory listings — HIGH
- **Python import system reference (docs.python.org)** — `sys.modules` caching semantics that make the shadowing unfixable from the library side — HIGH
- **PyPA packaging guides (namespace packages, src-layout)** — layout rationale — MEDIUM (guidance, not a hard API contract)

---
*Stack research for: embedding an existing Python LLM pipeline as an in-process library*
*Researched: 2026-09-16*
