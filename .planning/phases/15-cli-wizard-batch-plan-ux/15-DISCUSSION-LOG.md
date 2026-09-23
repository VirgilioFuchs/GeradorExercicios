# Phase 15 — Discussion Log

**Date:** 2026-09-23  
**Mode:** Agent-recommended defaults (user: “coloque o que você achar melhor”)

## Areas selected
All four gray areas (wizard flow, argparse shape, demo parity, docs/matrix).

## Decisions (summary)
| Area | Choice |
|------|--------|
| Wizard | 3 band counts + quantidade; soft-warn; order matéria→tópico→bands→qty→… |
| Argparse | `--plano F,M,D` only; no triple flags |
| Payload | Mirror demo: mixed→plano, uniform→legacy |
| DRY | Shared `plan_ux` helper for wizard + argparse |
| Docs | README short note + --help; offline tests |

## Skipped / deferred
- `--facil/--medio/--dificil` flags
- TIPO-OPEN
