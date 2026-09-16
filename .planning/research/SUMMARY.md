# Project Research Summary

**Project:** Gerador de Exercícios com IA
**Domain:** Embeddable in-process Python LLM exercise-generation library + throwaway stdlib demo
**Milestone:** v2.0 "Embed em Produção" (SEED-003 Slice A)
**Researched:** 2026-09-16
**Confidence:** HIGH

## Executive Summary

v2.0 turns a working CLI pipeline into an in-process library boundary. Experts build this as **library core + thin CLI adapter**: one callable that returns data and raises, with stdout, files, and `sys.exit` owned only by presentation adapters. The recommended approach adds **no new runtime dependency** — `service.py` as the seam, `main.run()` as the CLI adapter, domain bound 1–40, a machine-readable error `kind`, scoped `LLM_PROVIDER` restore, and a throwaway `demo/` page on `[::1]:8642` via stdlib `http.server`. Packaging / rename to `exercise_ai/` stays parked; Settings stays rejected.

The critical risks are process-level behaviour leaking into a long-lived host (`sys.exit`, unrestored env, package-dir writes, stderr dumps) and two demo-day killers already present on Windows: **cp1252 `UnicodeEncodeError` on math glyphs (`√`)** turning success into failure, and **Gemini with no client timeout** pinning the caller indefinitely. Mitigate both in Phase 11 before the demo. Concurrency stays out of scope — sequential only — enforced in the demo with `ThreadingHTTPServer` + Lock → HTTP 409 when busy.

**Sharp exit for the next milestone:** `sys.path.insert` embed is empirically broken (both import orders). Packaging / rename to `exercise_ai/` is **not** work for v2.0, but the first real host integration cannot succeed without unparking it.

## Key Findings

### Recommended Stack

For v2.0 the correct stack addition is **nothing**. Python 3.11 (CI pin), existing `openai` / `google-genai` / `pydantic` / `python-dotenv` / `pytest`, plus stdlib `http.server` (`ThreadingHTTPServer`), `socket.AF_INET6` for `::1`, `json`, and `functools.partial` for `directory=`. No FastAPI/Flask/Streamlit, no agent frameworks, no `pyproject.toml` this milestone.

**Core technologies:**
- **Python 3.11+** — already pinned; demo patterns need only 3.7+
- **stdlib `ThreadingHTTPServer` + `AF_INET6`** — zero-dep demo on `http://[::1]:8642/`; browsers pre-open sockets that stall bare `HTTPServer`
- **Existing SDKs unchanged** — Gemini needs an explicit finite timeout (`HttpOptions.timeout` ms); OpenAI/Grok already use `timeout=30.0`
- **Deferred: hatchling + `src/exercise_ai/`** — only viable host-embed packaging; inventory ready for the next milestone

Details: [STACK.md](STACK.md)

### Expected Features

Table stakes collapse into one extraction: `service.generate_batch(request) -> ExerciseBatch` with no `sys.exit`, no print/file on the library path, no import-time `load_dotenv` on `service`, domain 1–40, three-category errors (`kind`), `LLM_PROVIDER` restored, honest sequential contract, and a written JSON + error table. Demo: form mirroring CLI params, exercises + raw contract JSON, "Gerando…" state, honest error-by-category, stdlib server with CSRF/loopback guards.

**Must have (table stakes):**
- No process exit / no stream / no unrequested FS writes from the service path
- Error contract catchable without PT string-matching (`kind` on config `ValueError`s; subclasses of existing types OK)
- Domain bound 1–40; env restore; Gemini timeout + documented worst case
- Demo: form, dual panel, busy/error states, sequential enforcement

**Should have (competitive — next pass, not this signature):**
- Usage/cost + correlation id **returned alongside** the batch (lead differentiator of next embed-hardening)
- Per-call provider/reasoning overrides as kwargs (not Settings); dry-run mode if cheap

**Defer (later milestones):**
- Print→logging conversion (~33 sites) — known debt; host escape hatch is `redirect_stderr`
- Packaging / `exercise_ai/` rename — **lead item of NEXT milestone**
- Async/concurrency, Settings, HTTP product surface, SEED-003 images/storytelling

Details: [FEATURES.md](FEATURES.md)

### Architecture Approach

One new module (`service.py`), `run()` delegates, import rule `main → service → pipeline` (nothing below the seam imports `main`). Build order: pure move first (suite stays green), then env hygiene + error `kind` as siblings, then demo as acceptance test. Keep `generate_batch(...) -> ExerciseBatch` this milestone (locked signature / KISS).

**Major components:**
1. **`service.py`** — embed boundary: lifecycle, scoped env, return batch or raise
2. **`main.run()`** — CLI adapter: print, `--out`, fail logs, `sys.exit(1)`
3. **`demo/server.py`** — throwaway stdlib consumer outside package and CI

Details: [ARCHITECTURE.md](ARCHITECTURE.md)

### Critical Pitfalls

1. **`sys.exit` / `SystemExit` kills the host** — service raises; only adapter exits; test with `except Exception`
2. **cp1252 vs `√`/`→`** — success reported as failure; harden in Phase 11 before demo day
3. **`LLM_PROVIDER` never restored** — scoped context manager always (failover writes even when caller doesn't)
4. **Flat module name collision** — detection + reserved-name list only this milestone; prevention = packaging next
5. **Demo: broad bind / no CSRF / double-submit** — loopback assert, Host/Origin/JSON Content-Type, Lock→409

Details: [PITFALLS.md](PITFALLS.md)

## Cross-researcher resolutions (opinionated)

| Tension | Resolution | Why |
|---------|------------|-----|
| Print→logging (~33 sites) | **Defer** (Architecture). Host uses `redirect_stderr`. | KISS / YAGNI; high regression risk vs tests that assert stderr. **Known debt for a later milestone.** |
| Demo server concurrency | **`ThreadingHTTPServer` + `Lock`; busy → HTTP 409** | Browsers stall on bare `HTTPServer`; lock *demonstrates* sequential contract instead of assuming it. |
| `generate_batch` return type | **Keep `-> ExerciseBatch`** | Locked signature / KISS. **"Usage returned alongside the batch" is the lead differentiator of the next embed-hardening pass** — do not widen now. |
| Packaging | **Stay parked** | Do not unpark into v2.0. Record as **lead item of NEXT milestone** with sharp exit: first real host integration cannot succeed without `exercise_ai/` packaging. |
| Encoding (cp1252 / `√`) | **In-scope Phase 11** (precondition or early hardening) | Already fails on this machine; demo cannot present if success is reported as failure. |
| Gemini unbounded timeout | **Small Phase 11 safety item** | Document worst-case and/or set finite timeout on Gemini client — proportionate, not a redesign. |

## Constraint tensions for the operator

These locked decisions stand. Surface residual risk honestly — do not quietly overturn them:

1. **Env remains config; Settings REJECTED** — Compatible with scoped restore and optional per-call kwargs. Config *parsing* stays distributed; only error contract and per-call scoping centralise at `service.py`. Partial compliance with "centralize configuration" project rule — conscious YAGNI.
2. **Packaging PARKED** — Residual danger is real: `sys.path` embed is broken in both directions. v2.0 ships detection + reserved-name list only. **Next milestone must lead with packaging** or host integration fails.
3. **Concurrency OUT** — Globals (`_collector`, env, math buffers) make concurrent calls corrupt. Demo Lock→409 enforces the contract.
4. **Demo: stdlib only, `[::1]:8642`, outside package and CI, throwaway** — Load-bearing anti-accretion controls; loopback refuse-to-start is the tripwire.
5. **No Settings, no HTTP framework, no agent frameworks, no new runtime deps** — Affirmed by stack research.
6. **Zero regression on CLI argparse and `gerar` wizard** — Keep `_positive_quantidade` (exit 2 + PT message) alongside domain `le=40`; wizard stays on `main.run()`.
7. **Phases continue as 11 and 12** — not restarting at 1.

## Implications for Roadmap

Continue numbering from Phase 10. Two phases only — keep step 1 of the seam a **pure move** (Architecture sequencing). Encoding + Gemini timeout fit Phase 11 without inventing Phase 13.

### Phase 11: Service Layer Extraction and Core Embed Adjustments
**Rationale:** Everything below the seam depends on a green, behaviour-preserving extraction first; host-safety fixes then land on that boundary before any UI consumes it.
**Delivers:**
- `service.py` with `generate_batch(request, *, max_retries=?, provider=?, reasoning=?) -> ExerciseBatch`
- `main.run()` as CLI adapter (print / `--out` / fail logs / `sys.exit`); wizard unchanged
- `ConfigError(ValueError)` + `kind` at config raise sites; three-way host contract documented
- `_scoped_env` always restoring `LLM_PROVIDER` / `LLM_REASONING_EFFORT` (incl. failover)
- Domain `Field(ge=1, le=40)` + non-empty `topico`; argparse check retained
- Service: no `sys.exit`, no exercise-file writes on library path; token flush lifecycle owned at boundary
- **Encoding harden:** ASCII diagnostics (`->`), CLI stream `reconfigure(encoding="utf-8", errors="replace")`; no library dump of math batches to cp1252 streams
- **Gemini timeout:** finite client timeout + short worst-case note for the host
- Name-collision self-check / reserved-name list (detection only; packaging stays parked)
- Fix three tests pinned to `main` internals after delegation

**Addresses:** TS-01, TS-02, TS-04, TS-05 (minimal), TS-06, TS-07, TS-08 (service path), TS-09, TS-10/11 (contract draft), Pitfalls 1–4, 7–11, 16
**Avoids:** Mixing env/error behaviour into the pure-move commit; deleting argparse bound; introducing Settings or packaging
**Deferred inside Phase 11 (explicit debt):** full print→logging conversion (TS-03 mechanical pass) — document stderr writes + `redirect_stderr`

### Phase 12: Demo UI at `[::1]:8642`
**Rationale:** Demo is the acceptance test for the boundary; needs error `kind` and a safe service path first.
**Delivers:**
- `demo/` at repo root (outside package, outside CI): stdlib only, inline CSS/JS (no CDN)
- Bind `::1:8642` via `ThreadingHTTPServer` subclass `address_family = AF_INET6`; refuse non-loopback
- Form mirroring CLI defaults/bounds; side-by-side rendered exercises + raw `model_dump()` JSON
- "Gerando…" + disabled submit; honest error panel by category + PT message (no stderr dump on page)
- Module-level Lock around generate; second caller gets **HTTP 409**
- Host/Origin allowlist + require `application/json` on generate route; optional generation budget
- Loud throwaway banner + `demo/README.md` expiry / delete-at-close note
- Demo loads `.env` in its own `__main__` (service does not)

**Addresses:** DM-01…DM-04, DM-06; Pitfalls 12–15, 17
**Uses:** Phase 11 `service.generate_batch` + error contract
**Avoids:** Productising the demo; FastAPI; dual-stack wildcards; rendering diagnostics/credentials

### Phase Ordering Rationale

- Pure seam extraction first so "zero CLI regression" is checkable against the untouched suite, then hygiene, then demo.
- Encoding + Gemini timeout before Phase 12 so demo day cannot invent failures that are already latent.
- Packaging stays out so Phase 11 remains a boundary win independent of host stack discovery — but the roadmapper must list unpark packaging as the **first item of the milestone after v2.0**.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 11 (light):** Exact Gemini `HttpOptions.timeout` units/value and aggregate worst-case arithmetic across RELY × model walk × failover — confirm against current SDK docs at plan time.
- **Phase 11 (light):** Which of the three filesystem sites (NDJSON flush, postmortem, fail log) stay CLI-only vs env-gated no-op — proportionate options already in PITFALLS; pick one in plan-phase.

Phases with standard patterns (skip research-phase):
- **Phase 11 seam extraction / scoped env / ConfigError** — well-documented in ARCHITECTURE.md with line-level map
- **Phase 12 stdlib demo server** — STACK + PITFALLS already prescribe the ~20-line shape

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Local probes (IPv6, sys.path collision) + Context7/CPython/PyPA |
| Features | HIGH on table stakes; MEDIUM on differentiators | Official logging/SDK docs + direct code read; demo scope is judgement |
| Architecture | HIGH | Official mypy/Click/PyPA patterns + repo line map |
| Pitfalls | HIGH | First-hand Windows cp1252 / SystemExit / finally probes on this machine |

**Overall confidence:** HIGH

### Gaps to Address

- **Host preference on usage-in-response:** Signature stays `ExerciseBatch` for v2.0; ask at the demo whether usage should lead the next hardening pass (already the recommended default).
- **OpenAI/google-genai unbounded major pins:** Out of v2.0 scope; backlog only.
- **Token NDJSON on service path:** Architecture notes flush still writes under package dir unless gated — plan-phase must choose env-root or guarded no-op without a storage abstraction.
- **DF-05 dry-run:** Features wanted it in MVP; Architecture/KISS did not require it for the seam. Treat as optional Phase 11 stretch only if it stays tiny — do not block demo.

## Sources

### Primary (HIGH confidence)
- Context7 `/websites/python_3_library`, `/openai/openai-python`, `/googleapis/python-genai`, `/pypa/hatch`, `/pypa/setuptools`
- CPython `http.server` / logging HOWTO / import system; PyPA entry-points + src-layout guidance
- Executed locally (Windows 10.0.22631): `::1` bind, module-shadowing vs real `exercise-ai/`, cp1252 encode failures, `SystemExit` vs `except Exception`
- Repo read: `main.py`, `failover.py`, `reliability.py`, `generator*.py`, `models.py`, `token_usage/`, tests, CI workflow

### Secondary (MEDIUM confidence)
- Practitioner exception/SDK design consensus (SE.SE, Bird SDK concepts, python-list library etiquette)
- Local-AI loopback CSRF / Host-header advisories

### Tertiary (LOW confidence)
- Demo UX checklist (DM-*) — judgement for one-off host handoff; no published practice

---
*Research completed: 2026-09-16*
*Ready for roadmap: yes*
*Phases: 11 (service embed) → 12 (demo); next milestone leads with packaging/rename*
