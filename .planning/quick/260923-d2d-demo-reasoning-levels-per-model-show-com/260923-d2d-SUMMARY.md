---
id: "260923-d2d"
status: complete
completed: "2026-09-23"
commit: "a03ec71"
---

# Quick Summary: Per-model reasoning in demo

## Done

- `reasoning.py`: `supported_reasoning_levels` + `assert_reasoning_compatible`; reject API-only `xhigh`/`max` (not shared with other models)
- `/models`: each entry `{id, reasoning:[...]}` + `reasoning_levels`
- Demo UI: model labels show `pensamento: none|low|medium|high` or `sem pensamento`; reasoning select filters to the selected model
- POST `/gerar` validates model↔reasoning (400 on incompatible)
- Tests: reasoning + demo tracer/ui — green

## GPT-6 Sol/Luna

Shown levels: **none | low | medium | high**  
Not shown (incompatible with shared surface): **xhigh**, **max**
