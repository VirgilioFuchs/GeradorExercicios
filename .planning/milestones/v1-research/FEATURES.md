# Feature Research

**Domain:** AI-powered math exercise generation
**Researched:** 2026-09-01
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Parameterized input (topic, difficulty, count) | Core use case | LOW | JSON or CLI args |
| Structured exercise output (statement, answer, explanation) | Usable without manual cleanup | MEDIUM | Pydantic + Structured Outputs |
| Structural validation | LLM output is unreliable | LOW | Validator module + tests |
| Clear error messages | Developers and teachers need to debug | LOW | Missing API key, invalid JSON, wrong count |
| Environment-based API config | Security baseline | LOW | `.env` + `.env.example` |
| Portuguese exercise content | Target audience (AGENT.md) | LOW | Prompt language, not code |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Controlled retry on validation failure | Higher success rate without infinite loops | MEDIUM | Max 1–2 attempts with logged reason |
| Difficulty levels (fácil/médio/difícil) | Curriculum alignment | LOW | Enum in schema + prompt |
| Topic scoping in prompt | Reduces off-topic exercises | LOW | Explicit topic constraint |
| Dev logging (duration, validation reason) | Observability for learning | LOW | stdlib logging |
| Future math correctness validation | Trust in answers | HIGH | Deferred post-MVP |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Multi-agent orchestration | "More AI" | Overkill; obscures learning goals | Linear pipeline |
| RAG over textbook corpus | "Better exercises" | Complexity before basics work | Prompt with topic |
| Real-time web UI first | Demos look good | Delays core generator | CLI MVP |
| Unlimited auto-retry | "Always get output" | Cost + latency spiral | Cap at 2 retries |
| Calling v1 an "agent" | Marketing | Misleading architecture | LLM application |

## Feature Dependencies

```
Structural validation
    └──requires──> JSON output from LLM
                       └──requires──> Prompt templates + API call

Retry on failure
    └──requires──> Validator with error reasons

MySQL persistence (v2)
    └──requires──> Stable exercise schema

Performance analysis (v4)
    └──requires──> MySQL + attempt history

Agent loop (v6)
    └──requires──> Tools (DB, generator, validator)
```

## MVP Definition

### Launch With (v1)

- [ ] CLI entry (`python main.py`) with input parameters
- [ ] LLM generation with structured JSON output
- [ ] Validator: JSON, keys, count, non-empty fields
- [ ] Error handling: API key, network, timeout, rate limit, invalid structure
- [ ] Unit tests for validator (mocked LLM responses)
- [ ] Modular file layout per AGENT.md

### Add After Validation (v1.x)

- [ ] Bounded retry/regeneration on validation failure
- [ ] Math correctness checks (symbolic or rule-based)
- [ ] CLI arguments (argparse) instead of hardcoded demo input

### Future Consideration (v2+)

- [ ] MySQL persistence (students, attempts, scores)
- [ ] Performance analytics and topic recommendation
- [ ] Personalization from student history
- [ ] Agent with tool use and decision loop

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Structured JSON generation | HIGH | MEDIUM | P1 |
| Structural validator + tests | HIGH | LOW | P1 |
| Env-based API key | HIGH | LOW | P1 |
| Error handling | HIGH | MEDIUM | P1 |
| Retry policy | MEDIUM | LOW | P2 |
| Math validation | HIGH | HIGH | P3 (post-MVP) |
| MySQL | MEDIUM | HIGH | v2 |
| Agent | LOW (MVP) | HIGH | v6 |

## Competitor Feature Analysis

| Feature | Khan-style platforms | Generic ChatGPT | Our Approach |
|---------|---------------------|-----------------|--------------|
| Topic-aligned exercises | Curated content | Ad-hoc prompts | Parameterized + validation |
| Structured output | DB-backed | Manual copy-paste | JSON schema enforced |
| Difficulty control | Built-in levels | Prompt-only | Enum + prompt + validation |
| Answer explanations | Human-reviewed | Variable quality | Required field + future validation |

## Sources

- AGENT.md — explicit MVP scope and evolution stages
- OpenAI educational examples — math tutor structured output patterns
- Domain conventions for ed-tech exercise generators

---
*Feature research for: math exercise AI generator*
*Researched: 2026-09-01*
