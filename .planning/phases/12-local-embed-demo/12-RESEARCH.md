# Phase 12: Local Embed Demo - Research

**Researched:** 2026-09-18
**Domain:** Stdlib IPv6 loopback HTTP demo consuming Phase 11 `generate_batch` embed contract
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Page composition
- **D-01:** Primary surfaces are the form and rendered exercises; contract JSON is secondary — **Reversibility:** reversible
- **D-02:** Results area uses tabs **Exercícios | JSON** (switching replaces the view; not an inline toggle) — **Reversibility:** reversible
- **D-03:** Before first success: Exercícios empty; JSON tab shows a schema/shape hint of `ExerciseBatch` fields (no fake exercise data) — **Reversibility:** reversible
- **D-04:** UI chrome in Portuguese; technical identifiers (exception class names, `GenerationRequest` / JSON field names, `kind`) stay in English as in the Python contract — **Reversibility:** reversible

#### Form field set
- **D-05:** Form exposes the four `GenerationRequest` fields **plus** provider and reasoning; demo sets env then calls `generate_batch` (provider/reasoning are not part of the request object) — **Reversibility:** reversible
- **D-06:** Two labeled sections: **Contrato (`GenerationRequest`)** vs **Ambiente (só nesta demo)** with an explicit note that env controls are not in the batch JSON — **Reversibility:** reversible
- **D-07:** Demo-ready presets on first load (e.g. Matemática / equação do 1º grau / médio / quantidade 2) so one click generates — **Reversibility:** reversible
- **D-08:** Provider/reasoning controls mirror the wizard: openai|gemini|grok + empty/auto; reasoning none|low|medium|high with default medium — **Reversibility:** reversible

#### Busy & error UX
- **D-09:** While generating: disable submit button and show **Gerando…**; leave other fields editable (server Lock still returns 409 if concurrent) — **Reversibility:** reversible
- **D-10:** Errors show a badge with the exception class (`ConfigError` / `InvalidRequestError` / `GenerationFailedError`) plus the PT human message, and `kind` when present — **Reversibility:** reversible
- **D-11:** HTTP 409 uses an explicit sequential-contract message including **HTTP 409** (not a soft “please wait” only) — **Reversibility:** reversible
- **D-12:** On failure after a prior success: keep last good Exercícios/JSON; show error banner above — **Reversibility:** reversible

#### Throwaway chrome
- **D-13:** Persistent top banner **and** footer footnote (throwaway / delete at v2.0 close / loopback-only URL) — **Reversibility:** reversible
- **D-14:** `demo/README.md` includes the full anti-accretion pack: expiry/delete-at-close, literal `http://[::1]:8642/` (never `localhost`), `netstat` check, not-for-staging, no CI / no deps — **Reversibility:** reversible
- **D-15:** Root `README.md` Embed section gets a short pointer to `demo/` and the loopback URL with delete-at-close note — **Reversibility:** reversible
- **D-16:** Top banner is dismissible for the browser session (X until reload); footnote remains — **Reversibility:** reversible

#### Already locked (carry forward — do not re-litigate)
- Bind `[::1]:8642` via `ThreadingHTTPServer` + `AF_INET6`; refuse non-loopback bind
- Sequential generation: Lock → HTTP 409 when busy
- POST generation requires `application/json` + Host/Origin allowlist
- Stdlib only; outside package and CI; `load_dotenv` only in demo `__main__`
- Render exercises + `ExerciseBatch.model_dump()` only — never stderr/diagnostics/env values
- Consume Phase 11 `generate_batch` + three error subclasses unchanged

### the agent's Discretion
- Exact preset topic string and inline CSS/JS structure (single file vs few static files under `demo/`)
- Exact schema-hint wording for the empty JSON tab
- Visual styling of banner/badges/tabs (keep throwaway-simple; no design system)
- How provider empty/auto is represented in the HTML control (empty option vs “auto” label)

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.

(Already deferred at milestone level, unchanged: PKG-01, OBS-01, LOG-01, SEED-003 B/C.)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DEMO-01 | Página local em `demo/` (`http://[::1]:8642/`, stdlib only, fora do CI) mostra form CLI-equivalente, exercícios renderizados, JSON bruto, estado "Gerando…" e erro por categoria | Stdlib `ThreadingHTTPServer` + handler POST → `generate_batch`; form sections Contrato/Ambiente; tabs Exercícios\|JSON; busy/error badges mapped to three exception classes |
| DEMO-02 | Servidor recusa bind não-loopback; enforce sequencial com Lock → HTTP 409; exige `application/json` + Host/Origin allowlist no POST de geração; banner throwaway + nota de expiração no README | `ipaddress.is_loopback` refuse-to-start; `Lock.acquire(blocking=False)` → 409; Host/Origin/Content-Type guards; `demo/README.md` anti-accretion + root README pointer |
</phase_requirements>

## Project Constraints (from AGENTS.md)

Actionable directives the planner must not violate:

- **Tech stack:** Python; no agent frameworks (LangChain / CrewAI / AutoGen) — demo uses stdlib `http.server` only for the HTTP surface.
- **Simplicity / YAGNI:** each file single responsibility; no productizing the demo into a real API.
- **Security:** API keys in `.env`, never in code or logs; never render env values or stderr diagnostics in the page.
- **Reliability:** LLM is not source of truth; structural validation already lives in the pipeline — demo only displays validated `ExerciseBatch` or typed errors.
- **Retries:** max 1–2 regenerations already in service; demo must not invent retry loops.
- **Testability:** validator (and demo guards) testable without external API where possible.
- **Stack pins:** `openai` ≥1.50, `pydantic` ≥2.0, `python-dotenv` ≥1.0, `pytest` ≥8.0 — **no new runtime deps for Phase 12**.
- **GSD workflow:** planning artifacts stay in sync; demo lives outside package and CI.

## Summary

Phase 12 is a **throwaway stdlib consumer** of the Phase 11 embed seam. Experts build it as a tiny `demo/` tree at repo root: `ThreadingHTTPServer` subclass with `address_family = socket.AF_INET6` bound to `("::1", 8642)`, a request handler that serves static UI and one JSON POST route that sets provider/reasoning env then calls `service.generate_batch`, and a module-level `threading.Lock` with `acquire(blocking=False)` so concurrent generation returns **HTTP 409** without blocking static GETs.

Prior STACK research floated a static-only page; that is **superseded** by locked DEMO-01/DEMO-02 and CONTEXT (live form → generation → tabs). Packaging stays parked: the demo owns the process and may `sys.path.insert` `exercise-ai/` exactly as `main.py` / README describe. `load_dotenv` runs only under demo `__main__`. No FastAPI, no dual-stack wildcards, no stderr panel, no CI job.

**Primary recommendation:** Implement `demo/serve.py` as AF_INET6 `ThreadingHTTPServer` + handler subclass; Lock only around `generate_batch`; Host=`[::1]:8642` / Origin=`http://[::1]:8642` / Content-Type `application/json`; PT UI with EN contract identifiers; full anti-accretion docs.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Bind + refuse non-loopback | API / Backend | — | Server process owns socket family and start-time assert |
| Serve static HTML/CSS/JS | CDN / Static (local) | Browser / Client | Files from `demo/`; browser renders |
| Form + tabs + Gerando… UX | Browser / Client | — | Busy state and last-success retention are client-side |
| POST /gerar + Host/Origin/JSON guards | API / Backend | — | CSRF/loopback spend controls must be server-enforced |
| Sequential Lock → 409 | API / Backend | — | Enforces process-level sequential contract |
| `generate_batch` + env provider/reasoning | API / Backend | — | Library seam; demo sets env then calls |
| Anti-accretion banner/README | CDN / Static (local) | — | Operator-facing docs/chrome only |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.11+ (CI pin `3.11`; local probe `3.14.0`) | Runtime | Project pin; demo APIs need only 3.7+ |
| `http.server.ThreadingHTTPServer` | stdlib | Concurrent request threads | Browsers pre-open sockets; bare `HTTPServer` waits indefinitely [CITED: docs.python.org/3.16/library/http.server.html] |
| `socket.AF_INET6` | stdlib | IPv6 loopback bind | `HTTPServer.address_family` defaults to `AF_INET` (value `2`) — must set class attr before construct [VERIFIED: local probe + `.planning/research/STACK.md:247-260`] |
| `threading.Lock` | stdlib | Sequential generation | `acquire(blocking=False)` → False when busy → HTTP 409 [CITED: docs.python.org/3.16/library/threading.html] |
| `ipaddress` | stdlib | Refuse non-loopback bind | `ip_address(host).is_loopback` — `::1` True, `0.0.0.0`/`::` False [CITED: docs.python.org/3.16/library/ipaddress.html] [VERIFIED: local probe] |
| `json` | stdlib | Request/response bodies | Match CLI `model_dump()` path |
| `functools.partial` | stdlib | Pin handler `directory=` | Avoid process-global `os.chdir` [CITED: STACK Finding 5] |
| Existing `exercise-ai` stack | as in `requirements.txt` | Generation | Demo imports `service` / `models`; does not add packages |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `python-dotenv` | ≥1.0.0 (already installed) | Load `.env` in demo `__main__` only | Never on `service` import; never inside handler module import path used by tests |
| `pytest` | ≥8.0 | Offline unit tests for pure guards | Optional `pytest demo -q` locally — **not** wired into CI |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `ThreadingHTTPServer` + Lock | FastAPI / Flask | Forbidden — new deps + product surface |
| `AF_INET6` + `::1` | Dual-stack `::` / `0.0.0.0` | Exposes LAN; violates refuse-to-start |
| Live POST → `generate_batch` | Static `contrato.json` only | Superseded by DEMO-01 locked live flow |
| Separate asset files | Fully inline HTML | Both OK (discretion); ThreadingHTTPServer unblocks assets either way |
| Package install `exercise_ai` | `sys.path.insert` | Packaging parked; demo owns process [VERIFIED: README.md:111-121] |

**Installation:** none — stdlib + existing `exercise-ai/requirements.txt`.

```bash
# No new packages. Run from repo root after keys exist in .env:
python demo/serve.py   # → http://[::1]:8642/
```

## Package Legitimacy Audit

> Phase installs **zero** new packages. Existing deps unchanged.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| — | — | — | — | — | N/A | No install this phase |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```text
Browser (operator)
  │  GET /  (static index.html [+ js/css])
  │  POST /gerar  Content-Type: application/json
  │       Host: [::1]:8642
  │       Origin: http://[::1]:8642  (if present)
  ▼
DemoServer (ThreadingHTTPServer, address_family=AF_INET6)
  bind ("::1", 8642) ──► start check: ipaddress.is_loopback else refuse
  │
  ├─ GET * ──► SimpleHTTPRequestHandler.directory=demo/  (NO lock)
  │
  └─ POST /gerar
        │
        ├─ Host allowlist? ──no──► 403
        ├─ Origin allowlist (if header)? ──no──► 403
        ├─ Content-Type application/json? ──no──► 415 (or 400)
        ├─ Lock.acquire(blocking=False)? ──no──► 409 + PT sequential message
        │
        ├─ parse JSON → GenerationRequest fields
        ├─ set/clear LLM_PROVIDER + LLM_REASONING_EFFORT from Ambiente
        ├─ generate_batch(request)  ──► ExerciseBatch | ConfigError |
        │                               InvalidRequestError |
        │                               GenerationFailedError
        ├─ Lock.release()
        └─ JSON response { ok, batch | error{class, message, kind?} }
              │
              ▼
Browser: tabs Exercícios | JSON; badges; keep last success on failure
```

External: LLM providers via existing pipeline (keys from `.env` loaded only in demo `__main__`).

### Recommended Project Structure

```text
demo/                          # NEW — repo root, outside exercise-ai/, outside CI
├── serve.py                   # __main__: load_dotenv, loopback assert, serve_forever
├── index.html                 # PT UI: banner, form sections, tabs, footnote
├── app.js                     # optional (discretion) — fetch, tabs, busy/error
├── README.md                  # full anti-accretion pack
└── tests/                     # optional offline guard unit tests (NOT in CI)
    └── test_guards.py

README.md                      # Embed section: short pointer to demo/
# exercise-ai/ unchanged for this phase (consume only)
```

**Filename note:** SUMMARY mentions `demo/server.py`; STACK run command uses `demo/serve.py`. Prefer **`serve.py`** to match STACK's verified invocation string; either is fine if README documents the literal command. [CITED: `.planning/research/SUMMARY.md:59`] [CITED: `.planning/research/STACK.md:62-63`]

### Pattern 1: AF_INET6 ThreadingHTTPServer subclass

**What:** Set `address_family` on the **class** before construction; bind `("::1", 8642)`.
**When to use:** Always for this demo (locked).
**Example:**

```python
# Source: .planning/research/STACK.md Finding 5 (verified on Windows);
# ThreadingHTTPServer rationale: docs.python.org/3.16/library/http.server.html
import functools
import ipaddress
import socket
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST, PORT = "::1", 8642
DEMO_DIR = Path(__file__).resolve().parent

class DemoServer(ThreadingHTTPServer):
    address_family = socket.AF_INET6

def assert_loopback(host: str) -> None:
    if not ipaddress.ip_address(host).is_loopback:
        raise SystemExit(f"Recusa bind não-loopback: {host!r}")

# In __main__ only:
assert_loopback(HOST)
handler = functools.partial(SimpleHTTPRequestHandler, directory=str(DEMO_DIR))
# Prefer a subclass of SimpleHTTPRequestHandler that adds do_POST — see Pattern 2
with DemoServer((HOST, PORT), handler) as httpd:
    print(f"Demo em http://[{HOST}]:{PORT}/  (Ctrl+C para parar)")
    httpd.serve_forever()
```

### Pattern 2: Lock only around generation (not static)

**What:** Module-level `Lock`; non-blocking acquire on POST generate; always release in `finally`.
**When to use:** Every live generation path.
**Example:**

```python
# Source: docs.python.org/3.16/library/threading.html — acquire(blocking=False)
import threading

_GEN_LOCK = threading.Lock()

def handle_gerar(...):
    if not _GEN_LOCK.acquire(blocking=False):
        # HTTP 409 — message MUST include literal "HTTP 409" (D-11)
        return 409, {"ok": False, "error": {...}}
    try:
        batch = generate_batch(request)
        return 200, {"ok": True, "batch": batch.model_dump()}
    finally:
        _GEN_LOCK.release()
```

Static `do_GET` must **not** take the lock. [CITED: `.planning/research/PITFALLS.md` Pitfall 12]

### Pattern 3: Import `generate_batch` via flat `sys.path`

**What:** Demo owns the process; insert `exercise-ai/` then import flat modules.
**When to use:** Demo entry only (packaging parked).
**Verified contract:**

```python
# Source: README.md Embed section [VERIFIED: README.md:117-129]
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "exercise-ai"))

from models import GenerationRequest, DificuldadeEnum
from service import (
    generate_batch,
    ConfigError,
    InvalidRequestError,
    GenerationFailedError,
)
```

Mirror `main.py` path bootstrap style [VERIFIED: `exercise-ai/main.py:14-17`]:

```python
current_dir = Path(__file__).resolve().parent
# for demo: package_dir = current_dir.parent / "exercise-ai"
```

### Pattern 4: Provider/reasoning via env (not request fields)

**What:** Form sends provider/reasoning; demo mutates env then builds `GenerationRequest` with only the four contract fields.
**When to use:** Always (D-05/D-08).

Wizard parity sets [VERIFIED: `exercise-ai/wizard.py:40-42`]:

```python
_VALID_PROVIDER = frozenset({"openai", "gemini", "grok"})
_VALID_REASONING = frozenset({"none", "low", "medium", "high"})
```

Empty provider → return `None` / leave unset for auto-detect [VERIFIED: `exercise-ai/wizard.py:129-136`]. Empty reasoning → `"medium"` [VERIFIED: `exercise-ai/wizard.py:143-148`].

Env keys restored by service after each call [VERIFIED: `exercise-ai/service.py:14`]:

```python
_SCOPED_ENV_KEYS = ("LLM_PROVIDER", "LLM_REASONING_EFFORT")
```

Demo should set/clear those keys **before** `generate_batch` (same pattern as CLI [VERIFIED: `exercise-ai/main.py:317-326`]). Prefer demo-local save/restore around the call so leftover env does not leak across form submissions when switching auto ↔ explicit. [ASSUMED] — CLI leaves env set; demo UX benefits from per-request scope.

### Anti-Patterns to Avoid

- **Bare `HTTPServer`:** browser pre-open hang [CITED: http.server docs].
- **Bind `""` / `0.0.0.0` / `::` to "make localhost work":** LAN exposure [CITED: PITFALLS 13].
- **Write `localhost` in docs/UI:** IPv4-first resolve → connection refused → operator broadens bind [CITED: PITFALLS 13].
- **Lock around all requests:** freezes assets; use Lock only on generate [CITED: PITFALLS 12].
- **Render stderr / env values:** ships batches and secrets to the screen [CITED: PITFALLS 15].
- **`load_dotenv` on `service` import or demo module import:** reintroduces import-time side effects [CITED: CONTEXT already locked; Phase 11 D-15].
- **FastAPI / dual-stack DualStackServer / CGIHTTPRequestHandler:** explicitly out [CITED: STACK Finding 5].
- **Add demo to CI / put under `exercise-ai/`:** violates fora do CI; CI is `pytest exercise-ai -q` [VERIFIED: `.github/workflows/ci.yml:28-29`].

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Concurrent HTTP while LLM runs | Custom async framework | `ThreadingHTTPServer` | Stdlib rationale for browser sockets |
| Sequential contract | Queue + worker process | `threading.Lock` + 409 | Demonstrates honest sequential API |
| IPv6 bind | Guess dual-stack flags | Class `address_family = AF_INET6` | Class attr consulted in `__init__` |
| Loopback safety | Firewall rules | `ipaddress.is_loopback` refuse-to-start | Anti-accretion tripwire |
| CSRF / quota burn | Cookie auth | Host + Origin + JSON Content-Type | Three-line allowlist |
| Schema serialization | Custom dict builder | `ExerciseBatch.model_dump()` | Contract the host will consume |
| New web framework | FastAPI/Flask | stdlib handler subclass | Zero deps locked |

**Key insight:** The demo's job is to **teach the embed contract**, not to be a secure multi-user product. Hard controls are loopback refuse-to-start + Host/Origin/JSON + Lock→409 + anti-accretion docs — not a framework.

## Common Pitfalls

### Pitfall 1: Browser hang on bare HTTPServer (PITFALLS 12)
**What goes wrong:** Page spinner; favicon/CSS never arrive during generation.
**Why:** Single-threaded accept loop.
**How to avoid:** `ThreadingHTTPServer` + Lock only on generate; optionally inline CSS/JS.
**Warning signs:** Spinner with no server log; overlapping USAGE runs.

### Pitfall 2: Wrong address family / broad bind (PITFALLS 13)
**What goes wrong:** `("::1", 8642)` fails on default AF_INET; operator binds `0.0.0.0`.
**Why:** `address_family` is a class attribute (default `AF_INET` = 2) [VERIFIED: local probe].
**How to avoid:** Subclass + `AF_INET6`; `assert is_loopback`; document literal `http://[::1]:8642/`; README `netstat` check for `[::1]:8642` not `[::]:8642`.
**Warning signs:** Windows Firewall "Allow access?" dialog; `netstat` shows `0.0.0.0` or `[::]`.

### Pitfall 3: Cross-origin POST burns credits (PITFALLS 14)
**What goes wrong:** Another tab POSTs to `[::1]:8642` with simple Content-Type; generation runs.
**Why:** Loopback ≠ authorization.
**How to avoid:** Host exactly `[::1]:8642`; if `Origin` present must be `http://[::1]:8642`; require `application/json`.
**Warning signs:** Server log Origin from foreign site.

### Pitfall 4: Diagnostics panel (PITFALLS 15)
**What goes wrong:** Full batch / API previews / env on shared screen.
**Why:** Tempting "transparency".
**How to avoid:** Only `model_dump()` + typed error JSON; leave stderr in terminal.
**Warning signs:** `<pre>` of captured stderr; UI listing env var values.

### Pitfall 5: Demo accretion (PITFALLS 17)
**What goes wrong:** Throwaway becomes staging API.
**Why:** Convenient HTTP surface with real keys.
**How to avoid:** Loopback assert; outside package/CI; loud banner+footnote; README expiry.
**Warning signs:** PRs adding auth/routes/deps to `demo/`.

### Pitfall 6: Importing `main` from demo
**What goes wrong:** Import-time `load_dotenv` + CLI coupling.
**Why:** `main.py` loads dotenv at import [VERIFIED: `exercise-ai/main.py:19-23`].
**How to avoid:** Import `service` / `models` only; dotenv solely in demo `__main__`.

### Pitfall 7: Treating STACK "static-first" as still authoritative
**What goes wrong:** Planner ships static JSON only and fails DEMO-01.
**Why:** STACK Finding 5 predated locked live-demo CONTEXT.
**How to avoid:** Honor CONTEXT/DEMO-01 live POST; treat static-first as historical alternative.

### Pitfall 8: Gemini hang (historical)
**What goes wrong:** PITFALLS 12 claimed no Gemini timeout.
**Status:** Phase 11 fixed — `HttpOptions.timeout=30000` [VERIFIED: `exercise-ai/generator_gemini.py:80-89`] [VERIFIED: README.md:171-173]. Demo does not re-fix; still expect multi-minute worst case.

## Code Examples

### Exception → badge payload

```python
# Source: exercise-ai/service.py [VERIFIED: service.py:17-47, 73-91]
try:
    batch = generate_batch(request)
except ConfigError as e:
    payload = {"class": "ConfigError", "message": str(e), "kind": e.kind}
except InvalidRequestError as e:
    payload = {"class": "InvalidRequestError", "message": str(e), "kind": e.kind}
except GenerationFailedError as e:
    payload = {
        "class": "GenerationFailedError",
        "message": str(e),
        "kind": getattr(e, "api_error_kind", None),
    }
```

`GenerationFailedError` uses `api_error_kind`, not `kind` [VERIFIED: `exercise-ai/service.py:36-47`]. UI should show `kind` when present (D-10) — map `api_error_kind` into the displayed kind field for that class.

### GenerationRequest / ExerciseBatch shapes

```python
# [VERIFIED: exercise-ai/models.py:7-11, 15-28, 41-50]
# DificuldadeEnum: "facil" | "medio" | "dificil"
# MAX_QUANTIDADE = 40
# GenerationRequest: materia, topico, dificuldade, quantidade (ge=1, le=40)
# Exercise: enunciado, resposta, explicacao
# ExerciseBatch: exercicios: list[Exercise]
```

Schema hint for empty JSON tab (discretion wording) should list those field names in English — no fake exercises (D-03).

### Minimal HTML structure (prescriptive skeleton)

```html
<!-- Discretion: single file vs split JS. Keep throwaway-simple. -->
<header id="throwaway-banner">… throwaway / delete-at-close / http://[::1]:8642/ … <button type="button">×</button></header>
<form id="gerar-form">
  <fieldset><legend>Contrato (GenerationRequest)</legend>
    <!-- materia, topico, dificuldade, quantidade — presets on load -->
  </fieldset>
  <fieldset><legend>Ambiente (só nesta demo)</legend>
    <p>… estes controles NÃO entram no JSON do lote …</p>
    <!-- provider: empty/auto | openai | gemini | grok -->
    <!-- reasoning: none | low | medium | high (default medium) -->
  </fieldset>
  <button type="submit">Gerar</button> <!-- disabled + label Gerando… while busy -->
</form>
<div id="error-badge" hidden></div> <!-- class name EN + PT message + kind -->
<nav role="tablist">
  <button data-tab="exercicios">Exercícios</button>
  <button data-tab="json">JSON</button>
</nav>
<section id="tab-exercicios"><!-- empty until first success; keep last on later failure --></section>
<section id="tab-json"><!-- schema hint until first success; then model_dump() --></section>
<footer>… footnote always visible …</footer>
```

Client: `fetch("/gerar", { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify(...) })`. On 409, show message containing **HTTP 409**. On failure after success, do not clear prior tab content (D-12).

### Host / Origin / Content-Type checks

```python
# Prescriptive allowlists from PITFALLS 14 [CITED]
ALLOWED_HOST = "[::1]:8642"
ALLOWED_ORIGIN = "http://[::1]:8642"

def _check_post_headers(handler) -> int | None:
    host = handler.headers.get("Host", "")
    if host != ALLOWED_HOST:
        return 403
    origin = handler.headers.get("Origin")
    if origin is not None and origin != ALLOWED_ORIGIN:
        return 403
    ctype = (handler.headers.get("Content-Type") or "").split(";")[0].strip().lower()
    if ctype != "application/json":
        return 415  # [ASSUMED] status; PITFALLS require enforce, not exact code
    return None
```

Absent `Origin` is allowed (direct navigation / same-origin fetch without Origin in some agents) [CITED: PITFALLS 14].

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Static `contrato.json` demo (STACK Finding 5) | Live POST → `generate_batch` | Phase 12 CONTEXT lock | Demo is acceptance of embed seam |
| Bare `HTTPServer` | `ThreadingHTTPServer` + Lock→409 | Research / PITFALLS 12 | Assets stay responsive; sequential enforced |
| Gemini client no timeout | `HttpOptions.timeout=30000` | Phase 11 | Demo no longer blocked on infinite hang |
| Packaging `exercise_ai` | Parked; `sys.path` | Milestone | Demo-only path; host still blocked until PKG-01 |

**Deprecated/outdated for this phase:**
- Static-only demo as the Phase 12 deliverable
- DualStackServer / `IPV6_V6ONLY=0` for `::1`
- `CGIHTTPRequestHandler`

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Wrong Content-Type → HTTP **415** (vs 400) | Architecture / Code Examples | Cosmetic; either acceptable if documented |
| A2 | Demo should save/restore env per request beyond service `_scoped_env` | Pattern 4 | Leftover `LLM_PROVIDER` across form submits if only CLI-style set-and-leave |
| A3 | POST path `/gerar` (vs `/api/gerar`) | Architecture | Must match client `fetch` URL — pick one in plan |
| A4 | Entry filename `serve.py` preferred over `server.py` | Structure | Docs inconsistency only |

**If wrong:** planner picks explicit values in PLAN.md (status codes, route path, filename).

## Open Questions

1. **POST route path**
   - What we know: need one JSON generation endpoint
   - What's unclear: `/gerar` vs `/api/gerar`
   - Recommendation: `/gerar` (PT, short, matches button label) — lock in plan

2. **HTTP status for bad Content-Type / Host**
   - What we know: 409 locked for busy; 403 for bad Origin/Host in PITFALLS
   - What's unclear: 415 vs 400 for Content-Type
   - Recommendation: 403 Host/Origin, 415 Content-Type, 400 JSON parse / validation before service

3. **Whether to ship `demo/tests/`**
   - What we know: demo fora do CI; nyquist wants Validation Architecture
   - What's unclear: how strictly to automate guard tests
   - Recommendation: Wave 0 adds pure-function unit tests under `demo/tests/` run manually / optional local pytest; **do not** change `.github/workflows/ci.yml`

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | demo server | ✓ | 3.14.0 local / 3.11 CI pin | — |
| stdlib `http.server` / `threading` / `ipaddress` / `socket` | DEMO-02 | ✓ | stdlib | — |
| `exercise-ai` imports via sys.path | DEMO-01 | ✓ | present | — |
| `python-dotenv` | load `.env` in `__main__` | ✓ | in requirements | Fail loud if missing keys |
| LLM API keys in `.env` | live generation smoke | operator machine | — | Unit tests mock `generate_batch`; manual UAT needs keys |
| IPv6 loopback `::1` | bind | ✓ (STACK verified Windows) | — | No IPv4 alternative in scope |

**Missing dependencies with no fallback:** none for coding; live UAT needs operator `.env` keys.

**Missing dependencies with fallback:** live LLM — mock in unit tests of handler error mapping.

Step 2.6: external tools probed — Python + stdlib OK; no Docker/DB required.

## Validation Architecture

> `workflow.nyquist_validation` is `true` in `.planning/config.json` [VERIFIED: `.planning/config.json:11`].

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest ≥8.0 (existing) |
| Config file | none project-wide — discovery via `pytest exercise-ai` |
| Quick run command | `pytest demo/tests -q` (once Wave 0 exists; **not CI**) |
| Full suite command | `pytest exercise-ai -q` (unchanged; must stay green; ignores `demo/`) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DEMO-02 | `is_loopback` refuse for `0.0.0.0` / `::` | unit | `pytest demo/tests/test_guards.py::test_refuse_non_loopback -x` | ❌ Wave 0 |
| DEMO-02 | Host/Origin/Content-Type allowlist decisions | unit | `pytest demo/tests/test_guards.py::test_headers -x` | ❌ Wave 0 |
| DEMO-02 | Lock busy → 409 mapping (pure helper or handler with mocked generate) | unit | `pytest demo/tests/test_guards.py::test_lock_409 -x` | ❌ Wave 0 |
| DEMO-01 | Exception class → error JSON shape | unit | `pytest demo/tests/test_error_map.py -x` | ❌ Wave 0 |
| DEMO-01 | Form/tabs/Gerando…/live LLM | manual UAT | Operator opens `http://[::1]:8642/` | N/A manual |
| DEMO-02 | Banner + README anti-accretion | manual / doc check | Read `demo/README.md` + UI | N/A manual |
| — | CI unchanged (`pytest exercise-ai -q` only) | regression | `pytest exercise-ai -q` | ✅ `.github/workflows/ci.yml` |

### Sampling Rate

- **Per task commit:** `pytest demo/tests -q` when demo tests exist; else `pytest exercise-ai/tests/test_service.py -q` smoke that import path still works
- **Per wave merge:** `pytest exercise-ai -q` (must not pick up `demo/`)
- **Phase gate:** Full exercise-ai suite green + manual UAT checklist for DEMO-01/02 in VERIFICATION / UAT

### Wave 0 Gaps

- [ ] `demo/tests/test_guards.py` — loopback assert, Host/Origin/Content-Type, lock→409 helper
- [ ] `demo/tests/test_error_map.py` — maps three exception classes (+ `kind` / `api_error_kind`) to response dict
- [ ] Extract pure functions (`assert_loopback`, `check_post_headers`, `error_payload`) in `demo/` so tests need no socket listen
- [ ] **Do not** add `demo` to GitHub Actions
- [ ] Manual UAT script notes in plan: presets → Gerando… → Exercícios/JSON tabs; second concurrent POST → HTTP 409; bad Host → 403

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Loopback-only throwaway; no user auth |
| V3 Session Management | no | No sessions; banner dismiss is client-only |
| V4 Access Control | yes (local) | Host allowlist `[::1]:8642`; Origin allowlist; refuse non-loopback bind |
| V5 Input Validation | yes | `application/json` only; Pydantic `GenerationRequest` bounds (`quantidade` 1–40) |
| V6 Cryptography | no | No new crypto; TLS N/A on loopback demo |

### Known Threat Patterns for stdlib local LLM demo

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Cross-origin POST burns API quota | Elevation / Economic | Host + Origin + JSON Content-Type [CITED: PITFALLS 14] |
| Broad bind exposes keys on LAN | Information Disclosure | `is_loopback` refuse-to-start [CITED: PITFALLS 13] |
| Double-submit / second tab | Tampering / Economic | Lock → HTTP 409 [CITED: PITFALLS 12] |
| Stderr / env rendered in UI | Information Disclosure | Render `model_dump()` + typed errors only [CITED: PITFALLS 15] |
| Demo promoted to staging | Elevation | Anti-accretion banner/README; outside CI [CITED: PITFALLS 17] |
| Secrets in logs/HTML | Information Disclosure | Never print API keys; dotenv only in `__main__` [AGENTS.md] |

## Sources

### Primary (HIGH confidence)
- Context7 `/websites/python_3_16` — `ThreadingHTTPServer`, `threading.Lock.acquire(blocking=False)`, `ipaddress.is_loopback`
- `exercise-ai/service.py`, `models.py`, `wizard.py`, `main.py` — read this session
- `README.md` Embed section — host contract
- `.planning/research/STACK.md` Finding 5 — AF_INET6 pattern
- `.planning/research/PITFALLS.md` 12–17 — demo threats
- `.planning/phases/12-local-embed-demo/12-CONTEXT.md` — locked decisions
- `.github/workflows/ci.yml` — `pytest exercise-ai -q`

### Secondary (MEDIUM confidence)
- `.planning/research/SUMMARY.md` Phase 12 shape
- Local runtime probes (AF_INET default, `::1` is_loopback, Lock nonblocking) on Windows Python 3.14.0
- classify-confidence context7 --verified → MEDIUM (seam); elevated to HIGH where cross-checked with local probe + in-repo reads

### Tertiary (LOW confidence)
- Exact HTTP status 415 for bad Content-Type — [ASSUMED]
- Per-request demo env save/restore beyond service scope — [ASSUMED] UX preference

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — stdlib + locked CONTEXT; no new packages
- Architecture: HIGH — STACK pattern + Phase 11 contract verified in source
- Pitfalls: HIGH — PITFALLS 12–17 + Phase 11 mitigations checked
- Code examples: HIGH — verbatim from service/models/wizard/README; HTTP snippets from official docs + STACK

**Research date:** 2026-09-18
**Valid until:** 2026-10-18 (30 days — stdlib stable)

---

*Phase: 12-local-embed-demo*
*Research completed: 2026-09-18*
*Ready for planning: yes*
