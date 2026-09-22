---
id: "260922-ep5"
title: "Demo painel de uso de tokens/tempo como CLI [USAGE]"
status: complete
created: "2026-09-22"
completed: "2026-09-22"
slug: "demo-painel-de-uso-de-tokens-tempo-como"
mode: quick
---

# Summary: Demo painel de uso de tokens

## Done

- `GET /usage/sessions` and `GET /usage/session` in `demo/serve.py` read only `TOKEN_USAGE_DIR` (patchable `_USAGE_DIR`); aggregate by `run_id` with CLI-like token/duration/usd sums and tentativas/sucessos/erros.
- Offline fixtures in `demo/tests/test_usage_endpoints.py` (tmp_path only; no real NDJSON).
- Third demo tab **Uso**: select `run_id`, refresh, empty state, summary panel + compact events.
- Fail-closed markers in `test_ui_markers.py`; `demo/README.md` Safety note for Uso / token-usage.

## Commits

1. `feat(demo): add token-usage session endpoints`
2. `feat(demo): add Uso tab for token-usage panel`
3. `test(demo): lock Uso markers and document token-usage panel`

## Verify

- `pytest demo/tests/test_usage_endpoints.py -q` → 7 passed
- Marker string check for Uso UI → ok
- `pytest demo/tests -q` → 30 passed

## Operator note

Restart `python demo/serve.py` if the running process predates the new `/usage/*` routes.
