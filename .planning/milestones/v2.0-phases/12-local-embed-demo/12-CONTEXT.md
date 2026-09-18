# Phase 12: Local Embed Demo - Context

**Gathered:** 2026-09-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Throwaway stdlib demo in `demo/` that consumes Phase 11's embed contract (`service.generate_batch`) so the operator and host team see the integration flow end-to-end: form → generation → rendered exercises + contract JSON, with busy/error UX and loopback-only safety. Outside the package and CI. Does not include packaging (PKG-01), widening `generate_batch` return type, print→logging, or productizing the demo into a real HTTP API.

</domain>

<decisions>
## Implementation Decisions

### Page composition
- **D-01:** Primary surfaces are the form and rendered exercises; contract JSON is secondary — **Reversibility:** reversible
- **D-02:** Results area uses tabs **Exercícios | JSON** (switching replaces the view; not an inline toggle) — **Reversibility:** reversible
- **D-03:** Before first success: Exercícios empty; JSON tab shows a schema/shape hint of `ExerciseBatch` fields (no fake exercise data) — **Reversibility:** reversible
- **D-04:** UI chrome in Portuguese; technical identifiers (exception class names, `GenerationRequest` / JSON field names, `kind`) stay in English as in the Python contract — **Reversibility:** reversible

### Form field set
- **D-05:** Form exposes the four `GenerationRequest` fields **plus** provider and reasoning; demo sets env then calls `generate_batch` (provider/reasoning are not part of the request object) — **Reversibility:** reversible
- **D-06:** Two labeled sections: **Contrato (`GenerationRequest`)** vs **Ambiente (só nesta demo)** with an explicit note that env controls are not in the batch JSON — **Reversibility:** reversible
- **D-07:** Demo-ready presets on first load (e.g. Matemática / equação do 1º grau / médio / quantidade 2) so one click generates — **Reversibility:** reversible
- **D-08:** Provider/reasoning controls mirror the wizard: openai|gemini|grok + empty/auto; reasoning none|low|medium|high with default medium — **Reversibility:** reversible

### Busy & error UX
- **D-09:** While generating: disable submit button and show **Gerando…**; leave other fields editable (server Lock still returns 409 if concurrent) — **Reversibility:** reversible
- **D-10:** Errors show a badge with the exception class (`ConfigError` / `InvalidRequestError` / `GenerationFailedError`) plus the PT human message, and `kind` when present — **Reversibility:** reversible
- **D-11:** HTTP 409 uses an explicit sequential-contract message including **HTTP 409** (not a soft “please wait” only) — **Reversibility:** reversible
- **D-12:** On failure after a prior success: keep last good Exercícios/JSON; show error banner above — **Reversibility:** reversible

### Throwaway chrome
- **D-13:** Persistent top banner **and** footer footnote (throwaway / delete at v2.0 close / loopback-only URL) — **Reversibility:** reversible
- **D-14:** `demo/README.md` includes the full anti-accretion pack: expiry/delete-at-close, literal `http://[::1]:8642/` (never `localhost`), `netstat` check, not-for-staging, no CI / no deps — **Reversibility:** reversible
- **D-15:** Root `README.md` Embed section gets a short pointer to `demo/` and the loopback URL with delete-at-close note — **Reversibility:** reversible
- **D-16:** Top banner is dismissible for the browser session (X until reload); footnote remains — **Reversibility:** reversible

### Already locked (carry forward — do not re-litigate)
- Bind `[::1]:8642` via `ThreadingHTTPServer` + `AF_INET6`; refuse non-loopback bind
- Sequential generation: Lock → HTTP 409 when busy
- POST generation requires `application/json` + Host/Origin allowlist
- Stdlib only; outside package and CI; `load_dotenv` only in demo `__main__`
- Render exercises + `ExerciseBatch.model_dump()` only — never stderr/diagnostics/env values
- Consume Phase 11 `generate_batch` + three error subclasses unchanged

### Agent Discretion
- Exact preset topic string and inline CSS/JS structure (single file vs few static files under `demo/`)
- Exact schema-hint wording for the empty JSON tab
- Visual styling of banner/badges/tabs (keep throwaway-simple; no design system)
- How provider empty/auto is represented in the HTML control (empty option vs “auto” label)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone / requirements
- `.planning/REQUIREMENTS.md` — DEMO-01, DEMO-02
- `.planning/ROADMAP.md` — Phase 12 goal, success criteria, notes (stdlib, `[::1]:8642`, load_dotenv in `__main__`)
- `.planning/PROJECT.md` — v2.0 Embed em Produção; Out of Scope (packaging, concurrency as product feature)
- `.planning/research/SUMMARY.md` — demo shape: ThreadingHTTPServer + Lock → 409; throwaway controls
- `.planning/research/PITFALLS.md` — Pitfalls 12–17 (timeouts, ::1 bind, Host/Origin, no stderr render, anti-accretion)
- `.planning/research/STACK.md` — stdlib-only demo stack
- `.planning/seeds/SEED-003-host-embed-images-storytelling.md` — Slice A acceptance via demo

### Prior phase decisions
- `.planning/phases/11-service-layer-extraction/11-CONTEXT.md` — D-01..D-15 embed contract
- `.planning/phases/11-service-layer-extraction/11-VERIFICATION.md` — Phase 11 passed must-haves

### Implementation touchpoints
- `exercise-ai/service.py` — `generate_batch`, error subclasses
- `exercise-ai/models.py` — `GenerationRequest`, `ExerciseBatch`
- `exercise-ai/wizard.py` — provider/reasoning option sets to mirror
- `README.md` — Embed section (add short demo pointer)
- `demo/` — new (does not exist yet)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `generate_batch(GenerationRequest) -> ExerciseBatch` — sole generation entry for the demo handler
- `ConfigError` / `InvalidRequestError` / `GenerationFailedError` (+ `kind`) — map 1:1 to error badges
- `ExerciseBatch.model_dump()` — JSON tab contract payload
- Wizard provider/reasoning option sets (`openai|gemini|grok`, `none|low|medium|high`)

### Established Patterns
- Env is config source; demo `__main__` calls `load_dotenv`; service must not load dotenv on import
- Sequential contract enforced in demo with Lock (not in service)
- Flat modules + `sys.path` for local import (packaging parked — demo uses the same lab layout)

### Integration Points
- New: `demo/` server + static page (stdlib `http.server`)
- Call: `service.generate_batch` after optional env set for provider/reasoning
- Docs: `demo/README.md` + short pointer in root `README.md` Embed section
- Not in CI; no new package dependencies

</code_context>

<specifics>
## Specific Ideas

- Operator chose tabbed JSON (not inline toggle) and schema hint before first generation — teach the contract before the first live call.
- Provider/reasoning stay visually segregated so the host team does not think they are part of `GenerationRequest`.
- 409 messaging should teach the sequential contract, not hide HTTP status.
- Banner dismissible for cleaner screen-share; footnote + README keep the anti-accretion signal.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

(Already deferred at milestone level, unchanged: PKG-01, OBS-01, LOG-01, SEED-003 B/C.)

</deferred>

---

*Phase: 12-Local Embed Demo*
*Context gathered: 2026-09-18*
