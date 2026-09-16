# Pitfalls Research

**Domain:** LLM-based educational exercise generation
**Researched:** 2026-09-01
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Markdown-Wrapped JSON

**What goes wrong:**
Model returns ` ```json ... ``` ` despite instructions, breaking `json.loads`.

**Why it happens:**
Training bias toward conversational formatting; prompt-only JSON mode is weak.

**How to avoid:**
Use OpenAI Structured Outputs (`response_format` + Pydantic `.parse()`); keep text fallback parser only as backup.

**Warning signs:**
Integration tests pass with mocks but production fails intermittently.

**Phase to address:**
Phase 1 (generator setup)

---

### Pitfall 2: Wrong Exercise Count

**What goes wrong:**
User requests 5 exercises; model returns 3 or 7.

**Why it happens:**
LLMs weak at exact counting; no post-check.

**How to avoid:**
Validator enforces `len(exercicios) == quantidade`; retry with explicit error in prompt.

**Warning signs:**
Validator tests pass but manual runs show count drift.

**Phase to address:**
Phase 1 (validator)

---

### Pitfall 3: Empty or Placeholder Fields

**What goes wrong:**
Exercises with `""` enunciado or generic "explicação" copy-paste.

**Why it happens:**
Schema satisfied syntactically but not semantically.

**How to avoid:**
Validator rejects empty/whitespace-only strings; future `@field_validator` for min length.

**Warning signs:**
JSON validates but teachers reject output quality.

**Phase to address:**
Phase 1 (validator), Phase 2 (semantic checks)

---

### Pitfall 4: API Key Leakage

**What goes wrong:**
Keys in git, logs, or error tracebacks.

**Why it happens:**
Quick debugging, missing `.gitignore`.

**How to avoid:**
`.env` only; `.env.example` without secrets; never log request headers.

**Warning signs:**
Key visible in README or test fixtures.

**Phase to address:**
Phase 1 (project scaffold)

---

### Pitfall 5: Infinite Retry Loop

**What goes wrong:**
Validation fails → retry forever → cost spike.

**Why it happens:**
"Make it work" loops without cap.

**How to avoid:**
Max 1–2 retries per AGENT.md; log failure reason; exit with clear error.

**Warning signs:**
No retry counter in code.

**Phase to address:**
Phase 2 (reliability)

---

### Pitfall 6: Off-Topic Exercises

**What goes wrong:**
Requested "equação do 1º grau" but got geometry.

**Why it happens:**
Weak prompt constraints; no topic enforcement.

**How to avoid:**
Explicit prompt: "somente tópico X"; include topic in system message; manual QA samples.

**Warning signs:**
Stakeholder reports irrelevant exercises.

**Phase to address:**
Phase 1 (prompts)

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skip validator tests | Faster first commit | Regressions undetected | Never |
| Hardcode demo input in main | Quick demo | Not reusable CLI | MVP day-1 only |
| Raw dicts instead of models | Less code | Schema drift | Never at LLM boundary |
| Single giant prompt string | Simple | Hard to maintain | MVP if centralized in prompts.py |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| OpenAI API | No timeout | `timeout=30` on client |
| OpenAI API | Ignoring `refusal` | Check refusal field; surface to user |
| OpenAI API | Unpinned model alias | Pin `gpt-4o-mini` or `gpt-4o-2024-08-06` |
| dotenv | Committing `.env` | `.gitignore` + `.env.example` |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Sync calls in batch jobs | Slow throughput | Async/batching later | >100 requests |
| Huge prompts with history | Token cost | Send only relevant context (future) | Personalization phase |
| No caching | Repeated identical requests | Cache by hash (future) | API quota limits |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Logging full API responses in prod | PII / key exposure | Dev-only debug logs |
| User-controlled prompt injection | Jailbreak / off-topic | Sanitize inputs; system prompt boundaries |
| Exposing generator as public API without auth | Cost abuse | Auth before HTTP layer (v2+) |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Opaque "Error" messages | Can't fix config | Specific: missing key, invalid JSON, wrong count |
| No progress indication | Feels hung on slow API | Log "generating..." + duration |
| Mixed languages in output | Confusing for students | Portuguese in exercises; consistent labels |

## "Looks Done But Isn't" Checklist

- [ ] **Generator:** Often missing validator — verify invalid JSON is rejected
- [ ] **Validator:** Often missing count check — verify `quantidade` enforcement
- [ ] **Errors:** Often swallow exceptions — verify explicit messages for each case
- [ ] **Tests:** Often only happy path — verify 7 negative cases from AGENT.md
- [ ] **Security:** Often `.env` committed — verify `.gitignore`

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Markdown JSON | LOW | Switch to Structured Outputs |
| Wrong count | LOW | Add validator + retry |
| Key leaked | HIGH | Rotate key, scrub git history |
| Agent framework added too early | MEDIUM | Strip to pipeline modules |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Invalid JSON structure | Phase 1 | Validator unit tests |
| API/config errors | Phase 1 | Manual run without key |
| Retry/cost control | Phase 2 | Test max retry enforced |
| Math wrong answers | Phase 3+ | Symbolic check tests |
| Data loss | Phase 4 (MySQL) | Integration tests |

## Sources

- AGENT.md — error handling, retry, logging rules
- OpenAI Structured Outputs docs — refusal, schema constraints
- Common LLM app failure modes (2025–2026)

---
*Pitfalls research for: math exercise AI generator*
*Researched: 2026-09-01*
