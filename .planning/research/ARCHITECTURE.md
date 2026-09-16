# Architecture Research

**Domain:** Python LLM pipeline — extracting an embeddable library boundary from a CLI-first codebase
**Researched:** 2026-09-16
**Confidence:** HIGH

> Scope note: this is v2.0 integration research for an **existing** architecture (v1.2 shipped).
> Nothing here proposes redesigning the pipeline. The recommendation is one new module,
> a delegating `run()`, and four small edits at named call sites.

## Standard Architecture

### System Overview

The conventional shape for this problem is **library core + thin CLI adapter**: one callable
boundary that returns data and raises exceptions, with every presentation concern (stdout
rendering, file output, process exit) pushed to the outermost layer. The three consumers —
argparse CLI, `gerar` wizard, demo — are peers of each other but **not** peers at the same
depth: the CLI and wizard share one adapter (`main.run`), while the demo talks to the service
directly.

```
┌──────────────────────────────────────────────────────────────────────┐
│                      PRESENTATION / ADAPTERS                          │
│   (owns: stdout, stderr, files, sys.exit, .env loading, argparse)     │
│                                                                       │
│  ┌──────────────┐   ┌──────────────┐          ┌───────────────────┐  │
│  │ main.main()  │   │  wizard.py   │          │ demo/server.py    │  │
│  │  argparse    │   │  gerar       │          │ stdlib HTTP       │  │
│  └──────┬───────┘   └──────┬───────┘          └─────────┬─────────┘  │
│         │                  │                            │            │
│         │   both funnel    │                            │            │
│         └────────┬─────────┘                            │            │
│                  ▼                                      │            │
│         ┌──────────────────┐                            │            │
│         │   main.run()     │  CLI adapter:              │            │
│         │  print / --out   │  text + JSON + exit 1      │            │
│         │  sys.exit(1)     │                            │            │
│         └────────┬─────────┘                            │            │
└──────────────────┼──────────────────────────────────────┼────────────┘
                   │                                      │
═══════════════════▼══════════════════════════════════════▼════════════  ← THE SEAM
┌──────────────────────────────────────────────────────────────────────┐
│                    SERVICE BOUNDARY  (service.py — NEW)               │
│   generate_batch(request, *, max_retries, provider, reasoning)        │
│      → ExerciseBatch        raises ConfigError / ValueError / RuntimeError │
│   owns: run lifecycle (begin_run/flush), scoped env overrides         │
│   forbidden: print to stdout, write exercise files, sys.exit          │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                      EXISTING PIPELINE (unchanged)                    │
│   failover.generate_with_failover                                     │
│        └─ reliability.generate_validated_batch   (bounded RELY loop)  │
│              ├─ generator.generate_exercises → OpenAI | Gemini | Grok │
│              └─ validator.validate_exercise_batch → math_check        │
│   cross-cutting: token_usage (singleton), reasoning, prompts, models  │
└──────────────────────────────────────────────────────────────────────┘
```

**Import direction rule (the one invariant that keeps this honest):**

```
demo/server.py ──┐
                 ├──> service.py ──> failover ──> reliability ──> generator / validator
main.py ─────────┘                                                      └──> models
wizard.py ──> main.py   (CLI surface reusing the CLI adapter — allowed)
```

Nothing at or below `service.py` may import `main` or `wizard`. This is the whole boundary,
and it is mechanically checkable with one grep.

### Component Responsibilities

| Component | Responsibility | Status in v2.0 |
|-----------|----------------|----------------|
| `service.py` | The embed boundary. Resolve retries, scope env overrides, own the token-usage run lifecycle, call the pipeline, return `ExerciseBatch` or raise. | **NEW** |
| `main.run()` | CLI adapter. Render text to stdout, write `--out` JSON, log, write fail logs, `sys.exit(1)`. | **MODIFIED** (body delegates; behaviour identical) |
| `main.main()` | argparse parsing, CLI-level env set, build `GenerationRequest`. | **UNCHANGED** |
| `wizard.py` | Interactive prompt collection; delegates to `main.run`. | **UNCHANGED** |
| `failover.py` | Single OpenAI↔Gemini switch on eligible permanent errors. | **UNCHANGED** (env restore handled above it) |
| `reliability.py` | Bounded regeneration loop; `resolve_max_retries`. | **MODIFIED** (config errors gain `kind`) |
| `generator.py` | Provider dispatch, client construction, API error mapping. | **MODIFIED** (config errors gain `kind`) |
| `models.py` | Pydantic schemas. | **MODIFIED** (quantity upper bound moves here) |
| `demo/server.py` | Throwaway stdlib HTTP page consuming the service. | **NEW** |

## Recommended Project Structure

```
GeradorExercicios/
├── exercise-ai/
│   ├── service.py          # NEW — the embed boundary + ConfigError
│   ├── main.py             # MODIFIED — argparse + run() adapter
│   ├── wizard.py           # unchanged
│   ├── failover.py         # unchanged
│   ├── reliability.py      # MODIFIED — ConfigError kind
│   ├── generator.py        # MODIFIED — ConfigError kind
│   ├── generator_gemini.py # unchanged
│   ├── validator.py        # unchanged
│   ├── math_check.py       # unchanged
│   ├── models.py           # MODIFIED — MAX_QUANTIDADE + le=40
│   ├── reasoning.py        # MODIFIED — ConfigError kind
│   ├── output_paths.py     # unchanged (CLI-only concern)
│   ├── prompts.py          # unchanged
│   ├── token_usage/        # unchanged
│   └── tests/              # MODIFIED — 3 tests pinned to main's internals
└── demo/
    └── server.py           # NEW — stdlib http.server, outside CI
```

### Structure Rationale

- **`service.py` sits beside the modules it calls, not above them.** Packaging and the
  `exercise_ai/` rename are parked, so flat modules stay. A host puts `exercise-ai/` on
  `sys.path` and does `import service`. Because the other modules import each other by bare
  name (`from models import ...`), that same `sys.path` entry makes the whole tree resolve —
  so **`service.py` needs no `sys.path` bootstrap of its own**. The one in `main.py:15-17`
  exists because `main.py` is run as a script, which is a different situation.
- **`demo/` lives outside `exercise-ai/`** precisely so it must go through the public seam.
  A demo living inside the package could reach for internals by accident; one living outside
  has to do what a real host does. It is excluded from CI, so it may not import pytest
  fixtures or test helpers.
- **No `errors.py`.** The error contract is part of the boundary, so `ConfigError` is defined
  in `service.py` and re-exported nowhere else. One new file, not two. If the hierarchy ever
  grows past two classes, split then — not now.

## Architectural Patterns

### Pattern 1: Service facade with a thin CLI adapter

**What:** The library exposes one function that takes a request object and returns data.
The CLI is a wrapper that converts the returned data to text and the raised exceptions to
exit codes. This is the dominant Python convention, and there is a well-known reference
implementation: **`mypy.api.run()`** exists solely so another Python application can run mypy
in-process, and it returns `(normal_report, error_report, exit_status)` instead of writing to
the real streams and exiting. Click institutionalises the same split with `standalone_mode`:
by default `Command.main()` catches exceptions, prints, and calls `sys.exit()`; setting
`standalone_mode=False` disables exactly those two behaviours so a programmatic caller gets
the return value and the exception instead. **[HIGH — official mypy docs; official Click docs]**

The PyPA `console_scripts` specification pushes the same discipline at the process edge: the
entry-point function "may return an integer to be used as a process exit code", and the
generated wrapper is literally `sys.exit(main())`. Exit is the wrapper's job, not the
function's. **[HIGH — PyPA interoperability specification]**

**When to use:** whenever a second consumer appears. That is now.

**Trade-offs:** one extra indirection and one extra file. In exchange the pipeline becomes
callable, the CLI keeps its exact behaviour, and the presentation logic stops being load-bearing.
The cost is real but small; the alternative (host shells out to the CLI and parses stdout) is
strictly worse and was already rejected by the milestone goal.

**Example — the seam:**

```python
# exercise-ai/service.py  (NEW)
"""Embed boundary: GenerationRequest → ExerciseBatch. No print, no files, no sys.exit."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

from failover import generate_with_failover
from models import ExerciseBatch, GenerationRequest
from reliability import resolve_max_retries
from token_usage import begin_run, flush_token_usage


class ConfigError(ValueError):
    """Configuração inválida ou ausente. ``kind`` distingue o motivo para o host."""

    def __init__(self, message: str, *, kind: str) -> None:
        super().__init__(message)
        self.kind = kind


def generate_batch(
    request: GenerationRequest,
    *,
    max_retries: int | None = None,
    provider: str | None = None,
    reasoning: str | None = None,
) -> ExerciseBatch:
    """Gera e valida um lote. Levanta ConfigError/ValueError/RuntimeError; nunca encerra o processo."""
    with _scoped_env(provider=provider, reasoning=reasoning):
        begin_run()
        try:
            n = resolve_max_retries(max_retries)
            return generate_with_failover(request, max_retries=n)
        finally:
            flush_token_usage()
```

**Example — `run()` becomes the adapter.** Everything that stays is a presentation concern:

```python
# exercise-ai/main.py  (MODIFIED — only the try block changes)
def run(request, out_path, max_retries=None) -> None:
    _configure_logging()                       # stays: handler config is the app's job
    logger.info("Início da geração de exercícios")
    logger.info("Parâmetros: ...", ...)        # stays: pinned by tests on run()

    try:
        validated_batch = service.generate_batch(request, max_retries=max_retries)

        print(format_batch_text(validated_batch))          # stays: stdout rendering
        out = resolve_success_out_path(out_path)           # stays: file output
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(validated_batch.model_dump(), indent=2,
                                  ensure_ascii=False), encoding="utf-8")
        logger.info("Geração concluída com sucesso → %s", out)

    except ValueError as val_err:              # stays: ConfigError subclasses ValueError,
        ...                                    #        so this branch is unchanged
        sys.exit(1)                            # stays: exit is the adapter's job
    ...
    finally:
        flush_token_usage()                    # stays: idempotent safety net (D-04)
```

Exactly four things move out of `run()`: `begin_run()` (main.py:203),
`resolve_max_retries(...)` (main.py:215), `generate_with_failover(...)` (main.py:216), and the
`finally: flush_token_usage()` ownership (main.py:258 — the call itself stays as a no-op net).

### Pattern 2: Scoped environment override (the env-restore fix)

**What:** A `contextlib.contextmanager` that snapshots the environment keys it will disturb and
restores them in `finally`. This is the standard answer to "per-call override of process-wide
config" and appears in essentially identical form in `unittest.mock.patch.dict(os.environ, ...)`
(official stdlib), in `snakeoil.contexts.os_environ`, and in the `pollute` package. All of them
mutate `os.environ` **in place** rather than rebinding it, so that references held elsewhere
(and the child-process environment) stay correct. **[HIGH — stdlib `unittest.mock` docs;
corroborated by two independent third-party implementations]**

The `snakeoil` implementation carries the note "this is explicitly not thread safe", which
matches this milestone's constraint exactly: one generation at a time, sequential.

**When to use:** when config is read deep in the stack from a process-global source and you
cannot thread a parameter down without a large refactor. That is precisely this codebase —
`generator._resolve_provider()` (generator.py:36-50) and
`reasoning.resolve_reasoning_effort()` (reasoning.py:28-38) read `os.environ` far below the
boundary, so an env-scoped override is the smallest correct mechanism.

**Trade-offs:** still global mutation, just balanced. It is not thread-safe and does not
compose with concurrent callers — acceptable and explicitly in-contract here. It is strictly
better than the status quo, which mutates and never restores.

**The non-obvious requirement:** `LLM_PROVIDER` must be guarded on **every** call, not only
when the caller passes `provider=`. `failover._default_switch_provider` (failover.py:54-55)
writes `os.environ["LLM_PROVIDER"]` during a failover and never restores it, so a host that
suffers one OpenAI timeout has its environment silently switched to Gemini **for the rest of
the process**. Guarding only caller-supplied keys would miss this entirely.

```python
_GUARDED = ("LLM_PROVIDER", "LLM_REASONING_EFFORT")

@contextmanager
def _scoped_env(*, provider: str | None, reasoning: str | None) -> Iterator[None]:
    """Restore guarded keys on exit — failover mutates LLM_PROVIDER even if we don't."""
    originals = {k: os.environ.get(k) for k in _GUARDED}
    if provider is not None:
        os.environ["LLM_PROVIDER"] = provider
    if reasoning is not None:
        os.environ["LLM_REASONING_EFFORT"] = reasoning
    try:
        yield
    finally:
        for key, value in originals.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
```

**Why this does not regress the CLI:** `main.main()` sets `os.environ["LLM_PROVIDER"]` at
main.py:282 **before** calling `run()`, so the service snapshots the already-set value and
restores it to the same value. `test_main.py::test_cli_provider_override_sets_env` (line 191)
and `test_cli_provider_grok_sets_env` (line 233) both assert the variable is still set after
`main.main()` returns — and both still pass. The CLI keeps owning process-level config;
the service's `provider=`/`reasoning=` kwargs exist for hosts and the demo. Do **not** move the
CLI's env assignment into the service call: that would restore the variable and break both tests.

I verified no test asserts that `LLM_PROVIDER` remains switched to the peer after a failover
(`test_run_failover_writes_out_and_redacts` passes `switch_provider=lambda name: None`), so
restoring it is regression-free. **[HIGH — read the test suite directly]**

### Pattern 3: Error contract by subclassing the built-in the caller already catches

**What:** Give the library a distinguishable exception type, but subclass the built-in whose
semantics already fit. Standard guidance is to define a root exception per library so callers
can catch everything with one clause; the refinement that matters here is that inheriting from
a *specific* built-in is better when the semantics fit, because "callers who catch `ValueError`
will automatically catch yours too, which is the correct behaviour in most library code."
**[MEDIUM — practitioner consensus across several independent sources, not an official spec]**

This reconciles the locked decision (a `kind` attribute on config `ValueError`s) with the
conventional pattern, at zero regression cost: `ConfigError(ValueError)` is caught unchanged by
`run()`'s existing `except ValueError` branch (main.py:231), prints the same message, and exits
1 — while a host can write `except ConfigError as e: e.kind`.

It is also consistent with how this codebase already tags errors: `generator.py:93-105` attaches
`retriable` and `api_error_kind` to `RuntimeError`. Attribute tagging is the established local
idiom; `ConfigError` adds a type only where the host needs to branch.

**Resulting host-facing contract — built entirely from types that already exist:**

| Raised | Meaning for the host | Attributes | Raise sites |
|--------|---------------------|------------|-------------|
| `ConfigError` (a `ValueError`) | Environment/config is wrong; the host must fix it. Not retryable. | `.kind` | generator.py:50, 57, 65; failover.py:47, 49-51; reliability.py:46-48, 50-52; reasoning.py:35-37; main.py:82-94 |
| `ValueError` (bare) | Batch failed validation after the bounded regenerations. | — | validator.py:34, 66; reliability.py:133-136 |
| `RuntimeError` | Provider/API failure. | `.retriable`, `.api_error_kind` | generator.py:93-141 |

Suggested `kind` values, drawn from the existing messages rather than invented:
`missing_key`, `unknown_provider`, `invalid_max_retries`, `invalid_reasoning`.

```python
# exercise-ai/generator.py:50 — before
raise ValueError(_MISSING_KEY_MSG)
# after
raise ConfigError(_MISSING_KEY_MSG, kind="missing_key")
```

The message strings must not change: `test_main.py:90` and the `test_logging_security.py`
assertions match on message text.

### Pattern 4: The boundary owns the run lifecycle

**What:** Whoever owns "one call" owns the setup and teardown of per-call state. The token
collector is a module-level singleton (`collector.py:125`) whose `begin_run()` clears the buffer
(`collector.py:47-50`). Today `main.run()` brackets it. If the service did not, a host calling
the boundary in a loop would accumulate `UsageEvent` objects forever and attribute run N's
tokens to run N+1 — an unbounded memory leak plus corrupted observability.

So `service.generate_batch()` calls `begin_run()` on entry and `flush_token_usage()` in
`finally`. `run()` keeps its own `finally: flush_token_usage()` as a documented-idempotent
safety net (the buffer is already cleared, so it returns immediately at collector.py:104), which
keeps `test_token_usage.py::test_main_run_flush_in_finally` passing.

**Trade-off worth stating plainly:** flushing writes NDJSON under
`exercise-ai/token-usage/<day>/<provider>.ndjson` and prints `[USAGE] resumo` lines to stderr.
That is a file side effect the host inherits from a "library" call. Two mitigations already
exist and need no new code: `TOKEN_USAGE_DIR` is injectable (collector.py:16), and the summary
goes to stderr which a host can capture. Do not build an opt-out flag for this now — YAGNI
until a host actually objects.

**One ordering shift to verify:** flushing inside the service means `[USAGE] resumo` lands on
stderr slightly earlier than today (before `logger.info("Geração concluída...")`). No test
asserts relative ordering within stderr — they all assert membership, and stdout/stderr are
captured into separate buffers — so this is safe, but it is the single behavioural difference
worth an explicit check during verification.

## Data Flow

### Request flow (host / demo)

```
host code
   │  GenerationRequest(materia, topico, dificuldade, quantidade)
   ▼
service.generate_batch(request, provider=?, reasoning=?, max_retries=?)
   │  _scoped_env snapshots LLM_PROVIDER + LLM_REASONING_EFFORT
   │  begin_run()                       ← clears the singleton buffer
   ▼
resolve_max_retries  →  generate_with_failover
   │                        └─ generate_validated_batch (RELY loop)
   │                              ├─ generate_exercises  → provider SDK
   │                              └─ validate_exercise_batch → math_check
   ▼
ExerciseBatch returned  ──────────────────────────────────┐
   │  finally: flush_token_usage()                        │
   │  finally: env restored (incl. any failover switch)   │
   ▼                                                      ▼
host serialises / renders as it wishes        or  ConfigError / ValueError / RuntimeError
                                                   propagates — host process survives
```

### Request flow (CLI — unchanged externally)

```
argv → main.main() → argparse validation (exit 2 on bad input, before any LLM call)
                   → os.environ["LLM_PROVIDER"] / ["LLM_REASONING_EFFORT"]
                   → GenerationRequest
                   → main.run()
                        → service.generate_batch()
                        → print(format_batch_text(...))        [stdout]
                        → write exercicios-gerados/success/…   [file]
                        → on error: stderr + fail log + sys.exit(1)
```

`wizard.run_wizard()` enters this same flow at `main.run()` (wizard.py:248), which is why the
wizard needs **zero changes**.

### State management

There is no application state store. The three pieces of mutable process state, and who owns
each after this change:

| State | Location | Owner after v2.0 |
|-------|----------|------------------|
| Token event buffer | `collector._collector` singleton (collector.py:125) | `service.generate_batch` (begin/flush bracket) |
| `LLM_PROVIDER`, `LLM_REASONING_EFFORT` | `os.environ` | CLI sets process-wide; service scopes and restores per call |
| Math postmortem buffers | `math_check` drain functions (reliability.py:19-23, 66-71) | unchanged — drained inside the RELY loop |

## Scaling Considerations

**The template's user-scale table does not apply here** and inventing one would be noise. This
is an in-process library called sequentially by a single host, with an explicit one-generation-
at-a-time contract. There are no users, requests/sec, or datastores to scale.

The honest limits, in the order they will actually bite:

1. **Provider rate limits and latency** — already handled: 30s timeouts (generator.py:58, 69),
   bounded regeneration (max 3), single failover switch. Nothing to add.
2. **Concurrency** — the first thing that breaks if the contract is violated. The token
   collector singleton and the `os.environ` provider switch are both process-global; two
   simultaneous `generate_batch` calls would interleave usage events and race on `LLM_PROVIDER`.
   This is why the demo must serialise (see Integration Points). Out of scope to fix; in scope
   to **document at the boundary** so the host team knows the rule.
3. **Batch size** — capped at 40 by the domain bound. Fine.

## Anti-Patterns

### Anti-Pattern 1: `sys.exit()` in library code

**What people do:** call `sys.exit(1)` on failure deep in the call stack. Here:
`main.run()` at main.py:238, 246, 254, plus `wizard.py:180, 238`.

**Why it's wrong:** `sys.exit` raises `SystemExit`, which inherits from `BaseException`, not
`Exception` — so a host's `except Exception` will not catch it and the host process dies.
This is the exact failure the milestone requirement "falha no gerador não derruba o processo do
host" names. PEP 348 documents the rationale for that inheritance split. **[HIGH]**

**Do this instead:** raise; let the outermost adapter exit. Keep all three `sys.exit(1)` calls
exactly where they are in `run()` — that function *is* the adapter, and ~25 tests across five
files assert `SystemExit` from it. The fix is not to remove them but to put the seam *below*
them, which `service.py` does.

### Anti-Pattern 2: Printing to the caller's streams

**What people do:** `print(..., file=sys.stderr)` scattered through pipeline modules:
`reliability.py:92-95, 112, 142-145` (stage/progress), `failover.py:80, 89` (`[FAILOVER]`),
`generator.py:116, 219, 237, 255` (`[API:*]`), `collector.py:165, 181, 189` (`[USAGE]`),
`reasoning.py:71-74`, and `validator.py:19-24`, which dumps the **entire batch JSON** to stderr
on any validation failure.

**Why it's wrong:** the official Python logging guidance is explicit — libraries should log to a
named logger and add only `NullHandler`, because "the configuration of handlers is the
prerogative of the application developer"; adding handlers or writing streams under the hood
"might well interfere with their ability to carry out unit tests and deliver logs which suit
their requirements." The same doc maps the decision directly: `print()` is for "ordinary usage
of a command line script", a logger is for "events that occur during normal operation", and an
exception is for reporting an error. **[HIGH — official Python logging HOWTO]**

**Do this instead — and deliberately not yet.** The correct end state is a dedicated logger
(`exercise_ai.progress`) with `NullHandler` in the library and a bare `%(message)s` stderr
handler attached by the CLI. But converting ~15 print sites is a behaviour-visible change across
modules whose output is asserted by name in many tests, for a benefit the host has not yet asked
for. That fails the smallest-correct-change and YAGNI tests.

**For this milestone:** leave the prints, and *document* that the library writes progress and
diagnostics to `sys.stderr`. A host silences them with `contextlib.redirect_stderr(io.StringIO())`
— which works because `print(file=sys.stderr)` resolves `sys.stderr` at call time, and because
`main._StderrStream` (main.py:40-48) was already written to honour redirection. The existing
tests prove the mechanism: they capture the whole pipeline's stderr with exactly this technique
(test_main.py:39). Flag the logging conversion as a **candidate follow-up phase**, not v2.0 work.

### Anti-Pattern 3: Mutating `os.environ` and not restoring it

**What people do:** `failover._default_switch_provider` (failover.py:54-55) and
`main.main()` (main.py:282, 290) and `wizard.run_wizard()` (wizard.py:233, 240) all assign to
`os.environ` with no restore.

**Why it's wrong:** in a CLI this is invisible because the process exits immediately. In a host
it is a permanent, action-at-a-distance mutation of global state — and for the failover case the
host did not even ask for it. The project's own Python rule lists "global mutable state" under
*Avoid*.

**Do this instead:** the scoped context manager of Pattern 2, always guarding `LLM_PROVIDER`.
Leave the CLI's assignments alone (pinned by tests, harmless pre-exit).

### Anti-Pattern 4: Module-level singleton holding per-call state

**What people do:** `_collector = TokenUsageCollector()` at collector.py:125, reached via
`get_collector()` from generator.py and reliability.py.

**Why it's wrong:** it silently assumes one run per process. `begin_run()` *clears* the buffer
(collector.py:49), so in a host the first call of run N+1 wipes anything unflushed from run N,
and skipping `begin_run()` leaks events across runs forever.

**Do this instead — scoped, not rearchitected.** Do **not** convert the collector to an injected
instance this milestone: it is reached from two modules via a module-level accessor, and
threading an instance through `failover → reliability → generator` would touch every signature
for no behaviour change. Instead, make the *boundary* own the lifecycle (Pattern 4 above) and
document the one-at-a-time contract. Revisit only if a host needs concurrent or nested runs.

### Anti-Pattern 5: Import-time side effects (`load_dotenv`)

**What people do:** `main.py:20-23` resolves a `.env` path and calls `load_dotenv()` at module
import time. Merely importing `main` mutates the importing process's environment.

**Why it's wrong:** a host that imports the pipeline gets its own environment rewritten from a
file it may not know exists, before it has executed a line of its own code. Config ownership
silently transfers to the library.

**Do this instead:** nothing — and that is the point. Because the seam sits *below* `main.py`
and `service.py` does not import `main`, a host importing `service` never triggers `load_dotenv`.
The anti-pattern is neutralised by the import direction rather than by editing main.py, which
keeps CLI behaviour bit-identical. The demo then has to load config explicitly, which is a
feature: it shows the host team exactly where config ownership sits.

### Anti-Pattern 6: Business rules in the argparse layer

**What people do:** the 1–40 quantity cap lives in `main._positive_quantidade`
(main.py:97-109, constant at main.py:37), while `GenerationRequest.quantidade` only enforces
`gt=0` (models.py:19). A library caller can request 10,000 exercises.

**Why it's wrong:** it is a domain invariant enforced only on the path that happens to have a
CLI in front of it. Any second consumer bypasses it. The project's rules call for Fail Fast and
for keeping configuration and business rules out of presentation code.

**Do this instead:** move the bound into the model and keep the argparse check as a UX layer.

```python
# exercise-ai/models.py
MAX_QUANTIDADE = 40

class GenerationRequest(BaseModel):
    ...
    quantidade: int = Field(..., gt=0, le=MAX_QUANTIDADE,
                            description="Quantidade exata de exercícios a gerar")
```

```python
# exercise-ai/main.py — keep the argparse check, source the constant
from models import MAX_QUANTIDADE
_MAX_QUANTIDADE = MAX_QUANTIDADE   # wizard reads main_mod._MAX_QUANTIDADE (wizard.py:202)
```

This is **not** duplicated business knowledge: the number lives in exactly one place. The
argparse check remains because it produces the CLI's exit code 2 and its Portuguese message
(`test_main.py:151-163` asserts "máximo 40"), which a Pydantic `ValidationError` would not.
Pydantic v2's `ValidationError` subclasses `ValueError`, so the library path stays inside the
error contract in Pattern 3 without extra handling.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| OpenAI / Grok | `openai` SDK, Structured Outputs via `client.beta.chat.completions.parse` (generator.py:207) | Unchanged. Grok reuses the OpenAI client against `api.x.ai/v1`. |
| Gemini | `google-genai` via `generator_gemini` (generator.py:334-337) | Unchanged. |
| Host application | **in-process function call** to `service.generate_batch` | New. No HTTP, no serialisation, no subprocess. Host must put `exercise-ai/` on `sys.path` and owns its own `.env`/env loading. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `main.run` → `service` | direct call, returns `ExerciseBatch` | The seam. `run()` keeps 100% of presentation. |
| `wizard` → `main.run` | direct call (wizard.py:248) | Unchanged. The wizard is a CLI surface, so reusing the CLI adapter is correct — routing it to `service` directly would force it to duplicate stdout rendering, file writing and exit handling. |
| `demo/server.py` → `service` | direct call | Must not import `main` or `wizard`. |
| `service` → `failover` | direct call (failover.py:58) | Unchanged signature. |
| anything → `main` | **forbidden below the seam** | The one invariant. Greppable. |

### Demo-specific integration notes

The demo is the only new consumer that introduces a runtime concern of its own:

- **Bind address.** `http.server.HTTPServer.address_family` defaults to `AF_INET` (verified: `2`
  on this machine), so serving on `http://[::1]:8642/` requires a subclass setting
  `address_family = socket.AF_INET6` (`23`). Without it the bind silently lands on IPv4.
  **[HIGH — empirically verified locally + stdlib docs]**
- **Threading vs. the one-at-a-time contract.** `ThreadingHTTPServer` handles each request in a
  thread; plain `HTTPServer` is a `socketserver.TCPServer` and serialises. Plain `HTTPServer`
  therefore satisfies the sequential contract for free, but the stdlib docs warn that browsers
  pre-open sockets "on which `HTTPServer` would wait indefinitely" — a demo that hangs in front
  of the host team is a bad demo. **[HIGH — official `http.server` docs]**

  **Recommendation, flagged for operator confirmation:** use `ThreadingHTTPServer` and wrap the
  single `service.generate_batch` call in one module-level `threading.Lock`. This is ~3 lines and
  it does **not** contradict the "no thread safety" constraint — the lock exists precisely
  *because* the library is not thread-safe, and it keeps generation strictly sequential while the
  socket layer stays responsive. If the operator prefers the letter of the constraint over its
  intent, plain `HTTPServer` is acceptable and simpler; the pre-open stall is a cosmetic
  annoyance, not a correctness bug.
- **Config.** The demo must load env itself (`dotenv.load_dotenv()` — already a project
  dependency — or rely on exported variables), because `service` deliberately does not.

### Test integration points — three tests are pinned to `main`'s internals

These will fail the moment `run()` delegates. All three are **modified**, not new, and each
fails loudly rather than silently:

| Test | Line | Why it breaks | Fix |
|------|------|---------------|-----|
| `test_main.py::test_main_source_keeps_plain_stderr_contract` | 98-108 | Asserts the string `"generate_with_failover"` appears in `main.py` **source text**; it moves to `service.py`. | Re-point that assertion at the new delegation (e.g. `"service.generate_batch" in msrc`); keep the `sys.exit(1)` and plain-stderr assertions as-is. |
| `test_main.py::test_cli_max_retries_passes_to_run` | 251-259 | `patch.object(main, "resolve_max_retries", ...)` — `run()` no longer calls it, so `resolv.call_args` is `None`. | Patch `service.resolve_max_retries` instead. |
| `test_failover.py::test_run_failover_writes_out_and_redacts` | 350-388 | `patch.object(main, "generate_with_failover", ...)` — the name no longer lives in `main`'s namespace. | Patch `service.generate_with_failover` instead. |

Everything else in the suite patches `reliability.generate_exercises`, which sits well below the
seam and is untouched. That is a large, free regression net for the extraction.

### Build order

Dependency-respecting sequence. Step 1 is the hinge; 2 and 3 are independent siblings; 0 is
detachable and can run first or in parallel.

```
0. Domain bound (independent, tiny)
        │
1. Seam extraction  ◄── everything else depends on this
        ├──► 2. Env hygiene
        ├──► 3. Error contract
        │         │
        └─────────┴──► 4. Demo
```

| # | Step | New / Modified | Depends on | Rationale |
|---|------|----------------|------------|-----------|
| 0 | Move the 1–40 bound into `models.py`; `main` imports the constant | MOD `models.py`, `main.py` | — | Self-contained and independent of the seam. Doing it first means the boundary is bound-safe from its first commit. |
| 1 | Create `service.py` with `generate_batch`; `run()` delegates; fix the 3 pinned tests | **NEW `service.py`**; MOD `main.py`, 2 test files | 0 (optional) | Pure move, no behaviour change. Must be first — every later step edits or consumes this module. Verification is simply "the existing suite is green". |
| 2 | Add `_scoped_env` + `provider`/`reasoning` kwargs; always guard `LLM_PROVIDER` | MOD `service.py` | 1 | Needs the boundary to exist. Independent of step 3. Verify the two CLI env-assertion tests still pass. |
| 3 | `ConfigError(ValueError)` + `kind` at the 9 raise sites; document the 3-way contract | MOD `service.py`, `generator.py`, `failover.py`, `reliability.py`, `reasoning.py`, `main.py` | 1 | Touches many files but each edit is one line. Independent of step 2 — can run in parallel. Message strings must not change. |
| 4 | `demo/server.py` — stdlib HTTP, IPv6 bind, serialised call, renders exercises + contract JSON | **NEW `demo/server.py`** | 1, 2, 3 | Last by necessity: it is the acceptance test for the boundary, and it needs the error contract to render failures meaningfully. Outside CI. |

**Why not fold 2 and 3 into 1:** step 1's whole value is that it is behaviour-preserving and
verifiable against the untouched test suite. Mixing in env-restore and new exception types would
mean a failing test could be either a bad extraction or a bad new behaviour. Keeping the pure
move separate is what makes "zero regression" checkable rather than asserted.

## Constraint Check

Two places where the research rubs against a stated rule. Neither is a contradiction I am
proposing to break, but both should be visible to the roadmapper:

1. **"Centralize configuration parsing and validation"** (`.cursor/rules/10-python.mdc`) points
   toward a `Settings` object, which is explicitly rejected as YAGNI for this milestone. The
   partial resolution: `service.py` becomes the single place that *scopes and bounds* config for
   a call, and step 3 centralises the config **error** contract, without introducing a config
   type. Config *parsing* stays distributed across `generator`, `reasoning` and `reliability`.
   This is a conscious partial compliance, not an oversight — worth recording so a future
   milestone can finish the job if a host ever needs programmatic config.
2. **Library logging** — official Python guidance says libraries must not write to the
   application's streams (Anti-Pattern 2). This codebase does, in ~15 places, and I am
   recommending **not** fixing it in v2.0 on YAGNI and regression-risk grounds, with
   `redirect_stderr` as the documented host escape hatch. This is research contradicting current
   behaviour and the milestone consciously deferring the fix; it should be logged as known debt
   rather than quietly accepted.

## Confidence Summary

| Finding | Confidence | Basis |
|---------|-----------|-------|
| Library core + thin CLI adapter is the conventional shape | HIGH | Official mypy docs (`mypy.api.run`), official Click docs (`standalone_mode`), PyPA `console_scripts` spec |
| Exit codes belong to the outermost wrapper, not library functions | HIGH | PyPA entry-points specification; PEP 348 on `BaseException` |
| Libraries must not write to the caller's streams; use a named logger + `NullHandler` | HIGH | Official Python logging HOWTO |
| stdout = primary output, stderr = messaging; non-zero exit on failure | HIGH | Command Line Interface Guidelines (clig.dev) |
| Scoped env override via context manager with `finally` restore | HIGH | stdlib `unittest.mock.patch.dict`; corroborated by `snakeoil.contexts`, `pollute` |
| Subclassing `ValueError` keeps existing `except` clauses working | MEDIUM | Practitioner consensus (multiple independent sources); no official spec |
| `HTTPServer` is single-threaded; IPv6 needs `address_family = AF_INET6` | HIGH | Official `http.server` docs + empirically verified on this machine |
| The three pinned tests and all named line numbers | HIGH | Read directly from this repository |
| Build order and new/modified classification | HIGH (judgement) | My own analysis, grounded in the dependency graph above — not sourced |

## Sources

- Python logging HOWTO — "Configuring Logging for a Library" — https://docs.python.org/3/howto/logging.html (official)
- PyPA Entry points specification — "Use for scripts" — https://packaging.python.org/en/latest/specifications/entry-points/ (official)
- `http.server` — `HTTPServer` vs `ThreadingHTTPServer` — https://docs.python.org/3/library/http.server.html (official)
- `unittest.mock` — `patch.dict(os.environ, ...)` — https://docs.python.org/3/library/unittest.mock.html (official)
- Click — "Exception Handling and Exit Codes" / `standalone_mode` — https://click.palletsprojects.com/en/stable/exceptions (official, via Context7)
- mypy — "Integrating mypy into another Python application" (`mypy.api.run`) — https://mypy.readthedocs.io/en/stable/extending_mypy.html (official)
- Command Line Interface Guidelines — https://clig.dev/ (community standard)
- PEP 348 — Exception Reorganization — https://peps.python.org/pep-0348/
- Functional Core / Imperative Shell (Gary Bernhardt, 2012) — pattern framing for pushing effects to the edge
- `snakeoil.contexts.os_environ` — https://pkgcore.github.io/snakeoil/_modules/snakeoil/contexts.html — reference env-restore implementation
- This repository, read directly: `main.py`, `failover.py`, `reliability.py`, `generator.py`, `validator.py`, `reasoning.py`, `wizard.py`, `models.py`, `output_paths.py`, `token_usage/collector.py`, and `tests/`

---
*Architecture research for: Python LLM pipeline — library boundary extraction from a CLI-first codebase*
*Researched: 2026-09-16*
