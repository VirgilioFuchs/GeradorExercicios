# Feature Research

**Domain:** Embeddable in-process exercise-generation library (Python) consumed by a host application, plus a throwaway local demo page
**Researched:** 2026-09-16
**Confidence:** HIGH on the library-boundary table stakes (official Python/SDK docs + direct code reading); MEDIUM on differentiators (practitioner/vendor convention); LOW–judgement on the demo page scope (no sourced practice — stated as judgement below)

**Milestone:** v2.0 "Embed em Produção" — SUBSEQUENT milestone. Everything already shipped through v1.2 (parameterized generation, structured JSON, structural + math validation, bounded RELY, failover, token usage NDJSON/`[USAGE]`, argparse CLI, `gerar` wizard, offline CI) is treated as EXISTING and is not re-proposed. Only the *consumer-facing surface* of the new library boundary is in scope.

**Research provider note:** the `gsd_run query research-plan` seam is unavailable on this machine (bash/WSL resolves `$HOME` to `/home/anglo`, where `gsd-core/bin/gsd-tools.cjs` does not exist). Per the documented fallback, sources came from the built-in `WebSearch` and the Context7 MCP directly. Confidence tiers were assigned by hand using the same hierarchy (official docs = HIGH, vendor/practitioner = MEDIUM, single blog/forum = LOW).

---

## Feature Landscape

### Table Stakes (Host Integrators Expect These)

A host integrator reviewing this library will reject it if any of these is missing. Each row names the concrete blocker found in the current code, so the roadmapper can size real work rather than a principle.

| # | Feature | Why Expected | Complexity | Notes |
|---|---------|--------------|------------|-------|
| TS-01 | **No process exit from the library path** — the service returns or raises; only the CLI entry point converts failure to an exit code | A library that calls `sys.exit` makes a process-level decision on the host's behalf; the host can no longer recover, retry, or report. Community consensus is unambiguous: "a library module should never call `sys.exit()`" — HIGH/MEDIUM ([python-list], [SO 13992662]) | LOW | Current blocker: `main.run()` calls `sys.exit(1)` in all three `except` branches (`main.py:238,246,254`), plus `sys.exit(2)` for wizard extra-args. Fix is structural, not algorithmic: `service.generate_batch()` raises; `main.run()` keeps the `except → print → sys.exit(1)` behaviour so CLI regression is zero |
| TS-02 | **Return data, do not render or persist it** — `generate_batch(request) -> ExerciseBatch`, no `print`, no `--out` file write | The host renders in its own UI and persists in its own store. A library that formats text and writes JSON files has decided both for the host | LOW | Current blocker: `main.run()` does `print(format_batch_text(...))` to **stdout** (`main.py:218`) and writes the `--out` JSON (`main.py:219-228`). Both move up into the CLI adapter. `format_batch_text` stays and becomes CLI-only (the demo may reuse it, but the host must not need it) |
| TS-03 | **Do not write to the caller's stdout/stderr** — progress and diagnostics go through a namespaced `logging` logger with a `NullHandler`, and the library installs no other handler | Official Python guidance: use `logging.getLogger(__name__)`, never log to the root logger, attach **only** `NullHandler`, and "do not add any handlers other than NullHandler … the configuration of handlers is the prerogative of the application developer" — HIGH ([Python Logging HOWTO]) | MEDIUM | Biggest single chunk of work. ~33 unconditional `print(..., file=sys.stderr)` sites live in core modules that the service will call: `generator_gemini.py` (9), `generator.py` (6), `reliability.py` (6) — including `"Gerando…"`, `"Validando…"`, `duração total_ms=` — `token_usage/collector.py` (5, the `[USAGE]` lines), `failover.py` (3, `[FAILOVER]`), `math_check.py` (2), `validator.py` (2). Existing tests assert on captured stderr, so this is the highest regression-risk item in the milestone. `main.py` already has the right shape (`_configure_logging` attaches the StreamHandler) — the handler attachment must stay in the CLI adapter only |
| TS-04 | **An error contract with three distinguishable categories** — (a) your configuration is wrong, (b) the caller's input is invalid, (c) the model failed after N attempts — catchable **without** string-matching a Portuguese message | Practitioner consensus: exceptions are part of the public API; design a small hierarchy rooted in one package base, subclass only where callers must react differently, and store structured facts as attributes rather than message text — MEDIUM ([leynos python-errors SKILL], [SE.SE 310415], [EngineersOfAI]) | MEDIUM | Current blocker: every failure is a bare `ValueError` or `RuntimeError` carrying a PT sentence. Config failure (`"Chave ausente para o provedor openai…"`), input failure (bad `quantidade`), and exhaustion (`"após 1 regenerações: …"`) are the *same two types*. The host's only discriminator today is `getattr(exc, "retriable", None)` / `api_error_kind`, which are monkey-patched attributes set in `generator.py:93-105`, not a documented contract. **See "Constraint Tensions" #2** for the recommended shape |
| TS-05 | **An explicit, bounded timeout with a documented worst case** | A synchronous in-process call that can hang indefinitely is the classic reason an integrator refuses an embed: the host's request thread is held hostage. Project rule `20-ai-engineering.mdc` also lists timeouts as a centralized concern | LOW (per-client) / MEDIUM (aggregate budget) | **Two concrete defects found.** (1) Gemini has **no timeout at all**: `genai.Client(api_key=...)` (`generator_gemini.py:82`) passes no `http_options`, and `HttpOptions.timeout` defaults to `None`, which the SDK converts to an `httpx` timeout of `None` — HIGH, Context7 `/googleapis/python-genai` (`types.py`, `_api_client.get_timeout_in_seconds`). Fix: `http_options=types.HttpOptions(timeout=30000)` (milliseconds — confirmed in the same source). (2) The OpenAI/Grok clients set `timeout=30.0` but leave the SDK's own `max_retries` at its default of **2**, so one logical call is up to **3 HTTP attempts** with backoff — HIGH, Context7 `/openai/openai-python` (`_constants.py`: `DEFAULT_MAX_RETRIES = 2`, `INITIAL_RETRY_DELAY = 0.5`, `MAX_RETRY_DELAY = 8.0`). Multiply by the layers the project already has — RELY up to 4 attempts, Gemini walking up to 5 model candidates (`GEMINI_MODEL_FALLBACKS`), failover doubling across providers — and the worst-case wall clock is minutes at best and unbounded on the Gemini path. The host needs one stated number |
| TS-06 | **No hidden global state; restore anything the library mutates** | The host's process outlives the call. A library that permanently changes the environment silently changes the behaviour of every later call | LOW | Current blocker, already on the milestone's own target list ("`LLM_PROVIDER` restaurado"): `failover._default_switch_provider` writes `os.environ["LLM_PROVIDER"]` and never restores it (`failover.py:54-56,82`), and `main.main()` does the same for `--provider`/`--reasoning`. After one failover, the host's process is pinned to the peer provider forever. Fix is a `try/finally` restore around the failover hop. Two more globals to acknowledge: the module-level `_collector` singleton (`token_usage/collector.py:125`) and `math_check`'s module-level `_uninterpretable` / `_last_inconsistencies` buffers (drained via `clear_math_buffers()` in the success path only) |
| TS-07 | **Input validation in the domain model, not in the CLI parser** | A host calling `generate_batch` bypasses argparse entirely. Validation that lives in an `argparse` type is not validation | LOW | Current blocker, also on the milestone's target list ("bound 1–40 no domínio"): `GenerationRequest.quantidade` is only `gt=0` (`models.py:19`); the 1–40 bound lives in `main._positive_quantidade`. A host can request 5 000 exercises and spend real tokens finding out. Fix: `Field(..., ge=1, le=40)` plus a non-empty constraint on `topico`. Pydantic's `ValidationError` then becomes a natural member of category (b) in TS-04 |
| TS-08 | **No filesystem side effects the caller did not ask for** | In a production host the package may live in a read-only `site-packages`, in a container with an ephemeral filesystem, or be shared across tenants. Writes into the package directory are a deployment failure waiting to happen | MEDIUM | Current blocker: three write sites fire on paths **inside the package dir** (`output_paths.PACKAGE_DIR / "exercicios-gerados"`) regardless of who called — `_write_postmortem` on final validation failure (`reliability.py:130`), `write_fail_error_log` on every error branch of `run()`, and `flush_token_usage` appending `token-usage/<day>/<provider>.ndjson` (`collector.py:102-122`) from `run()`'s `finally`. The service boundary must make all three the *caller's* decision (opt-in flag or caller-supplied directory) while the CLI keeps today's behaviour byte-for-byte |
| TS-09 | **Importable without import-time side effects** | `import` must not reach into the host's process state. A host whose own `.env` or `sys.path` is silently rewritten by an import will not ship it | LOW–MEDIUM | Current blocker: `main.py` mutates `sys.path` (`main.py:15-17`) and calls `load_dotenv` (`main.py:20-23`) at module import. The new `service.py` must be importable with neither. Mitigating fact: `load_dotenv` does not override already-set env vars, so the damage is bounded — but `sys.path.insert` is unconditional. Note the coupling: the flat-module import style (`from models import …`) is what forces the `sys.path` hack, and packaging is explicitly parked this milestone, so the realistic target is "the *service* module is clean", not "the package is clean" |
| TS-10 | **A written contract: the exact JSON shape, field semantics, and an error table** | The host team codes against a document, not against a reading of `models.py`. This is the artifact the demo exists to deliver | LOW | Depends on TS-04 being decided first, or the error table has nothing stable to list. The `Exercise` / `ExerciseBatch` shape already exists and is unchanged — that is the easy half |
| TS-11 | **Honest concurrency statement: one generation at a time, per process** | Concurrency is out of scope by decision, which is fine — but the host *will* call this from a web request handler. Silence reads as "thread-safe" | LOW | This is the KISS-compatible alternative to actually making it safe. It is not merely a doc: TS-06's globals (`_collector`, `math_check` buffers, `LLM_PROVIDER`) make two concurrent calls genuinely corrupt each other's usage records and provider choice. Stating the constraint is honest; leaving it implied is a trap. Also constrains the demo server — see DM-06 |

### Differentiators (Worth Considering, Not Assumed)

| # | Feature | Value Proposition | Complexity | Notes |
|---|---------|-------------------|------------|-------|
| DF-01 | **Return usage/cost with the result** (tokens in/out, USD, duration, attempts, provider actually used, whether failover fired) | The host can meter and bill per generation without parsing NDJSON files or scraping `[USAGE]` stderr lines. SDK convention is to expose usage and rate-limit metadata on the response object rather than only in logs — MEDIUM ([SDK design guide], [Bird SDK concepts]) | LOW (data already exists) / **but see tension #1** | Nearly free at the data layer: `TokenUsageCollector.events` already holds every event in memory before `flush()` clears it, with provider, model, status, tokens, `duration_ms`, `usd`, `usd_source`, and `error_kind` per event. The cost is **not** collection — it is that `-> ExerciseBatch` has nowhere to put it. Decide in the same phase as the signature |
| DF-02 | **Caller-supplied correlation id / request id** | Lets the host join its own request log to the library's usage records when a teacher reports a bad batch. Typed errors carrying a request id is standard SDK practice — MEDIUM ([SDK design guide]) | LOW | Already 90% built: `token_usage.begin_run(run_id: str | None = None)` accepts an external id and otherwise generates `uuid4().hex[:12]`, and `run_id` is already a field on every `UsageEvent`. The work is exposing it on the service signature and returning it (same tension as DF-01) |
| DF-03 | **Per-call configuration override for the three knobs that matter** — `provider`, `reasoning`, `max_retries` — as function arguments | The host may want cheap/fast for a quiz preview and high reasoning for a graded assessment, in the same process. The two-tier pattern (identity/transport fixed at construction, lifecycle knobs defaulted at construction and overridable per call) is the mainstream SDK convention — MEDIUM ([Bird SDK concepts], [OpenAI `with_options`] HIGH via Context7) | MEDIUM | `max_retries` is **already** a `run()` parameter and resolves CLI > `RELY_MAX_RETRIES` > 1 (`reliability.resolve_max_retries`) — the precedence pattern to copy. `provider` and `reasoning` are settable *only* by mutating `os.environ`, which is exactly the TS-06 defect. Doing this properly means threading a parameter through `failover → reliability → generator → _resolve_provider` instead of writing env. **Compatible with the env-is-config constraint** (see tension #3) — it is an argument, not a `Settings` object |
| DF-04 | **Structured event callback** (`on_event: Callable[[dict], None] | None`) for progress and diagnostics | Lets the host drive its own "gerando… / validando… / 1ª regeneração" UI without configuring Python logging. Same forum thread that bans `print` from libraries offers exactly two sanctioned outlets: "sent to the caller somehow, or handled using the logging facility" — MEDIUM ([python-list]) | MEDIUM | **Judgement:** do TS-03 (logging) first and treat the callback as an *upgrade*, not a substitute. Logging is the sourced convention and satisfies the boundary on its own; the callback is what the host will actually enjoy using, but it is a second public surface to keep stable. If both land, the callback should be a thin fan-out at the same call sites, not a parallel code path |
| DF-05 | **Dry-run / validation-only mode** (`validate_only=True`: validate the request, build the prompt, return without calling any provider) | The host team can wire and demo the whole integration — including error rendering — at zero token cost, and the boundary becomes testable in the existing offline CI. Highest value-per-line item in this table, in my judgement | LOW | The pieces are already separable: `prompts.build_prompts(request)` is pure, and request validation is (after TS-07) pure Pydantic. Also directly de-risks the demo: the host team can click through the flow before any key is configured. Pairs naturally with a "validate this batch I already have" helper over `validator.validate_exercise_batch`, though that second half is optional |
| DF-06 | **Per-call timeout parameter plus a published worst-case budget** | Turns TS-05 from "we set 30s somewhere" into a number the host can put in its own SLA | MEDIUM | Depends on TS-05 landing first. The interesting design question is whether the parameter is a per-HTTP-attempt timeout (easy: pass through to both SDKs) or a total deadline across RELY + model-candidate walk + failover (harder: needs a deadline threaded through the loops). Recommend per-attempt + a documented multiplier; a true deadline is a v2.1 conversation |
| DF-07 | **Cooperative cancellation** (`should_cancel: Callable[[], bool]`, checked between RELY attempts and before the failover hop) | If the host's user navigates away, the library stops spending tokens | MEDIUM | **Judgement — defer.** Real cancellation of an in-flight HTTP call requires threads or async, which the concurrency-out-of-scope constraint forbids. A between-attempts check is the only honest version and it only helps in the multi-attempt case. Say so explicitly rather than shipping a `cancel()` that does not cancel |

### Anti-Features (Do NOT Build This Milestone)

| # | Feature | Why Requested | Why Problematic | Alternative |
|---|---------|---------------|-----------------|-------------|
| AF-01 | `Settings` / config object | "Config should be typed and injectable" | Already rejected by the operator this milestone; introduces a parallel config source alongside env and a migration for every call site, to solve a problem (multi-tenant config) that does not exist yet | Env stays the config source. Add DF-03 per-call arguments for the three knobs that genuinely vary per call |
| AF-02 | `generate_batch_async` / thread pool / concurrent batch execution | "The host is a web app, it needs throughput" | Out of scope by decision, and the current globals (TS-06) make it actively unsafe. Would double the public surface and every test | Sequential contract, documented (TS-11). The host can run one process per worker if it needs parallelism — that is its call to make, not ours |
| AF-03 | HTTP API / FastAPI or Flask wrapper around the service | "Expose it as a microservice so any host can call it" | Out of scope; adds a dependency, a deployment unit, auth, and a network hop to a problem that is solved by `import`. The host is Python and calls in-process | In-process `generate_batch`. The demo gets its HTTP from `http.server` in a throwaway directory outside the package and outside CI |
| AF-04 | Idempotency key with server-side dedupe / result cache | "Retried writes shouldn't double-charge" — a real and standard SDK concern ([Bird SDK concepts]) | It does not transfer to this domain. Idempotency keys work because a server stores and replays the response; there is no server here and persistence is out of scope. Generation is also *intentionally* non-deterministic — replaying a stored batch for the same key would defeat the point of asking again | Correlation id only (DF-02). Retry safety is already handled where it belongs: bounded RELY plus a single failover hop |
| AF-05 | Provider plugin registry / abstract `Provider` base class / DI container | "Three providers means we need an abstraction" | Three providers dispatched by one `if/elif` in `generate_exercises` is correct at this size. An abstraction now would be designed against zero knowledge of the fourth provider, and both project rules (`KISS → YAGNI`, "do not create abstractions only because they may be useful in the future") forbid it | Keep `_resolve_provider` + `if/elif`. Revisit if a fourth provider with a genuinely different shape appears |
| AF-06 | Retry policy engine / circuit breaker / exponential-backoff configuration | "Production resilience" | Three retry layers already exist and stack (SDK `max_retries=2`, Gemini model-candidate walk, RELY 0–3, plus failover). A fourth configurable layer makes the worst-case *less* predictable, which is the opposite of what TS-05 needs | Bound and document what exists (TS-05). If anything, consider *reducing* the OpenAI SDK's own `max_retries` so the budget is legible |
| AF-07 | Translating error messages to English / i18n layer for the host | "The host team's logs are in English" | Portuguese is the operator-facing language by constraint, and a translation layer makes every message a two-place edit | Split the contract: a stable machine-readable discriminator (exception class and/or `kind`) that the host branches on, plus the existing PT sentence as the human message. The host renders its own copy if it wants English. This makes the PT constraint a non-issue rather than a conflict |
| AF-08 | `pyproject.toml`, rename to `exercise_ai/`, publish to an index | "It's a library now, package it" | Already parked until the host's stack is known. Packaging decisions made against an unknown consumer get redone | Path-based import for now; let the demo prove the shape. The one thing to *avoid* is new code that makes packaging harder later |
| AF-09 | Streaming / partial results / per-exercise progressive rendering | "Generation takes seconds, stream it" | Breaks the project's core value: the batch is validated *before* the caller sees it. Streaming means emitting unvalidated exercises, and validation is per-batch (quantity checks included) | A "generating…" state in the host UI (DM-03), optionally fed by DF-04. Perceived-latency problem, not an architecture problem |
| AF-10 | Persisting batches inside the library (DB, ORM, storage abstraction) | "The host needs the exercises saved" | Out of scope, and it is TS-08 in reverse — the library would own a resource the host already owns | Return data; the host persists. The CLI keeps its `--out` file because a CLI legitimately owns its output |
| AF-11 | Growing the demo into a product: login, saved history, editing exercises, PDF/DOCX export, image previews, multi-user | "While we're building a UI anyway…" | The demo's stated purpose is to show a contract to one team, once. Every feature added is throwaway code that acquires an owner, and it competes with the library work that actually ships | One page, no state, deleted or left unmaintained after the meeting. The contract JSON panel (DM-02) is the deliverable — everything else is framing |
| AF-12 | Metrics export (Prometheus, OpenTelemetry) from the library | "Production observability" | New dependency and a second observability contract, when the host almost certainly has its own | The existing `[USAGE]` lines and NDJSON stay; DF-01 hands usage to the host, which feeds its own metrics stack |
| AF-13 | Generated images / storytelling exercises in the schema | Both are in SEED-003 and genuinely coming | Slices B and C by the operator's own ordering; they change schema, prompts, validation, and the host contract simultaneously. Doing any of it now means shipping a contract to the host team that immediately breaks | Ship the text contract. Note in TS-10 that `Exercise` will gain fields later, so the host should tolerate unknown/extra keys rather than assume a closed schema — cheap forward-compatibility, zero code |

---

## Constraint Tensions (flagged explicitly, per the quality gate)

Four places where good library practice pushes against a locked decision or against another item in this file. None is a reason to break a constraint; each needs a conscious call during roadmapping.

**1. `generate_batch(request) -> ExerciseBatch` leaves no room for usage, run_id, or provider-used (DF-01, DF-02).**
This is the single most consequential decision in the milestone, because **widening a return type later is a breaking change for the host**. Three options: (a) keep `-> ExerciseBatch` and expose usage through a module-level `last_run_usage()` — rejected, it is precisely the hidden global state TS-06 removes; (b) return a small `GenerationResult` with `.exercicios` plus `.usage` / `.run_id` / `.provider`; (c) ship `-> ExerciseBatch` now and add a separate `generate_batch_with_usage` later. **My recommendation: decide in the phase that creates `service.py`, and if usage matters at all to the host, take (b) now.** If the host team says "we only want the exercises", (a)/(c) never come up and `-> ExerciseBatch` is genuinely right. This is a question to put to the host team *at the demo*, and the demo is a good place to show both panels.

**2. A `kind` string attribute on `ValueError` satisfies the locked decision but is the weaker of two shapes (TS-04).**
Sourced practice is a small hierarchy rooted in one base class, with error codes called out as "a low-level implementation detail leaking into your abstractions", justified mainly when wrapping a third party that already has codes ([SE.SE 310415], MEDIUM). There is an option that satisfies both: define `ConfigError(ValueError)`, `InvalidRequestError(ValueError)`, `GenerationFailedError(RuntimeError)` — **subclasses of the types already raised**, so every existing `except ValueError` / `except RuntimeError` in the CLI, wizard, and 133-test suite keeps passing unchanged (zero regression), while the host gets `except ConfigError`. The `kind` attribute can ride along on the same objects for cheap logging. Cost is one small module; the locked decision is honoured in substance (no new config object, no CLI behaviour change) and the host stops string-matching `"após N regenerações"`.

**3. Per-call overrides are compatible with env-as-config — but only if implemented as arguments.**
DF-03 is *not* a `Settings` object and does not displace env as the configuration source; the precedence `argument > env var > default` already exists and is proven in `resolve_max_retries`. The trap is implementing it the way the code does today: writing `os.environ["LLM_PROVIDER"]`. That reintroduces TS-06. Thread a parameter; do not mutate the environment.

**4. "Zero new dependencies" for the demo excludes CDN assets, not just pip packages.**
A Tailwind/Bootstrap/Alpine `<script src="https://…">` is a runtime network dependency and, in my judgement, violates the spirit of the constraint (it also breaks the demo on a machine with no internet, in the middle of a presentation). Inline the CSS and the ~30 lines of `fetch()` JavaScript in the single HTML string. Stdlib `http.server` + `json` is all the demo needs.

---

## Demo Page: Minimum to Communicate the Contract

Purpose is narrow and worth restating: **show one host team, once, what calling this library looks like and what JSON comes back.** Presentable, throwaway, `demo/` outside the package, stdlib only, outside CI, `http://[::1]:8642/`. The items below are my judgement (no sourced practice for "demo page for an internal integration handoff") — flagged as such, and each is justified by what the host team must walk away understanding.

| # | Element | What It Communicates | Complexity | Notes |
|---|---------|----------------------|------------|-------|
| DM-01 | **One form mirroring the CLI parameters exactly**: `materia` (text, default "Matemática"), `topico` (text), `dificuldade` (select: facil / medio / dificil), `quantidade` (number, min 1 max 40) | The form *is* the documentation of `GenerationRequest`. A host dev reads four inputs and knows the request shape | LOW | Mirror the real bounds so the demo also proves TS-07. Defaults should match the CLI's (`Equação do primeiro grau`, `facil`, `3`) so the page is usable with one click |
| DM-02 | **Side-by-side result: rendered exercises left, raw contract JSON right** | This is the actual deliverable. The left panel says "this is useful", the right panel says "this is what your code receives". Showing them adjacent is what makes the contract concrete instead of abstract | LOW | Pretty-printed, monospace, scrollable, with a copy button — the host dev will paste it into their own fixture. Render `enunciado` / `resposta` / `explicacao` labelled in PT, matching `format_batch_text`'s existing layout so CLI and demo tell the same story |
| DM-03 | **A "Gerando…" busy state** with the form disabled and an elapsed-seconds counter | A generation takes seconds; a page that freezes with no feedback reads as broken and derails the meeting. The counter also sets honest expectations about latency, which is the host's real integration concern (TS-05) | LOW | Must be honest about the worst case. If a RELY regeneration or a failover fires, this can run far longer than the happy path — "1ª Regeneração" / "trocando de provedor" text here is worth more than polish elsewhere |
| DM-04 | **An honest error state** showing the error *category* (configuração / entrada inválida / geração falhou) plus the PT message, styled as an error | The second-highest-value panel after DM-02, because it demonstrates TS-04 live. The host team's first design question will be "what do we do when it fails" — answer it on screen instead of in prose | LOW | Do not swallow errors into a blank page or dump a raw traceback / browser JSON view. The demo should be able to *produce* each category on demand — easiest with a deliberately wrong provider key for the config case and an out-of-range `quantidade` for the input case. DF-05 (dry-run) makes this reproducible without spending tokens |
| DM-05 | **A one-line run footer**: provider that answered, whether failover fired, tokens and USD, `run_id` | Turns the abstract DF-01/DF-02 conversation into a concrete "do you want these fields in the response?" question, asked while the host team is in the room | LOW (conditional) | Only build this if DF-01/DF-02 land. If they do not, the footer has to scrape stderr, which is exactly the anti-pattern the milestone removes — better to omit it |
| DM-06 | **Stdlib-only single-generation server**: `http.server`, one HTML string, `POST /api/gerar` returning the contract JSON | Zero new dependencies, and the ~40-line handler doubles as a worked example of how the host calls `generate_batch` and maps the three error categories | LOW–MEDIUM | **Concrete pitfall:** use single-threaded `HTTPServer`, or a module-level lock, **not** `ThreadingHTTPServer` — two concurrent generations would violate the sequential contract (TS-11) and corrupt the shared usage collector. The demo must not be the thing that disproves the contract it is demonstrating. Bind `[::1]:8642` per the milestone target |

**Explicit scope creep for the demo — do not build:** persistence or generation history; editing or regenerating a single exercise; download as PDF/DOCX/CSV; authentication or user accounts; a provider/model picker beyond what env already selects; live token charts; streaming or progressive rendering; CSS framework or any CDN asset (tension #4); mobile-responsive polish; dark mode; tests or CI wiring for the demo (explicitly out of CI); shipping the demo inside the package or importing anything from `demo/` into `exercise-ai/` (the dependency arrow must point one way only).

---

## Feature Dependencies

```
TS-01 (no sys.exit)
TS-02 (return, don't render)
TS-03 (no stdout/stderr writes)
    └──all three require──> service.py extracted from main.run(), with
                            main.run() as a thin CLI adapter
                                └──requires──> TS-09 (importable without
                                               sys.path / load_dotenv
                                               side effects)

TS-07 (1–40 bound in the domain)
    └──enables──> TS-04 (error contract: gives category (b) "invalid
                  caller input" something real to raise)
                      └──requires──> TS-10 (documented contract: the
                                     error table has nothing stable to
                                     list until TS-04 is decided)
                                         └──requires──> DM-04 (the demo's
                                                        error panel shows
                                                        TS-04's categories)

TS-05 (explicit timeouts)
    └──enhances──> DF-06 (per-call timeout parameter) — pointless before
                   the per-client timeouts exist at all

TS-06 (no hidden global state / restore LLM_PROVIDER)
    └──required by──> DF-03 (per-call provider/reasoning override) — doing
                      DF-03 by mutating os.environ recreates TS-06
    └──required by──> TS-11 (sequential contract) — the globals are the
                      reason the contract must be sequential

TS-08 (no unrequested filesystem writes)
    └──conflicts with──> the current CLI behaviour of write_fail_error_log
                         + flush_token_usage + postmortem, which must be
                         preserved exactly; so the split is "caller
                         decides" at the service, "CLI decides yes" in
                         the adapter

DF-01 (usage in the result) ──requires──> a return-type decision
DF-02 (correlation id)      ──requires──> the same decision
    └──both blocked by──> the locked signature -> ExerciseBatch
                          (Constraint Tension #1 — decide once, early)
    └──both enable──> DM-05 (demo run footer)

DF-05 (dry-run mode)
    └──enhances──> DM-04 (reproducible error states without tokens)
    └──enhances──> offline CI coverage of the new boundary
    └──requires──> TS-07 (request validation must be real to be the
                   only thing a dry run does)

DF-04 (event callback) ──enhances──> TS-03 (same call sites) and DM-03
DF-07 (cancellation)   ──conflicts with──> "concurrency out of scope"
                                           (only a cooperative
                                           between-attempts check is
                                           honest; defer)
```

### Dependency Notes

- **TS-01/02/03 all collapse into one extraction.** They are not three pieces of work; they are three acceptance criteria for the single act of splitting `main.run()` into `service.generate_batch()` (pure) and `main.run()` (adapter). Roadmap them together or the extraction gets done three times.
- **TS-03 is the schedule risk, not TS-01.** Removing `sys.exit` touches 4 lines. Removing ~33 `print` calls from `generator.py`, `generator_gemini.py`, `reliability.py`, `failover.py`, `math_check.py`, `validator.py`, and `collector.py` touches seven modules and the tests that assert on their stderr. Size accordingly, and consider doing it as a mechanical pass in its own plan.
- **TS-04 gates TS-10 gates DM-04.** The demo's most persuasive panel is downstream of the error-contract decision. If TS-04 slips, the demo shows a generic red box and the host team leaves without the answer they came for.
- **The return-type decision (tension #1) is the one-way door.** Everything else in this milestone can be adjusted in v2.1 without breaking the host. The signature cannot. Put it in the earliest phase that touches `service.py`, and prefer resolving it *before* the demo so DM-05 is buildable.
- **TS-08's real constraint is regression, not design.** The service must not write; the CLI must write exactly what it writes today (`exercicios-gerados/success/`, `fail/erros/`, `fail/postmortem/`, `token-usage/<day>/`). Any phase touching this needs the existing `test_output_paths` / `test_token_usage` suites green as its gate.
- **DF-05 pays for itself across three other items** (DM-04, CI coverage of the boundary, and the host team's ability to integrate before keys are provisioned). It is the differentiator I would not defer.

---

## MVP Definition

### Launch With (v2.0)

The boundary is only credible if all of these are true. Ordered roughly by dependency.

- [ ] **TS-09** — `service.py` importable with no `sys.path` mutation and no `load_dotenv` at import — otherwise every other item is built on a module that rewrites the host's process at import time
- [ ] **TS-01 + TS-02 + TS-03** — `service.generate_batch(request)` returns the validated batch; raises instead of exiting; writes nothing to stdout/stderr; `main.run()` becomes the adapter that prints, writes `--out`, and exits. CLI and wizard behaviour byte-identical
- [ ] **TS-07** — 1–40 bound and non-empty `topico` in `GenerationRequest`; `argparse` keeps its own message for CLI UX
- [ ] **TS-04** — three distinguishable error categories, catchable without string matching (recommended shape: subclasses of the existing `ValueError`/`RuntimeError` — tension #2)
- [ ] **TS-06** — `LLM_PROVIDER` restored after a failover hop; no env mutation that outlives a call
- [ ] **TS-05** — Gemini client gets an explicit timeout (it currently has none); the aggregate worst case is measured and written down
- [ ] **TS-08** — the service performs no filesystem write the caller did not request; the CLI's existing artifacts are unchanged
- [ ] **TS-10 + TS-11** — the contract document: request fields, response JSON, error table, and the explicit "one generation at a time per process" statement
- [ ] **DM-01 … DM-04, DM-06** — the demo: form, exercises + raw JSON side by side, generating state, honest error state, stdlib single-generation server
- [ ] **DF-05** — dry-run / validation-only mode. Included in the MVP against the instinct to defer it, because it makes DM-04 reproducible, gives the offline CI something to assert about the new boundary, and lets the host team integrate before keys exist

### Add After Validation (v2.1)

- [ ] **DF-01 + DF-02** — usage and correlation id in the response. **Trigger: the host team's answer at the demo.** If they want per-generation cost, this moves into v2.0 instead, because the return type cannot be widened later without breaking them (tension #1)
- [ ] **DM-05** — demo run footer. Trigger: DF-01/DF-02 landing
- [ ] **DF-03** — per-call `provider` / `reasoning` override. Trigger: the host asks for different quality tiers in one process
- [ ] **DF-04** — structured event callback. Trigger: the host says Python `logging` does not fit their UI progress needs
- [ ] **DF-06** — per-call timeout parameter. Trigger: the host's own request budget is tighter than our documented worst case

### Future Consideration (v2.2+)

- [ ] **DF-07** — cooperative cancellation. Defer: only honest between attempts while concurrency is out of scope; revisit if async ever enters scope
- [ ] **Packaging** (`pyproject`, `exercise_ai/` rename) — defer: parked until the host's stack is known (AF-08)
- [ ] **SEED-003 Slice B (images) and Slice C (storytelling)** — defer: they change the schema the host just integrated against (AF-13). Cheap hedge now: tell the host to tolerate unknown keys in `Exercise`
- [ ] **Async / concurrent generation** — defer: out of scope, and blocked on removing the shared globals first (AF-02)

---

## Feature Prioritization Matrix

| Feature | Host Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| TS-01 no `sys.exit` in the library path | HIGH | LOW | P1 |
| TS-02 return data, don't render/persist | HIGH | LOW | P1 |
| TS-03 no writes to caller's stdout/stderr | HIGH | MEDIUM | P1 |
| TS-04 three-category error contract | HIGH | MEDIUM | P1 |
| TS-05 explicit timeouts + worst-case budget | HIGH | LOW–MEDIUM | P1 |
| TS-06 restore `LLM_PROVIDER`; no hidden globals | HIGH | LOW | P1 |
| TS-07 1–40 bound in the domain model | MEDIUM | LOW | P1 |
| TS-08 no unrequested filesystem writes | HIGH | MEDIUM | P1 |
| TS-09 no import-time side effects | HIGH | LOW–MEDIUM | P1 |
| TS-10 written contract (JSON + error table) | HIGH | LOW | P1 |
| TS-11 explicit sequential-only statement | MEDIUM | LOW | P1 |
| DM-01 form mirroring CLI parameters | MEDIUM | LOW | P1 |
| DM-02 exercises + raw contract JSON side by side | HIGH | LOW | P1 |
| DM-03 "gerando…" busy state | MEDIUM | LOW | P1 |
| DM-04 honest error state by category | HIGH | LOW | P1 |
| DM-06 stdlib single-generation demo server | MEDIUM | LOW–MEDIUM | P1 |
| DF-05 dry-run / validation-only mode | HIGH | LOW | P1 |
| DF-01 usage/cost in the response | HIGH | LOW (data) | **P1 if the host wants cost; else P2** — one-way door |
| DF-02 caller-supplied correlation id | MEDIUM | LOW | P2 (same door as DF-01) |
| DM-05 demo run footer | MEDIUM | LOW | P2 (conditional on DF-01/02) |
| DF-03 per-call provider/reasoning override | MEDIUM | MEDIUM | P2 |
| DF-06 per-call timeout parameter | MEDIUM | MEDIUM | P2 |
| DF-04 structured event callback | MEDIUM | MEDIUM | P3 |
| DF-07 cooperative cancellation | LOW | MEDIUM | P3 |

**Priority key:** P1 must have for v2.0 · P2 should have, add when triggered · P3 future consideration

---

## Reference Library Comparison

How three libraries the host team already trusts handle the same concerns, and what this project should do. (Substitutes for competitor analysis — the relevant "competitors" for a library boundary are the SDKs the host has already integrated.)

| Concern | OpenAI Python SDK | Google Gen AI Python SDK | `requests` / stdlib convention | Our approach |
|---------|-------------------|--------------------------|-------------------------------|--------------|
| Timeouts | Client default 10 min; per-request override via `client.with_options(timeout=5.0)`; raises `APITimeoutError` (HIGH, Context7) | `HttpOptions(timeout=<ms>)`; **default `None` = no timeout** (HIGH, Context7) | Explicit `timeout=` strongly recommended; no default | Keep the existing 30 s on OpenAI/Grok, **add** the missing Gemini timeout, and publish the aggregate worst case (TS-05). Per-call override only later (DF-06) |
| SDK-internal retries | `DEFAULT_MAX_RETRIES = 2`, 0.5 s → 8 s backoff, honours `Retry-After` (HIGH, Context7) | Model-candidate walk is ours, not the SDK's | n/a | Do not add a fourth retry layer (AF-06). Bound and document the three that exist; consider lowering the OpenAI SDK's own `max_retries` so the budget is legible |
| Error taxonomy | Typed hierarchy with status/code/request-id attributes | `APITimeoutError(APIConnectionError)` hierarchy | Hierarchy under one base `RequestException` | Three categories as subclasses of the currently raised `ValueError`/`RuntimeError`, so the host gets typed catches and the existing suite is untouched (TS-04, tension #2) |
| Usage reporting | `usage` on the response object | usage metadata on the response | n/a | Data already collected in memory; the open question is only whether it reaches the caller (DF-01, tension #1) |
| Logging | Namespaced logger, no handlers installed | Namespaced logger | `NullHandler` on the package logger (official guidance, HIGH) | `logging.getLogger("exercise_ai")` + `NullHandler`; handler attachment stays in the CLI adapter (TS-03) |
| Per-call config | Construction defaults + `with_options(...)` per call | `config=` per call | n/a | Env for defaults (locked), function arguments for per-call overrides — never `os.environ` mutation (DF-03, tension #3) |
| Process exit | Never | Never | Never | `sys.exit` only in the CLI adapter (TS-01) |

---

## Sources

**HIGH confidence — official documentation**

- [Python Logging HOWTO — "Configuring Logging for a Library"](https://docs.python.org/3/howto/logging.html) — namespaced loggers, `NullHandler` only, never configure the root logger, "do not add any handlers other than NullHandler". Underpins TS-03.
- [`logging.handlers` / `NullHandler` reference](https://docs.python.org/3/library/logging.handlers.html) and [`logging.lastResort`](https://docs.python.org/3/library/logging.html) — why an unconfigured library still leaks WARNING+ to stderr.
- Context7 `/openai/openai-python` — README "Timeouts" and `_constants.py`: default timeout 10 min, `DEFAULT_MAX_RETRIES = 2`, `INITIAL_RETRY_DELAY = 0.5`, `MAX_RETRY_DELAY = 8.0`; per-request override via `with_options(timeout=…)`. Underpins TS-05 and the comparison table.
- Context7 `/googleapis/python-genai` — `types.HttpOptions.timeout: Optional[int] = None` documented in **milliseconds**, and `_api_client.get_timeout_in_seconds` confirming `None` → no httpx timeout; `APITimeoutError(APIConnectionError)`. Underpins the TS-05 Gemini finding.

**MEDIUM confidence — practitioner consensus and vendor SDK guidance**

- [python-list, "exceptions vs. sys.exit()"](https://mail.python.org/pipermail/python-list/2008-September/665793.html) and the [threaded replies](https://bytes.com/topic/python/840428-python-style-exceptions-vs-sys-exit) — "a library module should never call `sys.exit()`"; also "a library should never print error or status messages. Messages should either be sent to the caller somehow, or handled using the logging facility." Old thread, but the guidance is unchanged and corroborated below. Underpins TS-01, TS-03, DF-04.
- [SO 13992662 — `sys.exit` vs `SystemExit`](https://stackoverflow.com/questions/13992662/using-sys-exit-or-systemexit-when-to-use-which) — exiting belongs "as high up as possible"; deeply embedded `sys.exit` is a design smell.
- [MFG_PDE issue #546](https://github.com/derrring/MFG_PDE/issues/546) — a real project doing exactly this migration (library `sys.exit` → exception hierarchy, `sys.exit` left only in `__main__`). Useful as a worked precedent for TS-01 + TS-04 together.
- [SE.SE 310415 — best practice for custom exception classes](https://softwareengineering.stackexchange.com/questions/310415/what-is-considered-best-practice-for-custom-exception-classes) — subclass only where callers must react differently; YAGNI for internal consumers; error codes are "a low-level implementation detail leaking into your abstractions". Underpins TS-04 and tension #2.
- [`python-errors-and-logging` skill](https://github.com/leynos/python-skill/blob/a4123c75/skills/python-errors-and-logging/SKILL.md) — exceptions are public API; package base class with `*Error` suffix; wrap vendor errors at the layer boundary with `raise … from exc`.
- [Bird SDK concepts](https://bird.com/en-us/docs/sdks/concepts) — the two-tier config pattern (construction-only identity/transport vs per-call-overridable lifecycle knobs), idempotency-key-per-logical-call, retry only transient failures. Underpins DF-03 and the AF-04 reasoning.
- [SDK Design for Your Public API](https://khimananda.com/blog/sdk-design-for-your-public-api) — typed error hierarchies carrying request id and retryability; expose rate-limit/usage metadata on response objects rather than only in logs. Single-vendor blog; treated as corroboration, not authority.
- [Custom exception hierarchy design](https://engineersofai.com/docs/python/python-foundation/error-handling-and-defensive-engineering/custom-exceptions) — structured attributes over message text; `raise … from original`.

**HIGH confidence — direct reading of this repository (2026-09-16)**

- `exercise-ai/main.py` — `sys.exit` ×4, `print` to stdout, `--out` write, import-time `sys.path.insert` + `load_dotenv`, `os.environ` mutation for `--provider`/`--reasoning`.
- `exercise-ai/models.py` — `GenerationRequest.quantidade` bounded only by `gt=0`; `Exercise` / `ExerciseBatch` text-only shape.
- `exercise-ai/failover.py` — `os.environ["LLM_PROVIDER"]` written and never restored; `[FAILOVER]` printed to stderr.
- `exercise-ai/reliability.py` — `"Gerando…"` / `"Validando…"` / duration printed to stderr; postmortem written to a package-internal path on final failure.
- `exercise-ai/generator.py`, `generator_gemini.py` — `timeout=30.0` on the OpenAI/Grok clients, **no timeout** on the Gemini client, up to 5 model candidates, `retriable` / `api_error_kind` attributes patched onto plain `RuntimeError`.
- `exercise-ai/token_usage/collector.py` — module-level `_collector` singleton, `run_id` already accepts a caller-supplied value, events held in memory until `flush()` appends NDJSON and clears.
- `exercise-ai/output_paths.py`, `math_check.py` — package-relative artifact directories; module-level mutable buffers.
- `.planning/PROJECT.md`, `.planning/seeds/SEED-003-host-embed-images-storytelling.md`, `.cursor/rules/20-ai-engineering.mdc` — locked decisions, scope boundaries, and the KISS/YAGNI + centralized-timeout/retry rules.

**Judgement, not sourced practice (stated as such)**

- The entire demo-page section (DM-01 … DM-06) and its scope-creep list. No credible published practice exists for "one-off internal integration-handoff demo page"; the items are derived from the demo's stated purpose and from what the host team must leave understanding.
- The recommendation in tension #2 to use subclasses of the already-raised exception types (zero-regression path) rather than either a pure `kind` attribute or a fresh independent hierarchy.
- The recommendation to promote DF-05 (dry-run) into the v2.0 MVP.
- The `ThreadingHTTPServer` warning in DM-06 — inferred from the shared mutable globals found in the code, not from a published source.

---
*Feature research for: embeddable in-process exercise-generation library (host-consumed) + throwaway integration demo*
*Researched: 2026-09-16*
