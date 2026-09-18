---
phase: 11-service-layer-extraction
plan: 03
subsystem: api
tags: [encoding, cp1252, gemini, timeout, README, embed-contract, pytest]

requires:
  - phase: 11-service-layer-extraction
    provides: error subclasses + env restore (11-02)
provides:
  - ASCII-safe FAILOVER/validation diagnostics + CLI utf-8 reconfigure
  - Gemini HttpOptions.timeout=30000 ms pinned by test
  - README Embed / biblioteca contract (three subclasses, reserved names, sequential)
affects: [phase-12-demo]

actuals:
  tokens: 4200
  tasks: 3
  commits: 6

tech-stack:
  added: []
  patterns:
    - HttpOptions.timeout in milliseconds (google-genai); align magnitude to OpenAI 30s
    - stderr dumps use ensure_ascii / encode(errors=replace) for cp1252 safety
    - CLI stdout/stderr reconfigure(encoding=utf-8, errors=replace) at adapter startup

key-files:
  created:
    - exercise-ai/tests/test_encoding.py
  modified:
    - exercise-ai/failover.py
    - exercise-ai/validator.py
    - exercise-ai/main.py
    - exercise-ai/generator_gemini.py
    - exercise-ai/tests/test_failover.py
    - exercise-ai/tests/test_generators.py
    - README.md

key-decisions:
  - "Gemini timeout=30000 ms per Context7 /googleapis/python-genai HttpOptions"
  - "Validation dump uses ensure_ascii=True + _write_stderr_safe fallback"
  - "README section only (no CONTRACT.md); reserved names detection-only"

patterns-established:
  - "Runtime diagnostic arrows are ASCII -> on Windows-facing paths"
  - "Host contract documented in README Embed / biblioteca"

requirements-completed: [EMBED-05, EMBED-06, EMBED-07]

coverage:
  - id: D1
    description: cp1252-safe FAILOVER/validation diagnostics and CLI utf-8 stream reconfigure
    requirement: EMBED-06
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_encoding.py
        status: pass
      - kind: unit
        ref: exercise-ai/tests/test_failover.py
        status: pass
    human_judgment: false
  - id: D2
    description: Gemini client finite HttpOptions.timeout=30000 ms aligned to OpenAI 30s
    requirement: EMBED-05
    verification:
      - kind: unit
        ref: exercise-ai/tests/test_generators.py#test_gemini_client_http_timeout_is_30000_ms
        status: pass
    human_judgment: false
  - id: D3
    description: README embed contract with generate_batch, three error subclasses, reserved names, sequential note, worst-case latency
    requirement: EMBED-07
    verification:
      - kind: other
        ref: Select-String README anchors generate_batch|ConfigError|InvalidRequestError|GenerationFailedError|reserved|sequential
        status: pass
      - kind: unit
        ref: pytest exercise-ai -q (155 passed)
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-09-16
status: complete
---

# Phase 11 Plan 03: Encoding, Gemini timeout, README embed contract Summary

**Windows cp1252-safe diagnostics, Gemini 30s HTTP timeout, and a README host embed contract covering the three error subclasses.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-09-16T15:10:16Z
- **Completed:** 2026-09-16T15:15:56Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- Replaced Unicode arrows with ASCII `->` on FAILOVER and success-log paths; hardened validation stderr dumps; CLI `reconfigure(utf-8, replace)`.
- Set `genai.Client(..., http_options=types.HttpOptions(timeout=30000))` (ms per google-genai); unit test pins the value.
- Added README **Embed / biblioteca**: `generate_batch`, JSON shape, three-subclass error table, sequential contract, reserved flat module names, Gemini worst-case note.
- Full offline suite: **155 passed**.

## Task Commits

1. **Task 1 RED:** `7a97dab` — test(11-03): add failing tests for cp1252-safe diagnostics
2. **Task 1 GREEN:** `ac83d1d` — feat(11-03): ASCII-safe diagnostics and CLI utf-8 reconfigure
3. **Task 2 RED:** `c4737dc` — test(11-03): add failing test for Gemini HttpOptions timeout
4. **Task 2 GREEN:** `d4c3144` — feat(11-03): set Gemini HttpOptions.timeout to 30000 ms
5. **Task 3:** `e392fd5` — docs(11-03): add README embed contract section

## Files Created/Modified

- `exercise-ai/tests/test_encoding.py` — cp1252 stream regressions
- `exercise-ai/failover.py` — ASCII FAILOVER hop arrow
- `exercise-ai/validator.py` — `_write_stderr_safe` + `ensure_ascii` dump
- `exercise-ai/main.py` — `_reconfigure_stdio`, ASCII success log arrow
- `exercise-ai/generator_gemini.py` — HttpOptions.timeout=30000
- `exercise-ai/tests/test_failover.py` / `test_generators.py` — expectation + timeout pin
- `README.md` — Embed / biblioteca section

## Decisions Made

- Confirmed via Context7 `/googleapis/python-genai`: `HttpOptions.timeout` is **milliseconds**.
- Validation dumps prefer `ensure_ascii=True` so math glyphs never hit the stream encoder; replace fallback remains for residual text.
- Reserved-name collision is documentation-only (no runtime self-check).

## Deviations from Plan

None - plan executed exactly as written.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None beyond plan mitigations T-11-07 / T-11-08 / T-11-09.

## Issues Encountered

None.

## Next

Phase 11 plans complete — ready for phase verify / Phase 12 demo planning. Deferred: PKG-01, OBS-01, LOG-01, kwargs on `generate_batch`.

## Self-Check: PASSED

- FOUND: exercise-ai/tests/test_encoding.py
- FOUND: exercise-ai/generator_gemini.py (`HttpOptions|timeout`)
- FOUND: README.md (`generate_batch|ConfigError|reserved`)
- FOUND: commits 7a97dab, ac83d1d, c4737dc, d4c3144, e392fd5
- VERIFY: `pytest exercise-ai -q` → 155 passed
