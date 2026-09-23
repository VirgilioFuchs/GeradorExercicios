---
id: "260923-da9"
status: complete
completed: "2026-09-23"
commit: "3a97d1f"
---

# Quick Summary: xhigh/max visible only when supported

## Done

- OpenAI reasoning models (GPT-5*/GPT-6*/o*): `none|low|medium|high|xhigh|max`
- Gemini / Grok: base four only (no xhigh/max)
- gpt-4o*: sem pensamento
- Demo rebuilds reasoning select on provider/model change
- POST validates: gpt-6+xhigh ok; gemini+xhigh → 400

Restart `demo/serve.py` after pull.
