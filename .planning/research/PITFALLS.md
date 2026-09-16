# Pitfalls Research

**Domain:** Turning an existing Python CLI pipeline into an in-process embeddable library, plus a throwaway stdlib demo page
**Researched:** 2026-09-16
**Confidence:** HIGH for codebase-specific findings (read and, where marked, executed against the real modules on the operator's Windows machine); MEDIUM for ecosystem/doc-backed findings

> Scope note. This milestone adds an **embed boundary** to a system that already works as a CLI. Nothing here re-litigates LLM reliability, prompt design, validation strategy or failover policy — those were settled in v1–v1.2. Every pitfall below is about what changes when `run()` stops being the end of a process and starts being a function call inside somebody else's long-lived process, or when a demo page becomes the thing driving it.
>
> The operator's locked decisions (env stays the config source; no `Settings`; sequential only; stdlib-only throwaway demo on `[::1]:8642`; packaging parked) are treated as fixed. Where a locked decision genuinely increases a risk, it is flagged in a **Constraint check** line rather than argued against. Only one locked decision draws a real warning: see Pitfall 5.

---

## Critical Pitfalls

### Pitfall 1: `sys.exit()` in `run()` kills the host, and the host's `except Exception` will not save it

**What goes wrong:**
`main.run()` ends all three of its failure branches with `sys.exit(1)` (`main.py:238`, `:246`, `:254`). `sys.exit` raises `SystemExit`, which inherits from `BaseException`, **not** from `Exception`. A host that wraps the call in the idiomatic `try: ... except Exception:` does not catch it. The exception unwinds straight through the host's error handling; if nothing above catches `BaseException`, the host process exits with status 1. `wizard.run_wizard()` has the same shape via `raise SystemExit(1)` (`wizard.py:180`, `:238`).

Verified on this machine: a `SystemExit` raised inside a called function passes straight through an enclosing `except Exception` handler.

**Why it happens:**
It was correct before. In a CLI, `run()` *is* the end of the program, so exiting from the failure branch is the cleanest possible code. The refactor's danger is that `run()` keeps working perfectly in the CLI while being catastrophic when called — there is no failing test and no visible symptom until a real generation fails inside the host.

**How to avoid:**
Invert the ownership. `service.py` raises; `main.run()` becomes the adapter that catches and calls `sys.exit(1)`. Concretely: move the pipeline body into a service function that returns `ExerciseBatch` or raises, and leave the `except → print → write_fail_error_log → sys.exit(1)` block in `run()` where the CLI still owns it. The service must contain **zero** `sys.exit` and **zero** `SystemExit`.

**Warning signs:**
- `rg "sys\.exit|SystemExit" exercise-ai/` returns hits in any module reachable from `service.py`.
- A test that calls the service inside `pytest.raises(Exception)` passes only because `pytest.raises` accepts `BaseException` — write the guard as `except Exception` explicitly so it fails loudly.
- In the host: the process dies during generation with no traceback the host logged.

**Phase to address:** Embed boundary phase. This is the single defining requirement of the milestone.

---

### Pitfall 2: Artifact writes in `finally` / `except` blocks silently replace the real error

**What goes wrong:**
Two places write files on the failure path without protection, and both can destroy the error the host needs:

- `main.run()` ends with `finally: flush_token_usage()` (`main.py:255-258`). `flush()` does `day_dir.mkdir(parents=True, exist_ok=True)` and `path.open("a")` inside the package directory (`token_usage/collector.py:102-122`). If that raises `OSError`/`PermissionError`, Python discards the in-flight exception and propagates the `OSError` instead.
- `reliability._write_postmortem(POSTMORTEM_PATH)` is called from inside the `except ValueError` handler on retry exhaustion (`reliability.py:130`), also unprotected. A filesystem failure there replaces the real validation error with a path error.

Verified on this machine: raising from a `finally` block discards an in-flight `SystemExit` and propagates the new exception instead.

Note the asymmetry — `run()` *does* guard `write_fail_error_log` with `try/except OSError: pass` (`main.py:234-237`), so the protection pattern already exists in the codebase; it was just not applied to the other two sites.

**Why it happens:**
On the operator's machine the package directory is always writable, so these paths have never failed. In a host deployment the generator may sit in `site-packages`, a read-only mount, a container layer, or a directory the service account cannot write. The failure appears only in production, only on the error path, and it corrupts precisely the diagnostic the host was relying on.

**How to avoid:**
Wrap both sites the way `write_fail_error_log` is already wrapped (`except OSError: pass`, or log-and-continue). Separately, stop writing inside the package directory at all — see Pitfall 8, which removes the root cause.

**Warning signs:**
- A host error report whose type is `OSError`/`PermissionError` with a path under the generator's install directory, where a `ValueError`/`RuntimeError` was expected.
- The exception's `__context__` chain contains the real error while the surfaced type is a filesystem error.
- Run the test suite with the package directory made read-only; anything that changes error *type* is this bug.

**Phase to address:** Embed boundary phase.

---

### Pitfall 3: Windows cp1252 + LLM math output turns a successful generation into a failure

**What goes wrong:**
This is the sharpest Windows-specific hazard in the codebase, and it is already present.

`run()` prints the whole batch to stdout **before** writing the JSON file (`main.py:218-228`). LLM-generated math routinely contains `√`, `π`, `≠`, `≤`, `∛` — `math_check.py` itself has regexes matching exactly those characters, so the project already expects them in model output. On Windows, `locale.getpreferredencoding()` is `cp1252` and redirected/piped stdout uses it. `cp1252` cannot encode any of those characters.

Measured on this machine (`locale.getpreferredencoding(False)` → `cp1252`), running against the real project modules:

| Site | Result |
|------|--------|
| `main.format_batch_text(batch)` written to a cp1252 stream | **raises `UnicodeEncodeError`** |
| `validator._log_validation_failure(...)` batch dump to cp1252 stderr | **raises `UnicodeEncodeError`** |
| `failover.py:80` `[FAILOVER] openai → gemini` to cp1252 stderr | **raises `UnicodeEncodeError`** |

Three distinct consequences:

1. **Success reported as failure.** A perfect batch containing `√` crashes at `main.py:218`, is caught by `except Exception` (`:247`), prints "Falha inesperada", and exits 1 — *before* `out.write_text`. The host sees a failure; no JSON exists; the tokens were spent.
2. **Validation errors mutate into encoding errors.** `UnicodeEncodeError` is a subclass of `ValueError` (verified). `reliability.generate_validated_batch` catches `ValueError` from `validate_exercise_batch` and treats it as a retriable validation failure (`reliability.py:117`). So a crash inside the batch dump is misread as "the model produced a bad batch" and **triggers a paid regeneration**, then surfaces as `após 1 regenerações: 'charmap' codec can't encode character...`.
3. **Failover dies mid-hop.** `failover.py:80` is a bare `print` with a `→`, executed at the exact moment the primary provider has already failed.

`main.py:180` (argparse help) and `main.py:229` (logger) also carry `→`; the logger one degrades to logging's own error noise rather than raising, and the argparse one only bites when `--help` is redirected.

**Why it happens:**
The CLI is normally run in an interactive Windows Terminal, which is UTF-8, so nobody has hit it. A host embeds the generator in a service, a scheduled task, or a subprocess with captured output — all of which give you the locale codepage. The demo page will make it worse by generating a lot of math on a Windows box.

**How to avoid:**
Two small, proportionate changes:
- **Stop printing generated content from the library.** The service returns `ExerciseBatch`; only the CLI adapter renders it. This removes consequence 1 entirely and is already the milestone's stated design (`sem print`).
- **Make the remaining diagnostic writes encoding-proof.** Replace the `→` in `failover.py:80` and `main.py:180`/`:229` with ASCII (`->`), and have the CLI adapter reconfigure its own streams (`sys.stdout.reconfigure(encoding="utf-8", errors="replace")`) rather than assuming the library's callers did. `errors="replace"` on the diagnostic path means a stray model glyph degrades to `?` instead of aborting a run.

Also fix the `validator` dump (Pitfall 6) — that removes the regeneration-amplification path.

**Warning signs:**
- Any `UnicodeEncodeError` / `'charmap' codec can't encode` in host logs.
- An error message beginning `após N regenerações:` whose tail is a codec message.
- Token-usage NDJSON showing a `status=success` event for a run the host recorded as failed — the smoking gun for consequence 1.
- Cheap CI guard: assert no runtime `print`/log format string in `exercise-ai/` contains a non-Latin-1 character. One `rg` in a test.

**Phase to address:** Embed boundary phase owns the fix; the demo phase is where it will be *discovered* if it isn't fixed first, in front of the host team.

---

### Pitfall 4: `failover` repins `LLM_PROVIDER` for the rest of the host process's life

**What goes wrong:**
`failover._default_switch_provider` does `os.environ["LLM_PROVIDER"] = name` (`failover.py:54-55`) and never restores it. `generator._resolve_provider()` reads `LLM_PROVIDER` first (`generator.py:38-40`). So the *first* transient OpenAI timeout in a long-lived host permanently switches every subsequent generation to Gemini — including generations where the caller explicitly wanted OpenAI, and including generations hours later after OpenAI recovered. Nothing ever switches back.

The same pattern exists in `main.main()` (`main.py:282`, `:290`) and `wizard.run_wizard()` (`wizard.py:233`, `:240`) for `LLM_PROVIDER` and `LLM_REASONING_EFFORT`.

`os.environ` writes are pushed back into the real process environment, so the leak is not even confined to this library — every other component in the host sees the changed variable.

**Why it happens:**
In a CLI the process exits seconds later, so "never restore" is free and simpler. It is a textbook long-lived-process bug: the mod_wsgi project documents the same class of failure (env writes leaking between application instances) and concludes that long-running applications should not use process env for per-invocation configuration.

**How to avoid:**
Scope the mutation, don't remove env as the config source. A ~10-line `contextlib.contextmanager` that snapshots the keys it is about to touch and restores them (including restoring *absence*, via `os.environ.pop`) in a `finally`, wrapped around the failover switch and around the CLI's per-run overrides. This keeps env as the single config source — it only stops the library from making *permanent* writes.

**Constraint check:** fully compatible with "env stays the config source, no `Settings`". Reading env is untouched; only the library's own writes become scoped. Because concurrency is out of scope, the save/restore has no thread-safety problem — but note that `os.environ` mutation is inherently process-global, so this mitigation *depends* on the sequential contract holding. If the demo ever serves two generations at once, this fix silently breaks (see Pitfall 12).

**Warning signs:**
- `[FAILOVER]` appears once in host logs and every later `[USAGE]` line shows the peer provider.
- The host asks for `openai` and the returned usage says `gemini`.
- Test: call the service twice in one process, force an eligible error on the first, assert `os.environ.get("LLM_PROVIDER")` is byte-identical to its pre-call value (including having been unset).

**Phase to address:** Embed boundary phase. Already an explicit v2.0 target (`LLM_PROVIDER` restaurado) — this documents why and how to verify.

---

### Pitfall 5: Flat generic module names on the host's `sys.path` collide in both directions, non-deterministically

**What goes wrong:**
`main.py:14-17` does `sys.path.insert(0, current_dir)`. That publishes these top-level names into the host process: `main`, `models`, `prompts`, `validator`, `generator`, `generator_gemini`, `failover`, `reliability`, `reasoning`, `math_check`, `output_paths`, `wizard`, `token_usage`. `main`, `models`, `validator`, `prompts` and `token_usage` are among the most collision-prone names in Python.

Python resolves top-level imports by scanning `sys.path` in order, first match wins. Insert-at-0 means **we win**. The failure is bidirectional and depends on import order:

- **We shadow the host.** Host does `import models` expecting its own ORM layer, gets our Pydantic module. Symptom: `AttributeError: module 'models' has no attribute 'User'`, raised deep inside host code that nobody changed.
- **The host shadows us.** If the host imported *its* `models` first, `sys.modules["models"]` is already populated and our `from models import ExerciseBatch` returns the host's module. Symptom: `ImportError: cannot import name 'ExerciseBatch' from 'models'`, pointing at our import line but caused by the host's.

Which direction you get depends on whether the host imported first — i.e. on import order, which can differ between the host's dev machine and production. A third variant: during `exec_module` the module is already registered in `sys.modules`, so a circular or failing import can hand out a partially initialised module, producing an `AttributeError` for a name that plainly exists in the file.

**Why it happens:**
The flat layout was right for a single-file-ish lab. It only becomes a hazard at the moment a *second* codebase shares the interpreter — which is exactly what this milestone does.

**How to avoid — and an honest flag:**

> **Constraint check — this is the one locked decision that carries real residual danger.** Packaging/rename is parked until the host's stack is known, and that is a defensible call. But it means Pitfall 5 has **no prevention this milestone, only detection**. Every other pitfall here can be closed; this one can only be made loud. The roadmapper should treat "unpark packaging" as the first item of the next milestone, and the host team should be told the reserved name list *before* they integrate, not after.

Proportionate mitigation now, in `service.py`:
1. **A name-collision self-check at boundary import.** After the path bootstrap, assert each critical module's `__file__` resolves inside `exercise-ai/`; if not, raise a clear PT error naming the offending path. ~10 lines, no dependencies, and it converts a bizarre `AttributeError` three layers away into an actionable message.
2. **Decide insert-vs-append deliberately and write down why.** `insert(0)` breaks the host; `append` breaks us. Neither is correct — but `append` fails on *our* side with *our* error message, which is the kinder failure direction while packaging is parked.
3. **Hand the host team the reserved-name list** in the integration doc.

**Warning signs:**
- `ImportError: cannot import name X from 'models'` where `models.__file__` is not under `exercise-ai/`.
- `AttributeError` on a host module the host did not change, appearing right after the generator was integrated.
- Detection one-liner for the host: `python -c "import models; print(models.__file__)"` after importing the service.

**Phase to address:** Embed boundary phase (detection + documentation). Prevention belongs to the parked packaging milestone — the roadmapper should record it as explicitly deferred, not solved.

---

### Pitfall 6: The library writes to the host's stdout and stderr, including full generated batches

**What goes wrong:**
The pipeline is chatty, and all of it lands on whatever streams the host process happens to have:

| Site | What reaches the host |
|------|------------------------|
| `main.py:218` | the entire rendered batch, on **stdout** |
| `validator.py:19-24` | `[VALIDAÇÃO] <summary>` plus the **entire batch as pretty-printed JSON**, on stderr |
| `reliability.py:92-95`, `:112` | `Gerando…`, `Nª Regeneração`, `Validando…` |
| `reliability.py:142-145` | `duração total_ms=… chamadas=…`, from a `finally` |
| `collector.py:165`, `:181-192` | `[USAGE] …` per event plus per-run summary |
| `failover.py:80`, `:89` | `[FAILOVER] …` |
| `generator.py:116`, `generator_gemini.py:158` etc. | `[API:*] …` |
| `math_check.py:260-263` | `[MATH] …` |

The worst of these is `validator._log_validation_failure`: on any validation failure it dumps the **complete LLM-generated batch** to stderr. In a host with log aggregation that is unbounded model output — arbitrary length, arbitrary Unicode (Pitfall 3), and content the host never opted into indexing. If the topic text ever originates from an end user, it is also a path for injected content to reach an operator's log viewer.

Separately, `main._configure_logging()` attaches a handler to the `exercise_ai` logger and sets `propagate = False` (`main.py:50-58`). For a library that is backwards: a host that has configured structured JSON logging gets none of the generator's events, because `propagate=False` routes them around the host's handlers to raw stderr. The `if logger.handlers: return` guard also means a host that pre-attaches its own handler ends up with the level never set, so behaviour differs by import order.

**Why it happens:**
Every one of these was a deliberate, good CLI feature. `[USAGE]`, `[FAILOVER]` and `[VALIDAÇÃO]` are shipped v1.2 observability requirements. The mistake would be deleting them; the fix is moving where they are emitted.

**How to avoid:**
- Service returns data; the **CLI adapter** renders. `print(format_batch_text(...))` moves out of the service path.
- Convert the `print(..., file=sys.stderr)` diagnostics on the library side to `logger.*` calls on the `exercise_ai` logger. Then the host controls verbosity, format and destination with the standard mechanism it already has.
- In the library, follow the stdlib library convention: attach `logging.NullHandler()` and **do not** set level, format or `propagate`. Keep `_configure_logging()` — but call it from the CLI entry point only.
- Reduce the validator dump to a bounded summary (indices and field names that failed). Put the full batch behind `logger.debug` so it exists for the operator and is off by default for the host.

**Warning signs:**
- Host logs contain PT-BR exercise text, or lines starting `###  Exercício`.
- Host's JSON log pipeline shows unparseable raw lines interleaved with structured ones.
- Test: run the service under `contextlib.redirect_stdout`/`redirect_stderr` and assert both captures are empty on the success path.

**Phase to address:** Embed boundary phase.

---

### Pitfall 7: Import-time side effects — and the mirror-image bug of removing them

**What goes wrong:**
Importing `main` runs three things before any caller asks for anything (`main.py:14-23`): it mutates the host's `sys.path`, resolves a `.env` path, and calls `load_dotenv`.

`load_dotenv` writes into `os.environ` and defaults to `override=False`, so variables the host already set win and `.env` only fills gaps. That default is genuinely helpful here — but it still means the operator's `.env` silently injects keys into the host's global process environment for every variable the host had *not* set. Anything else in that process that enumerates `os.environ` — a crash reporter, a diagnostics endpoint, a subprocess spawn — now carries those keys.

The mirror-image bug is the more likely one to actually ship: if `service.py` is importable **without** importing `main`, then `.env` is never loaded, and the host gets `Nenhuma chave de API configurada` even though `.env` sits right there. Whichever way the refactor goes, config loading changes behaviour, and a test that imports `main` first will not catch it.

**Why it happens:**
`load_dotenv` at module scope is the canonical Python example, and for a script it is correct. For a library it makes an unavoidable global mutation a precondition of importing.

**How to avoid:**
Pick one owner and make it explicit:
- `service.py` does **not** call `load_dotenv`. It reads `os.getenv` and fails with a clear, `kind`-tagged error if a key is absent.
- `main.py` (the CLI adapter) keeps `load_dotenv` — the CLI owns the operator's `.env`.
- The `demo/` runner calls `load_dotenv` itself, explicitly, in its `__main__`.
- Document one line for the host: "we read `LLM_API_KEY` / `GEMINI_API_KEY` / `GROK_API_KEY` / `LLM_PROVIDER` / `LLM_REASONING_EFFORT` / `RELY_MAX_RETRIES` from the process environment; we do not load `.env` for you."

The `sys.path` bootstrap cannot be removed while packaging is parked. Make it a single guarded block in the boundary module, and cover it with the collision self-check from Pitfall 5.

**Constraint check:** compatible with env-as-config. This is about *who loads* `.env`, not about replacing env with an object.

**Warning signs:**
- `Nenhuma chave de API configurada` in a host where `.env` exists and is correct → nobody called `load_dotenv`.
- The host's env-var dump or crash report contains `LLM_API_KEY` → import-time injection is happening.
- Test: `import service` in a subprocess with a clean env and a populated `.env`, assert the key is absent from `os.environ`.

**Phase to address:** Embed boundary phase.

---

### Pitfall 8: Runtime artifacts are written inside the package directory

**What goes wrong:**
Three artifact roots are computed from `__file__` and live under `exercise-ai/`:

- `token_usage/collector.py:16` — `TOKEN_USAGE_DIR = <pkg>/token-usage`, appended to on every flush
- `output_paths.py:9-13` — `exercicios-gerados/success`, `fail/erros`, `fail/postmortem`
- `output_paths.resolve_success_out_path` maps any **relative** `--out` into `<pkg>/exercicios-gerados/success/<basename>`, discarding the caller's directory

PyPA's own packaging guidance is explicit that files inside the package directory should be read-only: installations are shared between users, may be mounted read-only, may be loaded from a zip, and may have multiple instances running in parallel. In a host deployment this produces permission errors (which then trigger Pitfall 2), artifacts that vanish on upgrade, and — if the host runs more than one instance — two processes appending to the same NDJSON file.

There is a subtler version too: the only lever a host has to redirect these is monkeypatching `collector.TOKEN_USAGE_DIR` and `reliability.POSTMORTEM_PATH`, both commented "Injectable for tests". A private test seam has quietly become the host's configuration API.

**How to avoid:**
- The service writes **no files**. It returns `ExerciseBatch`; the CLI adapter owns `--out`, and `resolve_success_out_path`'s relative-path rewriting stays a CLI behaviour (preserving the current CLI contract exactly).
- Token-usage NDJSON is the one artifact with a real reason to survive the service call. Proportionate options, cheapest first: (a) resolve `TOKEN_USAGE_DIR` from an env var with the current path as default — one `os.getenv`, consistent with env-as-config; (b) make flush a no-op when the directory is not writable, guarded per Pitfall 2. Do not build a storage abstraction.
- Postmortem JSONL is a debugging artifact; gate it on the same env var or drop it on the service path.

**Warning signs:**
- `PermissionError` with a path under the install directory.
- Generated JSON files appearing inside the host's dependency tree.
- Artifacts disappearing after a redeploy.
- Test: run the suite with `exercise-ai/` read-only; the service path must still succeed.

**Phase to address:** Embed boundary phase.

---

### Pitfall 9: The 1–40 cap lives in argparse, so the host and the demo can bypass it

**What goes wrong:**
`main._positive_quantidade` enforces `1 <= qty <= 40` (`main.py:97-109`), but `GenerationRequest.quantidade` only declares `gt=0` (`models.py:19`). A host — or the demo page — constructs `GenerationRequest` directly and can pass `quantidade=5000`.

The cost is not one oversized call. Downstream: the model cannot produce 5000 items, so `validate_exercise_batch` fails on the count mismatch (`validator.py:46-50`), which dumps the whole oversized batch to stderr (Pitfall 6), then `reliability` regenerates (default `max_retries=1`) and pays for a **second** oversized call, then writes a postmortem. One bad integer from the host becomes two maximal completions plus a log flood.

**Why it happens:**
Argparse validation is where a CLI naturally puts bounds, and it worked because argparse was the only door. The embed boundary opens a second door that bypasses it.

**How to avoid:**
Move the bound into `GenerationRequest` (`Field(..., ge=1, le=40)`) so the domain object enforces it wherever it is constructed.

**Regression trap — this is the part that is easy to get wrong.** Do *not* delete `_positive_quantidade` in the process. The milestone requires "CLI e wizard seguem idênticos". Argparse type errors exit with status **2** and argparse's own message; a Pydantic `ValidationError` would surface at a different point, with English Pydantic prose, and would fall into `run()`'s handlers with exit status 1. Keep both: argparse for the CLI's message and exit code, the model bound as the backstop for every other caller.

**Warning signs:**
- A `[USAGE]` event with an unusually large `prompt_tokens`/`completion_tokens` followed by a validation error mentioning `quantidade incorreta`.
- Test: `GenerationRequest(quantidade=41)` must raise; and `main.py --quantidade 41` must still exit 2 with the existing PT message.

**Phase to address:** Embed boundary phase. Already a v2.0 target (`bound 1–40 no domínio`); the regression trap is the part worth writing into the plan.

---

### Pitfall 10: The error contract is Portuguese prose, so the host must string-match to branch

**What goes wrong:**
Today a caller can only distinguish failures by parsing message text. `ValueError` is raised for missing API keys (`main.py:83`, `generator.py:50`, `generator_gemini.py:81`), for invalid `RELY_MAX_RETRIES` (`reliability.py:46`), for an unknown secondary provider (`failover.py:47`), and for every validation failure (`validator.py:66`). `RuntimeError` covers both retriable invalid responses and permanent API errors, distinguished only by ad-hoc attributes (`retriable`, `api_error_kind`) attached at construction and never documented as public.

So a host wanting to retry on rate-limit but alert on a bad API key has to match on `"Limite de requisições"` versus `"Chave ausente"`. Every message becomes frozen API. Changing `"o máximo 40 exercícios é permitido"` to fix its grammar silently breaks the host.

This is well-trodden ground: the general rule across library error-design guidance is that exception **class** and a stable **code** are contract, while message text is human-readable and explicitly not contract.

**Why it happens:**
The PT messages were designed for a human reading a terminal, and they are good at that. Nobody was branching on them because the only consumer was a person.

**How to avoid:**
The milestone already names the fix (`kind` nos `ValueError` de config). Make it uniform and minimal — no exception hierarchy, no error registry:
- Attach a `kind` attribute with a small closed set of ASCII strings (`config_missing_key`, `config_invalid`, `validation_failed`, `validation_exhausted`, plus the existing `api_error_kind` values `auth`/`rate_limit`/`timeout`/`connection`/`generic`/`refusal`).
- Keep the PT message as the human string; document explicitly that **text is not contract, `kind` is**.
- List the `kind` values in the host integration doc, with the note that unknown values may be added and should hit the caller's default branch.
- The existing `retriable` / `api_error_kind` attributes become documented rather than incidental.

**Warning signs:**
- Host code containing `"Chave ausente" in str(e)` or similar.
- A message-wording change breaking a host test.
- Test: assert every raise site reachable from the service sets `kind`, and that the set of observed values is a subset of the documented set.

**Phase to address:** Embed boundary phase.

---

### Pitfall 11: Redaction that matches live env values stops matching the moment config arrives from elsewhere

**What goes wrong:**
`generator._redact_env_secrets` and `generator_gemini._redact_env_secrets` scrub debug previews by reading `os.getenv(name)` and doing a literal `text.replace(val, "[REDACTED]")` (`generator.py:73-79`, `generator_gemini.py:102-108`). This is correct only while three things hold: the key is in the environment, it is byte-identical in the text, and the text passes through that function.

All three can break at the embed boundary:
- **Not in env.** If a host ever supplies a key by any route other than `os.environ` — set on a client, passed as a parameter, injected by a secrets manager after import — `os.getenv` returns empty, the loop skips, and the preview prints in full. The redactor fails **open** and silently.
- **Not byte-identical.** Exact-value matching is well documented as fragile: base64, URL-encoding, JSON/Unicode escaping, whitespace reformatting, truncation or splitting across fields all defeat it. A provider error body echoing an `Authorization: Bearer <key>` header is a realistic vector.
- **Doesn't pass through.** The redactor covers exactly two sites: the Gemini unparseable-response preview and the OpenAI refusal string. It does not cover exception tracebacks, SDK exception `__str__`, or `validator`'s full-batch dump.

**Constraint check:** env-as-config is what makes the *current* redactor work at all. That is fine while it holds — the honest statement for the host team is: "redaction assumes keys live in `os.environ`; if you inject credentials another way, redaction is void." That sentence is the deliverable, and it costs nothing.

**How to avoid:**
Keep the existing redactor (it is cheap and it works for the env case) and add two proportionate layers:
- **Prefix-based scrubbing as a backstop** — a small regex for known provider key shapes (`sk-`, `AIza`, `xai-`) so a value that never came from env still gets caught. ~5 lines, catches the fail-open case.
- **Shrink what gets previewed.** The codebase already gets this right for API errors: `_gemini_error_detail` and `_openai_error_detail` log only exception type and status code, explicitly never `str(exc)`. Extend the same allowlist discipline to the response previews and the validator dump (Pitfall 6). What is never printed cannot be un-redacted.
- Add a canary test: put a fake key of realistic shape in a response preview and assert it does not reach the captured stream.

**Warning signs:**
- A `[API:*] unparseable response:` line in host logs whose payload looks like a credential.
- Redaction tests that only ever exercise the env-populated path.
- Any new print of a provider payload added without going through the redactor.

**Phase to address:** Embed boundary phase. The demo phase must additionally never render raw stderr into the page — see Pitfall 15.

---

### Pitfall 12: Single-threaded `http.server` blocks for the whole LLM call, and the operator's reflex doubles the bill

**What goes wrong:**
`HTTPServer` is `socketserver.TCPServer`, which handles exactly one request at a time. A generation takes seconds to minutes. During that window the server accepts nothing — including the page's own favicon or CSS request. `BaseHTTPRequestHandler` also defaults to `HTTP/1.0` with `close_connection = True`, so there is no keep-alive to soften it.

The demo-day failure is behavioural, not technical: the page appears frozen with the host team watching, the operator presses refresh or opens a second tab, and now there are two queued generations spending real credits — and the second one will corrupt the first's telemetry, because `begin_run()` clears the shared collector buffer (Pitfall 16).

There is also a latency amplifier the host cannot see. One service call is not one provider call: `generator_gemini` walks up to five models in `GEMINI_MODEL_FALLBACKS` on capacity errors, `reliability` adds up to `max_retries` regenerations, and `failover` adds one hop to the peer. A single call can issue on the order of seven provider requests. The OpenAI and Grok clients set `timeout=30.0` (`generator.py:58`, `:69`) but **`genai.Client` is constructed with no timeout** (`generator_gemini.py:82`), so the Gemini leg has no client-side wall-clock bound at all. One hung Gemini call pins the single-threaded demo server indefinitely.

**How to avoid — respecting the sequential contract:**
The naive fix (`ThreadingHTTPServer`) conflicts with "one generation at a time": two concurrent handlers would race on the module-level collector and on `os.environ["LLM_PROVIDER"]`, breaking the Pitfall 4 mitigation. Do all four of these instead — together they are maybe 20 lines of stdlib:

1. **`ThreadingHTTPServer`** so asset and status requests are never blocked by a generation. One-word change, stdlib, zero deps.
2. **A module-level `threading.Lock` around the generate call**, using `acquire(blocking=False)` and returning **HTTP 409** with a PT message when it is already held. This *enforces* the sequential contract rather than assuming it, and makes the second tab a clean rejection instead of a second charge.
3. **Inline the CSS and JS** into the single HTML response, so there are no asset round-trips to queue in the first place.
4. **Disable the submit button on submit** and show a "Gerando…" state, so the operator's reflex never fires.

Optionally pass a `timeout` to `genai.Client` — that one belongs to the embed boundary phase, not the demo.

**Warning signs:**
- Browser spinner with no server log line for many seconds.
- Two `[USAGE]` runs with overlapping timestamps.
- A generation the page never rendered but the NDJSON recorded.

**Phase to address:** Demo phase (items 1–4). The missing Gemini client timeout is an embed boundary phase fix.

---

### Pitfall 13: Binding scope — `::1` needs an explicit address family, and the natural "fix" exposes the machine

**What goes wrong:**
`HTTPServer.address_family` defaults to `AF_INET`. Passing `("::1", 8642)` to a default `HTTPServer` fails; you must subclass and set `address_family = socket.AF_INET6`. The failure mode is that whoever hits this at 9pm before the demo makes it work by binding `("", 8642)` or `("::", 8642)` — and goes from loopback-only to **every interface on a Windows laptop**, possibly on a corporate LAN or café Wi-Fi, running with the operator's real API keys.

Two Windows specifics make this worse:

- **A `::1` bind serves IPv6 loopback only.** `127.0.0.1` and `::1` are distinct addresses, and setting `IPV6_V6ONLY=0` does *not* make a `::1`-bound socket accept IPv4 — only binding the wildcard `::` does, and that also exposes every interface. So a browser or proxy that resolves `localhost` to IPv4 first gets connection refused. That is the exact frustration that leads to the broad bind. Prevention: never write `localhost` anywhere; print and link the literal `http://[::1]:8642/`.
- **Windows loopback traffic does not traverse the Windows Firewall**, so binding `::1` produces **no firewall prompt**. That is normally reassuring, but it also removes the one signal operators rely on. The corollary is the useful one: **if you see the "Allow access?" dialog, you have bound too broadly.** Treat that prompt as an alarm, not a nuisance.

**How to avoid:**
- Subclass once: `class DemoServer(ThreadingHTTPServer): address_family = socket.AF_INET6`, bind `("::1", 8642)`.
- **Refuse to start unless the bound address is a loopback address.** Four lines against `ipaddress.ip_address(host).is_loopback`. This is the single highest-leverage control in the demo, because it also doubles as the anti-accretion tripwire (Pitfall 17) — the first step of "let's put this on a server" fails loudly instead of succeeding quietly.
- Print the exact URL on startup, with the brackets.

**Warning signs:**
- `netstat -ano | findstr 8642` shows `[::]:8642` or `0.0.0.0:8642` instead of `[::1]:8642`. This is the one-command check; put it in the demo README.
- A Windows Firewall prompt appears.
- Anyone reaches the page from another machine.

**Phase to address:** Demo phase.

---

### Pitfall 14: A loopback bind is not an authorisation boundary — any page the operator visits can spend credits

**What goes wrong:**
Binding `::1` stops other machines. It does **not** stop the operator's own browser. Any website open in another tab can issue a cross-origin `POST http://[::1]:8642/gerar`; with `Content-Type: text/plain` or a form encoding it is a CORS-simple request, so there is **no preflight to block it** and the request reaches the handler. The attacker cannot read the response under the same-origin policy — but they do not need to. The generation already ran and already cost money. DNS rebinding can additionally make the response readable; rebinding to `::1` is harder than to `127.0.0.1`, but Host-header validation costs three lines regardless.

This is not theoretical for AI tooling specifically: published advisories against local AI dev servers describe exactly this stack — loopback/broad bind, no `Host` validation, no auth — with impact explicitly including *consuming paid LLM quota* and disclosing prompt/response traces.

**How to avoid — proportionate to one operator, one afternoon, real keys:**
Three checks and one cap, all stdlib, all in the request handler:

1. **Host allowlist.** Reject unless the `Host` header is exactly `[::1]:8642`. Defeats DNS rebinding.
2. **Origin check.** If an `Origin` header is present and is not the demo's own origin, reject with 403. (Absent `Origin` is fine — that is a direct navigation.)
3. **Require `Content-Type: application/json`** on the generate route, else 415. This is the one that actually blocks the cross-site POST, because it forces a preflight that a foreign origin cannot pass.
4. **A hard generation budget.** A process-level counter that refuses further generations after N (say 25) with a PT message. This bounds the money risk absolutely, in about five lines, and needs no rate-limiting library. Combined with the 1–40 quantity bound from Pitfall 9, the worst case becomes arithmetic instead of open-ended.

Skip bearer tokens, sessions and real rate limiting — disproportionate for a throwaway single-operator demo, and the four items above already close the realistic paths.

**Warning signs:**
- Token-usage NDJSON shows generations the operator did not initiate.
- Server log shows a request whose `Origin` is not the demo.
- Request count in the `[USAGE]` summary exceeds what was demonstrated.

**Phase to address:** Demo phase.

---

### Pitfall 15: The demo renders diagnostics to make the contract visible, and ships generated content or config to the screen

**What goes wrong:**
The whole point of the demo is to show the host team "the JSON your system will consume". The tempting shortcut is to capture the generator's stderr and render it in a `<pre>` for transparency. That stream carries the full validation batch dump, `[API:*]` previews, `[USAGE]` lines, provider and model names, and — per Pitfall 11 — anything the value-matching redactor missed. A second variant is adding a "diagnostics" panel showing which env vars are set, which is one careless change away from showing their values.

The demo is being presented on a screen, possibly screen-shared or screenshotted, running with production keys.

**How to avoid:**
- Render exactly two things: the human-readable exercises, and `ExerciseBatch.model_dump()` — the actual contract object. That is a *better* demo of the integration contract than a log dump anyway.
- On failure, render the PT message and the `kind` from Pitfall 10. Nothing else.
- Never pipe the generator's stderr to the browser. If diagnostics are wanted, leave them in the operator's terminal.
- No env-var panel.

**Warning signs:**
- Any `[` tag string visible in the page.
- Page content that grows with `--max-retries`.
- A demo template containing `os.environ` or `getenv`.

**Phase to address:** Demo phase, with the redaction hardening from Pitfall 11 in the embed boundary phase.

---

### Pitfall 16: The module-level collector loses telemetry when a call path skips `flush()`

**What goes wrong:**
`collector._collector` is a module-level singleton (`collector.py:125`). `begin_run()` calls `self.events.clear()` (`:50`) and `flush()` clears after writing (`:122`). Because modules are cached in `sys.modules`, this buffer is shared by every call in the host process for the process's whole life.

In the CLI the design is airtight: `run()` calls `begin_run()` at the start and `flush_token_usage()` in a `finally`, and the docstring correctly notes that `SystemExit` still runs `finally`. The embed boundary is where it can break — if `service.py` is written without the matching `begin_run`/`flush` pair, or if an exception escapes before the `finally` is installed, the events sit in the buffer until the *next* call's `begin_run()` silently discards them. Billing data for a failed run — the run you most want to account for — disappears.

There is also a genuine cross-call hazard if the sequential contract is ever violated (see Pitfall 12): two overlapping generations share one buffer and one `run_id`.

**How to avoid:**
Keep the singleton — replacing it with a passed context object is exactly the kind of refactor YAGNI says to skip for a sequential, single-call-at-a-time contract. Instead make the pairing structural: one `contextlib.contextmanager` that does `begin_run()` on entry and `flush()` in its `finally` (guarded per Pitfall 2), used by both `service.py` and `run()`. That makes it impossible to have one without the other and keeps the single-flush-site invariant (D-04).

**Warning signs:**
- A `run_id` in the NDJSON with fewer events than the run made provider calls.
- Two `[USAGE] resumo` blocks with no intervening generation.
- Test: call the service twice in one process, force a failure on the first, assert both runs produced NDJSON records with distinct `run_id`s.

**Phase to address:** Embed boundary phase.

---

### Pitfall 17: The throwaway demo quietly becomes a production HTTP surface

**What goes wrong:**
This is the pitfall that is invisible at the moment it occurs. The demo is explicitly throwaway — stdlib only, outside the package, outside CI. Then it works, the host team likes it, and someone asks "can we just point staging at it for a week?" The accretion path is always the same: a second endpoint, a `requirements.txt`, a bind address change, an NSSM/systemd wrapper, a CI job "just to check it still builds". At no point does anyone decide to productionise it; it simply never gets deleted. Now an `http.server` — which CPython's own documentation warns is not recommended for production and implements only basic security checks — is serving traffic with the operator's personal API keys.

**How to avoid — three cheap, structural tripwires:**
1. **The loopback assertion from Pitfall 13 is the main control.** A demo that refuses to bind a non-loopback address cannot be deployed without someone deliberately deleting the check. That deletion is a visible, reviewable act — which is exactly the property you want.
2. **A loud PT startup banner**: throwaway, not for production, real credits being spent, keys from the operator's `.env`.
3. **`demo/README.md` with an explicit expiry** — the milestone it belongs to and the instruction to delete it at milestone close. Add "delete `demo/`" to the milestone completion checklist so it is an actual gate, not a hope.

The locked constraints (outside the package, outside CI, zero dependencies) are already the strongest anti-accretion controls available, because each one makes the demo actively inconvenient to deploy. They should be treated as load-bearing, not incidental.

**Warning signs:**
- A dependency file, lockfile or Dockerfile appears in `demo/`.
- The demo gains a second route, or any persistence.
- Anyone asks for the bind address to change, or for it to run unattended.
- A CI job references `demo/`.

**Phase to address:** Demo phase, with the deletion gate recorded at milestone close.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Keep flat modules with generic names on the host's `sys.path` | No packaging work while the host stack is unknown | `models`/`main`/`validator`/`token_usage` collide with host modules; failure direction depends on import order and can differ between the host's dev box and production | Accepted **this milestone only**, and only with the collision self-check and a published reserved-name list. Revisit as the first item once the host stack is known |
| `service.py` re-exports `main`'s helpers instead of owning the pipeline | Smallest diff, CLI regression risk near zero | `service` keeps `main`'s import-time `load_dotenv` + `sys.path` mutation and its `sys.exit` paths — i.e. the milestone's headline requirement is not actually met | Never. The direction of dependency must be `main → service`, not `service → main` |
| Leave `os.environ` writes unrestored because "it's sequential anyway" | Zero work | Provider silently repins for the host process's whole life; unrecoverable without a restart; invisible in logs | Never — the fix is ~10 lines and it is already a stated v2.0 target |
| Monkeypatch `collector.TOKEN_USAGE_DIR` / `reliability.POSTMORTEM_PATH` as the host's config mechanism | Works today, no new surface | A private test seam becomes undocumented public API; any rename breaks the host silently | Only for tests. For the host, read the directory from env (consistent with env-as-config) |
| Move the 1–40 bound to Pydantic and delete `_positive_quantidade` | One bound instead of two | CLI exit code changes 2→1 and the PT message becomes English Pydantic prose — breaks "regressão zero" | Never. Keep both; they serve different callers |
| Keep `logger.propagate = False` in the library | Diagnostics always visible to the operator | Host's structured logging is bypassed entirely; generator events never reach the host's aggregator | Only in the CLI adapter's `_configure_logging`, never on the library import path |
| Render the generator's stderr in the demo page | Instant "look, full transparency" | Full generated batches, `[API:*]` previews and possibly unredacted values on a shared screen | Never. Render `model_dump()` — it demonstrates the contract better anyway |
| Drop `ThreadingHTTPServer`, keep it single-threaded for simplicity | One less concept | Page appears frozen for minutes during the demo; operator double-submits; double spend | Acceptable **only** if CSS/JS are inlined so there are no asset requests *and* the submit button self-disables. Otherwise take the one-word change plus the lock |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Host process (long-lived) | Assuming `except Exception` around the call is sufficient | `SystemExit` is `BaseException`; the service must never raise it. Verify with an explicit `except Exception` guard in a test |
| Host process env | Letting the library write `LLM_PROVIDER` / `LLM_REASONING_EFFORT` permanently | Scope every library-side env write with a snapshot/restore context manager that also restores *absence* |
| Host logging | `propagate = False` plus a hard-coded `StreamHandler` in the library | `logging.NullHandler()` in the library; handler/level/format configured only by the CLI adapter |
| Host filesystem | Writing NDJSON and JSON artifacts under `__file__` | Service writes nothing; the one artifact worth keeping (token NDJSON) gets its root from env, with a guarded no-op when unwritable |
| Host `sys.path` | `sys.path.insert(0, ...)` at import time of a library module | Single guarded bootstrap in the boundary module + a `__file__`-provenance self-check that names the colliding path |
| `.env` / python-dotenv | Calling `load_dotenv` at import time of a library module | Only `__main__` entry points load `.env` (CLI, demo runner). `load_dotenv` defaults to `override=False`, so host env correctly wins — but the injection into the host's global env is still real |
| Google Gemini SDK | `genai.Client(api_key=...)` with no `timeout`, unlike the OpenAI/Grok clients which set `timeout=30.0` | Pass an explicit timeout so the Gemini leg has the same wall-clock bound; otherwise one hung call pins the caller's thread indefinitely |
| Gemini model fallback list | Assuming one service call is one provider call | Up to five model attempts, times bounded regeneration, plus one failover hop. Surface the attempt count to the caller, or at minimum document it |
| OpenAI SDK | `client.beta.chat.completions.parse` is a beta-namespaced surface | Pin the SDK version for the host and note the namespace in the integration doc; a host upgrading `openai` independently can break parsing |
| Windows console / redirected streams | Assuming UTF-8 | `locale.getpreferredencoding()` is `cp1252` on this machine; `→`, `√`, `π`, `≠` all fail to encode. Keep runtime strings ASCII; use `errors="replace"` on diagnostic streams |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Single-threaded `http.server` during a multi-second LLM call | Page and its own assets hang; browser spinner with no log activity | `ThreadingHTTPServer` + inline CSS/JS + a non-blocking lock returning 409 | The first time a second tab or a favicon request exists — i.e. immediately, on any real browser |
| Unbounded `quantidade` from the host or demo | One maximal completion, guaranteed count-mismatch, then a paid regeneration | `ge=1, le=40` on `GenerationRequest` (keep argparse's check too) | Any value above ~40; cost and latency scale linearly, failure becomes certain |
| Provider-call amplification inside one service call | Wall-clock minutes; several `status=attempt` rows sharing one `run_id` | Surface attempt count in the returned result or logs; consider a wall-clock budget at the boundary | Whenever Gemini returns capacity errors — the five-model walk runs before failover even engages |
| Gemini client with no timeout | Host thread pinned indefinitely; single-threaded demo dead until killed | Pass `timeout` to `genai.Client`, matching the 30s used for OpenAI/Grok | Any provider hang; no scale threshold — it is a single-request failure |
| Full-batch stderr dump on validation failure | Host log volume spikes on exactly the runs that already went wrong | Bounded summary at INFO; full batch at DEBUG | `quantidade` above ~10 with retries enabled |
| Collector buffer growing across a call that never flushes | Memory creep in a long-lived host; telemetry silently discarded at the next `begin_run()` | `begin_run`/`flush` paired in one context manager | Any failure path that bypasses the `finally` |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Redaction that only matches live `os.getenv` values | Fails **open** and silently if a key ever arrives from a non-env source, or is encoded/reformatted in the payload | Keep it, add a provider-key-prefix regex backstop, and state plainly in the host doc that redaction assumes env-sourced keys |
| Printing generated content and provider payloads to the host's stderr | Unbounded model output — and anything the redactor missed — in the host's log index | Allowlist what gets logged: type + status code, as `_gemini_error_detail` already does. Bounded summary instead of the full batch |
| `.env` values injected into the host's global process environment at import | Keys visible to every other component, crash reporter and spawned subprocess in that process | Only `__main__` entry points call `load_dotenv` |
| Loopback bind treated as authorisation | Any page the operator visits can POST and spend real credits; no preflight blocks a simple cross-site request | `Host` allowlist + `Origin` check + require `Content-Type: application/json` on the generate route |
| Broad bind to get IPv4 `localhost` working | Demo reachable from the LAN with the operator's real keys | Subclass with `AF_INET6`, bind `::1`, link the literal `http://[::1]:8642/`, and refuse to start on a non-loopback address |
| No spend ceiling on a page anyone reachable can submit | Unbounded API cost from a loop or a stuck submit | Process-level generation counter (~25) plus the 1–40 quantity bound; together the worst case is arithmetic |
| Rendering diagnostics in the demo page for transparency | Batches, provider details, possibly credentials on a screen-shared display | Render only the exercises and `model_dump()`; PT message + `kind` on failure |
| Artifacts written into the install directory | Generated content persisting inside the host's dependency tree, surviving redeploys, shared across instances | Service writes no files; telemetry root from env |
| Windows firewall silence on loopback | The usual "you are exposed" signal never fires for `::1` | Invert it: treat any firewall prompt as evidence of a too-broad bind. Verify with `netstat -ano | findstr 8642` |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Demo gives no feedback during a multi-second generation | Operator and host team believe it is broken; operator refreshes and double-spends | Disable submit on click, show "Gerando…", inline assets so nothing else can queue |
| Second submission queues silently instead of being rejected | Two charges, corrupted telemetry, confusing double render | Non-blocking lock → HTTP 409 with a clear PT message |
| Host receives only Portuguese prose to branch on | Host writes brittle substring matches; a wording fix breaks production | `kind` attribute as the machine contract; PT text stays for humans and is documented as non-contractual |
| CLI error text or exit code changes during the refactor | Existing scripts and the wizard break — violates "regressão zero" | Keep `_positive_quantidade` and every argparse message byte-identical; snapshot-test stdout/stderr and exit codes for the CLI before and after |
| Demo linked as `http://localhost:8642/` | Connection refused when the resolver prefers IPv4, then someone "fixes" it with a broad bind | Print and link the literal `http://[::1]:8642/` everywhere |
| Generator diagnostics vanish for the host after the refactor | Host loses the `[USAGE]` / `[FAILOVER]` observability v1.2 delivered | Route them through the `exercise_ai` logger so the host can opt in, rather than deleting them or forcing them to stderr |

## "Looks Done But Isn't" Checklist

- [ ] **No process exit:** `rg "sys\.exit|SystemExit" ` returns nothing in any module reachable from `service.py` — verify with a test using `except Exception`, not `pytest.raises(Exception)`
- [ ] **No output:** service runs under `redirect_stdout` + `redirect_stderr` and both captures are empty on the success path
- [ ] **No files:** run the suite with `exercise-ai/` read-only; the service success path still passes and no error *type* changes
- [ ] **Env restored:** call twice with a forced failover between; `os.environ` is byte-identical before and after, including keys that were originally unset
- [ ] **Errors typed:** every raise site reachable from the service sets `kind`; the observed set matches the documented set
- [ ] **Bound in the domain:** `GenerationRequest(quantidade=41)` raises **and** `main.py --quantidade 41` still exits 2 with the existing PT message
- [ ] **CLI unchanged:** stdout, stderr and exit codes snapshot-compared against pre-refactor for success, config-error, validation-exhaustion and failover paths; wizard flow unchanged
- [ ] **Telemetry paired:** two calls in one process with a failure on the first produce two NDJSON records with distinct `run_id`s
- [ ] **No collision:** after importing the service, `models.__file__` and `main.__file__` resolve under `exercise-ai/`; the self-check fires when they do not
- [ ] **Encoding safe:** no runtime `print`/log format string in `exercise-ai/` contains a non-Latin-1 character; a batch containing `√` round-trips with stdout redirected on Windows
- [ ] **`.env` ownership explicit:** importing the service in a clean-env subprocess does **not** populate `os.environ` from `.env`
- [ ] **Demo bound narrowly:** `netstat -ano | findstr 8642` shows `[::1]:8642`; no Windows Firewall prompt ever appeared
- [ ] **Demo rejects foreign callers:** a `curl` with a forged `Host` and one with a foreign `Origin` both return 403; a `text/plain` POST returns 415
- [ ] **Demo is bounded:** generation counter enforced; the demo refuses to start on a non-loopback address
- [ ] **Demo shows the contract, not the logs:** page contains `model_dump()` output and zero `[` diagnostic tags
- [ ] **Demo has an expiry:** `demo/README.md` states the milestone and "delete at close"; the deletion is on the milestone checklist
- [ ] **Runtime sanity:** the Python the demo actually runs under is the version the project targets — the operator's `python` on PATH is 3.14 while the project declares 3.11+

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| `sys.exit` reached the host and killed the process | LOW | Host restarts; move the exit into the CLI adapter and add the `except Exception` regression test. No data loss — nothing had been written |
| `finally`/`except` write masked the real error | LOW | Guard both sites with `except OSError`; re-run to recover the true error from the reproduced failure |
| Provider silently repinned by an unrestored env write | LOW technically, MEDIUM in trust | Restart the host to clear `os.environ`; add the scoping context manager. Audit the NDJSON to work out how long the wrong provider was serving and what it cost |
| cp1252 crash reported a successful generation as a failure | MEDIUM | Tokens are already spent and no JSON was written. Cross-reference `[USAGE]` `status=success` events against host-recorded failures to find affected runs; re-run only the ones that matter |
| Module-name collision in the host | HIGH | No in-place fix while packaging is parked. Short term: control import order or vendor into a host-owned subdirectory. Real fix: unpark packaging and rename to `exercise_ai/` — which is why this should lead the next milestone |
| Generated content or a credential reached host logs | HIGH | Rotate the affected API key immediately — redaction failures are not recoverable by deleting log lines. Purge the log index, then reduce what is printed rather than improving the redactor alone |
| Demo reachable beyond loopback | LOW if caught fast, HIGH if keys were used | Kill the process; check the NDJSON for generations the operator did not initiate; rotate keys if anything is unexplained; re-bind to `::1` with the loopback assertion |
| Demo accreted into production | HIGH | Do not harden it — `http.server` is documented as unsuitable for production. Delete it and scope a real HTTP surface as its own milestone with its own threat model |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| 1. `sys.exit` escapes to the host | Embed boundary | Test wrapping the service in `except Exception` catches every failure mode; no `sys.exit` in the service's import graph |
| 2. `finally`/`except` writes mask the real error | Embed boundary | Suite passes with the package directory read-only; error *types* unchanged |
| 3. Windows cp1252 vs LLM math Unicode | Embed boundary (demo surfaces it) | Batch containing `√` round-trips with stdout redirected; no non-Latin-1 chars in runtime strings |
| 4. `LLM_PROVIDER` never restored | Embed boundary | `os.environ` byte-identical across a call that failed over |
| 5. Flat generic module names | **Detection only** in embed boundary; prevention deferred to the parked packaging milestone | Self-check fires on a synthetic shadowing `models.py`; reserved-name list published to the host team |
| 6. Library writes to host stdout/stderr | Embed boundary | Service produces empty stdout and stderr on success; `NullHandler` present; no `propagate = False` on the library path |
| 7. Import-time `load_dotenv` / `sys.path` | Embed boundary | Clean-env subprocess import leaves `os.environ` unpopulated; documented who loads `.env` |
| 8. Artifacts inside the package directory | Embed boundary | Service writes no files; telemetry root overridable via env |
| 9. `quantidade` cap only in argparse | Embed boundary | Model rejects 41; CLI still exits 2 with the identical PT message |
| 10. PT prose as the error contract | Embed boundary | Every service-reachable raise sets `kind`; documented closed set |
| 11. Redaction assumes env-sourced keys | Embed boundary | Canary key of realistic shape never reaches a captured stream; prefix backstop covered by test |
| 12. Blocking single-threaded demo server | Demo (Gemini timeout → embed boundary) | Second concurrent submit returns 409; page assets load during a generation |
| 13. Binding scope / accidental exposure | Demo | `netstat` shows `[::1]:8642`; server refuses a non-loopback bind |
| 14. No Host/Origin/CSRF guard on the demo | Demo | Forged `Host` → 403; foreign `Origin` → 403; `text/plain` POST → 415 |
| 15. Demo renders diagnostics | Demo | Page contains `model_dump()` and no `[` diagnostic tags |
| 16. Collector singleton loses telemetry | Embed boundary | Two calls, first failing, produce two NDJSON records with distinct `run_id`s |
| 17. Demo accretes into production | Demo + milestone close | Loopback assertion present; `demo/README.md` expiry; deletion on the completion checklist |

**Suggested phase split for the roadmapper.** Pitfalls 1, 2, 4, 6, 7, 8, 10 and 16 are one coherent piece of work — they are all "stop behaving like a process, start behaving like a function" — and they should land together, because fixing any one of them in isolation leaves the boundary still unsafe to call. Pitfalls 3, 9 and 11 are independent hardening and can be sequenced separately, though 3 should precede the demo. Pitfall 5 is detection-and-documentation only and should be explicitly recorded as deferred rather than quietly closed. All of the demo pitfalls (12–15, 17) depend on the boundary existing first, so the demo phase must follow the embed boundary phase — and the demo is also the natural acceptance test for whether the boundary actually works.

## Sources

Confidence reflects the GSD `classify-confidence` seam: first-hand verification against this repository is HIGH; curated docs and cross-checked web sources are MEDIUM. External providers do not reach HIGH.

**HIGH — verified first-hand on the operator's Windows machine, against the real project modules**
- Direct reading of `main.py`, `generator.py`, `generator_gemini.py`, `validator.py`, `reliability.py`, `failover.py`, `models.py`, `output_paths.py`, `math_check.py`, `wizard.py`, `token_usage/collector.py`, `tests/conftest.py`
- Executed probes confirming: `locale.getpreferredencoding(False)` is `cp1252` on this machine; `→ √ π ≠` fail to encode in cp1252 (and `…` additionally fails in cp850/cp437); `main.format_batch_text` on a real batch raises `UnicodeEncodeError` against a cp1252 stream; `validator._log_validation_failure` does the same and `UnicodeEncodeError` **is** a `ValueError` subclass (so `reliability` misreads it as a retriable validation failure); the `[FAILOVER]` arrow raises; an exception raised in `finally` discards the in-flight `SystemExit`; `SystemExit` passes through an enclosing `except Exception`

**MEDIUM — curated documentation (Context7, `/python/cpython/v3.11.14`, `/theskumar/python-dotenv/v1.2.1`)**
- CPython `http.server` docs: explicit "not recommended for production / only basic security checks" warning; `ThreadingHTTPServer` as a minimal `daemon_threads = True` subclass with no added thread safety; `BaseHTTPRequestHandler` defaulting to HTTP/1.0 with no keep-alive; `StreamRequestHandler.timeout`
- CPython import reference: `sys.path` first-match-wins resolution; module registered in `sys.modules` before `exec_module` and deleted on failure; the documented "user file shadowing a stdlib module" symptom
- python-dotenv: `load_dotenv` writes to `os.environ` and defaults to `override=False`; `dotenv_values` as the non-mutating alternative

**MEDIUM — cross-checked web sources**
- `sys.exit` in reusable code kills the importing application; reserve it for `__main__` — <https://docs.python.org/3/library/sys.html>, <https://runebook.dev/en/docs/python/tutorial/stdlib/error-output-redirection-and-program-termination>, plus the `StreamParser` pattern at <https://github.com/Ball-Lang/ball/blob/main/python/cli/ball_cli/argparse_util.py>
- Module-level mutable state as a process-wide singleton via `sys.modules`; pass per-call context, expose explicit reset — <https://github.com/jlevy/repren/issues/43>, <https://lucumr.pocoo.org/2009/7/24/singletons-and-their-problems-in-python/>, <https://thinkinginpython.com/24_Singleton.html>
- `os.environ` as a process-wide cache written back to the real environment; long-lived applications should not use it for per-invocation config — <https://modwsgi.readthedocs.io/en/develop/user-guides/application-issues.html>, <https://bugs.python.org/issue7250>, <https://discuss.python.org/t/bikeshedding-a-method-to-refresh-os-environ/57628>
- Exact-value redaction defeated by encoding, reformatting and field-splitting; tracebacks and non-string objects bypass redactors; redact at the final sink and test with canaries — <https://gitdash.dev/blog/github-actions-secret-redaction-leaks>, <https://dev.to/sergey_shinder_ab2d943365/the-secret-was-masked-until-we-base64-encoded-it-31h4>, <https://www.devtoolsdaily.com/blog/redact-production-logs-before-sharing/>
- Package directories should be treated as read-only (shared installs, read-only mounts, zip imports, parallel instances) — <https://setuptools.pypa.io/en/latest/userguide/datafiles.html>, <https://docs.python.org/3/library/importlib.resources.html>
- Local AI dev servers: loopback is not authorisation; `Host` allowlist, `Origin` check and a JSON content-type requirement as the cheap defences; impact explicitly includes consuming paid LLM quota — <https://github.com/genkit-ai/genkit/issues/5581>, <https://github.blog/security/application-security/localhost-dangers-cors-and-dns-rebinding/>, <https://github.com/agentage/cli/commit/f24b61972d1ef7dc34bca4c658a5b95971497af0>
- `::1` and `127.0.0.1` are distinct; `IPV6_V6ONLY=0` only gives dual-stack when bound to the `::` wildcard; Windows loopback traffic bypasses the firewall so no prompt appears — <https://learn.microsoft.com/en-us/windows/win32/winsock/dual-stack-sockets>, <https://stackoverflow.com/questions/37729475/create-dual-stack-socket-on-all-loopback-interfaces-on-windows>, <https://superuser.com/questions/1834601/windows-firewall-on-ws2016-doesnt-accept-ipv6-loopback-ip>
- Exception class and stable codes are contract; message text is not — <https://softwareengineering.stackexchange.com/questions/434314/is-changing-the-exception-a-method-throws-a-breaking-change-for-a-library>, <https://github.com/prisma/prisma/blob/main/docs/Error%20Handling.md>

---
*Pitfalls research for: embedding an existing Python CLI generator as an in-process library, plus a throwaway stdlib demo page*
*Researched: 2026-09-16*
