---
id: "260922-ep5"
title: "Demo painel de uso de tokens/tempo como CLI [USAGE]"
status: planned
created: "2026-09-22"
slug: "demo-painel-de-uso-de-tokens-tempo-como"
mode: quick
---

# Quick Plan: Demo painel de uso de tokens

## Goal

Operator vê no demo um painel (aba/coluna) com totais CLI-like (`in`/`out`/`total`, `duration_ms`, `usd`) **mais** contagens `tentativas` / `sucessos` / `erros`, escolhendo um `run_id` a partir dos NDJSON em `exercise-ai/token-usage/{YYYY-MM-DD}/{provider}.ndjson`.

## Approach

- Dois GETs stdlib em `demo/serve.py` que leem **somente** `TOKEN_USAGE_DIR` (nunca `.env` / keys).
- Agrupar eventos por `run_id` across all day/provider files; agregados no servidor.
- Terceira aba **Uso** no demo (mesmo design system system-ui); empty state se pasta vazia.
- Testes offline: markers fail-closed + fixtures em tempdir (não commitar logs reais).

## Discretion locked

| Choice | Value |
|--------|-------|
| Surface | Terceira aba `Uso` + painel (não redesign da página) |
| Metrics | in/out/total (soma numéricos), duration_ms (soma), usd (soma numéricos senão `indisponível`), counts por `status` |
| Sessions | Listar `run_id` distintos; operador seleciona um |
| Server | stdlib only; sem npm/pip novo |
| Empty | UI empty state; endpoints retornam listas/objetos vazios |

<objective>
Add a throwaway demo usage panel backed by token-usage NDJSON so operators can inspect a past `run_id` like stderr `[USAGE]`, plus attempt/success/error counts.
Output: `demo/serve.py` usage endpoints, `demo/index.html` + `demo/app.js` Uso tab, offline tests with temp fixtures.
</objective>

<context>
@exercise-ai/token_usage/collector.py
@demo/serve.py
@demo/index.html
@demo/app.js
@demo/tests/test_ui_markers.py
@demo/tests/test_tracer_gerar.py
@README.md
</context>

<proven_verify_commands>
- `pytest demo/tests -q`
</proven_verify_commands>

<tasks>

<task type="auto" id="1">
  <name>Task 1: GET /usage/sessions + /usage/session from TOKEN_USAGE_DIR</name>
  <files>demo/serve.py, demo/tests/test_usage_endpoints.py</files>
  <read_first>
    exercise-ai/token_usage/collector.py,
    demo/serve.py,
    demo/tests/test_tracer_gerar.py
  </read_first>
  <action>
    In `demo/serve.py`:

    1. Import `TOKEN_USAGE_DIR` from `token_usage.collector` (already on `sys.path` via `exercise-ai/`). Keep a module-level alias (e.g. `_USAGE_DIR`) that tests can patch.

    2. Add helper `_iter_usage_events(base: Path) -> list[dict]` that:
       - If `base` missing or not a dir → return `[]`.
       - Walk only `base / YYYY-MM-DD / *.ndjson` (day dirs matching `\d{4}-\d{2}-\d{2}`; files ending `.ndjson`).
       - Skip path traversal / non-files; ignore corrupt JSON lines (continue).
       - Never open files outside `base.resolve()`.

    3. `GET /usage/sessions` → JSON:
       ```json
       {"ok": true, "sessions": [{"run_id": "...", "event_count": N, "first_ts": "...", "last_ts": "...", "providers": ["openai"]}]}
       ```
       Group all events by `run_id`; sort sessions by `last_ts` descending. Empty dir → `{"ok": true, "sessions": []}`.

    4. `GET /usage/session?run_id=...` → JSON:
       ```json
       {
         "ok": true,
         "run_id": "...",
         "events": [ /* UsageEvent dicts for that run_id, chronological */ ],
         "summary": {
           "prompt_tokens": <int|null|"indisponível">,
           "completion_tokens": <int|null|"indisponível">,
           "total_tokens": <int|null|"indisponível">,
           "duration_ms": <int>,
           "usd": <float|"indisponível">,
           "tentativas": <int>,
           "sucessos": <int>,
           "erros": <int>,
           "event_count": <int>
         }
       }
       ```
       Aggregation rules (mirror `_sum_numeric` / CLI resumo spirit):
       - Token fields: sum only `int` values; if no ints → `"indisponível"`.
       - `duration_ms`: sum of ints (default 0).
       - `usd`: sum only numeric usd; if none → `"indisponível"` (never invent `0`).
       - Counts: `tentativas` = status==`"attempt"`, `sucessos`==`"success"`, `erros`==`"error"`.
       - Missing/unknown `run_id` → `{"ok": true, "run_id": "...", "events": [], "summary": {...zeros/indisponível...}}` OR `{"ok": false, "error": {...}}` with 404 — prefer **200 + empty events** for simpler UI.
       - Reject empty/`..`/path-like `run_id` with 400.

    5. Wire both paths in `DemoHandler.do_GET` alongside `/models`. Response body must never include API keys, prompts, or `.env` contents — only UsageEvent fields already on disk.

    6. Add `demo/tests/test_usage_endpoints.py` using the same `demo_server` pattern as `test_tracer_gerar.py`:
       - `tmp_path` with fake `2026-01-01/openai.ndjson` containing 2–3 events across 2 `run_id`s (statuses attempt/success/error, mix of numeric + `"indisponível"` usd).
       - Patch serve’s usage dir to `tmp_path`.
       - Assert `/usage/sessions` lists both run_ids; `/usage/session?run_id=...` returns events + correct counts and token/duration sums.
       - Assert empty temp dir → `sessions: []`.
       - Do **not** read or depend on real `exercise-ai/token-usage/**` files.
  </action>
  <verify>
    <automated>pytest demo/tests/test_usage_endpoints.py -q</automated>
    <fails_when>non-zero exit, collection errors, failed assertions, or tests reading real token-usage files</fails_when>
  </verify>
  <acceptance_criteria>
    - `demo/serve.py` contains exact path strings `/usage/sessions` and `/usage/session`
    - `demo/serve.py` references `TOKEN_USAGE_DIR` (or patched alias of it) and does not read `.env` for these handlers
    - `demo/tests/test_usage_endpoints.py` exists and asserts `tentativas`/`sucessos`/`erros` from fixture statuses
    - Fixture NDJSON lives only under pytest `tmp_path` (not committed under `exercise-ai/token-usage/`)
  </acceptance_criteria>
  <done>Both usage GETs work against injectable dir; offline endpoint tests green.</done>
</task>

<task type="auto" id="2">
  <name>Task 2: Aba Uso — select run_id + painel CLI-like</name>
  <files>demo/index.html, demo/app.js</files>
  <read_first>
    demo/index.html,
    demo/app.js,
    exercise-ai/token_usage/collector.py
  </read_first>
  <action>
    Extend the throwaway demo UI without redesigning layout (keep `system-ui`, existing `.tabs` / `.panel` patterns).

    **`demo/index.html`:**
    - Add third tab button: id `tab-uso`, label `Uso`, `aria-controls="panel-uso"`.
    - Add `panel-uso` (role=tabpanel): 
      - `<select id="usage-run-select">` (placeholder option “Nenhuma sessão”)
      - Button `id="usage-refresh"` label `Atualizar`
      - Empty hint `id="usage-empty"` (PT): e.g. “Nenhum registro de uso. Gere um lote ou verifique `exercise-ai/token-usage/`.”
      - Summary region `id="usage-summary"` showing CLI-like lines / labeled fields:
        `in`, `out`, `total`, `duration_ms`, `usd`, plus `tentativas`, `sucessos`, `erros`
      - Optional compact event list `id="usage-events"` (monospace/`pre` or short rows) — keep secondary to the summary totals.
    - Do not widen page into a dashboard; one more tab is enough.

    **`demo/app.js`:**
    - Extend `showTab` to three tabs (`exercicios` | `json` | `uso`).
    - On load and on `usage-refresh` click: `fetch("/usage/sessions")` → populate `#usage-run-select` with `run_id` options (show `run_id` + optional `last_ts`).
    - On select change (and after populate if a value selected): `fetch("/usage/session?run_id=" + encodeURIComponent(id))` → render summary fields CLI-like (same labels as stderr `[USAGE]` token line: in/out/total/duration_ms/usd) and the three counts.
    - Empty `sessions` → show `#usage-empty`, clear summary.
    - Failures: soft message in the Uso panel (do not wipe Exercícios/JSON); never display secrets.
    - After successful `/gerar`, optionally call refresh sessions so the new `run_id` appears (best-effort; do not block generate UX).
  </action>
  <verify>
    <automated>python -c "from pathlib import Path; t=(Path('demo/index.html').read_text(encoding='utf-8')+Path('demo/app.js').read_text(encoding='utf-8')); req=['tab-uso','panel-uso','usage-run-select','/usage/sessions','/usage/session','tentativas','sucessos','erros','duration_ms']; missing=[r for r in req if r not in t]; assert not missing, missing"</automated>
    <fails_when>AssertionError, missing markers, or non-zero exit</fails_when>
  </verify>
  <acceptance_criteria>
    - `demo/index.html` contains `tab-uso`, `panel-uso`, `usage-run-select`, `usage-empty`, and visible labels/ids for tentativas/sucessos/erros (or those strings in the panel chrome)
    - `demo/app.js` contains `/usage/sessions`, `/usage/session`, and fetch+render for the selected `run_id`
    - Empty sessions path shows empty-state copy (not a broken select)
    - No new npm deps; no redesign of Contrato/Ambiente form
  </acceptance_criteria>
  <done>Operator can open Uso, pick a run_id, see CLI-like totals + attempt/success/error counts.</done>
</task>

<task type="auto" id="3">
  <name>Task 3: Fail-closed UI markers + docs touch</name>
  <files>demo/tests/test_ui_markers.py, demo/README.md</files>
  <read_first>
    demo/tests/test_ui_markers.py,
    demo/README.md,
    README.md
  </read_first>
  <action>
    1. Extend `demo/tests/test_ui_markers.py` (same fail-closed string-assert pattern):
       - index markers: `tab-uso`, `panel-uso`, `usage-run-select`, `Uso`
       - app.js markers: `/usage/sessions`, `/usage/session`, `tentativas`, `sucessos`, `erros`
       - Add needles to the combined cross-file test as appropriate.

    2. One short note in `demo/README.md` (Safety or Run section): Uso tab reads local NDJSON under `exercise-ai/token-usage/`; no secrets in the page; outside CI.

    3. Do **not** commit real usage NDJSON; do not remove `.gitignore` rules for `exercise-ai/token-usage/**`.

    4. Run full demo suite.
  </action>
  <verify>
    <automated>pytest demo/tests -q</automated>
    <fails_when>non-zero exit, missing Uso/usage markers, collection errors, or failed/errored tests</fails_when>
  </verify>
  <acceptance_criteria>
    - `test_ui_markers.py` fails if `tab-uso` or `/usage/sessions` removed from demo sources
    - `demo/README.md` mentions Uso or `token-usage`
    - `pytest demo/tests -q` passes
    - No real `exercise-ai/token-usage/**/*.ndjson` staged for commit by this task
  </acceptance_criteria>
  <done>Marker tests + demo suite green; docs mention the Uso surface.</done>
</task>

</tasks>

<verification>
- `pytest demo/tests -q` green
- Manual smoke (optional): `python demo/serve.py` → aba Uso lists run_ids from local NDJSON if present; empty dir shows empty state
</verification>

<success_criteria>
- Panel shows in/out/total, duration_ms, usd (or indisponível), tentativas/sucessos/erros for selected run_id
- Endpoints only read TOKEN_USAGE_DIR; no API keys exposed
- Throwaway demo remains stdlib-only
</success_criteria>

## PLAN COMPLETE
