# Demo local Embed (throwaway)

Throwaway stdlib demo that consumes the Phase 11 embed contract (`generate_batch`)
so operators can see form → generation → rendered exercises + contract JSON.

## Expiry / delete-at-close

This tree is **throwaway**. Delete `demo/` at **v2.0 close** — do not productize
into a real HTTP API, do not promote to staging, and do not add it to CI.

## Run

From the repository root:

```bash
python demo/serve.py
```

Then open the literal IPv6 loopback URL (bracketed form — do **not** substitute
an IPv4-first hostname alias such as `localhost`):

**http://[::1]:8642/**

## Loopback-only bind

The server binds **`[::1]:8642`** only and refuses non-loopback hosts.

Quick check that nothing is listening on a wildcard:

```bash
netstat -an | findstr 8642
```

Expect a listener on `[::1]:8642` (or equivalent IPv6 loopback), **not** `0.0.0.0:8642`
or `*:8642`.

## Not for staging

Loopback-only, Host/Origin allowlist, sequential Lock → HTTP 409. This is a lab
screen-share surface — **not** a staging or production service.

## No CI / no new deps

- Outside GitHub Actions (`pytest exercise-ai -q` remains the CI command).
- Stdlib only for the HTTP surface; no new pip/npm dependencies for this demo.
- Offline guards/UI marker tests live under `demo/tests/` for local use:
  `pytest demo/tests -q`.

## Safety

Never render stderr diagnostics or `.env` secret values in the page. Errors show
typed class / message / kind only.

The **Uso** tab reads local NDJSON under `exercise-ai/token-usage/` via
`GET /usage/sessions` and `GET /usage/session` — no API keys or prompts on the
page. Outside CI; restart `python demo/serve.py` if new routes are missing.
