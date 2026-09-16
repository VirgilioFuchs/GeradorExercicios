# Architecture Research

**Domain:** Python LLM exercise generation pipeline
**Researched:** 2026-09-01
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI / Entry (main.py)                   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌────────────┐  ┌───────────┐  ┌──────────┐ │
│  │ prompts  │  │ generator  │  │ validator │  │  models  │ │
│  └────┬─────┘  └─────┬──────┘  └─────┬─────┘  └────┬─────┘ │
│       │              │               │              │        │
├───────┴──────────────┴───────────────┴──────────────┴────────┤
│                    External LLM API (OpenAI)                 │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| `main.py` | Orchestration, I/O, top-level error handling | Parse input, call generator → validator, print JSON |
| `prompts.py` | Prompt templates only | `str.format()` or small builder functions |
| `generator.py` | LLM API call, response parsing | `openai.chat.completions.parse()` |
| `validator.py` | Structural validation (and future math checks) | Pure functions on dict/Pydantic models |
| `models.py` | Data contracts | Pydantic `Exercise`, `ExerciseBatch`, `GenerationRequest` |

## Recommended Project Structure

```
exercise-ai/
├── main.py              # CLI entry, orchestration
├── generator.py         # LLM client wrapper
├── validator.py         # Structural validation
├── prompts.py           # Prompt templates
├── models.py            # Pydantic/dataclass models
├── requirements.txt
├── .env.example
├── README.md
└── tests/
    └── test_validator.py
```

### Structure Rationale

- **Flat package:** MVP has few modules; no `src/` nesting needed yet
- **tests/ separate:** Keeps pytest discovery clean; validator tests don't need LLM
- **No `services/` layer:** YAGNI until MySQL or HTTP API added

## Architectural Patterns

### Pattern 1: Pipeline (Linear)

**What:** Input → prompt → LLM → validate → output  
**When to use:** MVP and learning-focused projects  
**Trade-offs:** Simple to reason about; no branching intelligence

### Pattern 2: Schema-First Contract

**What:** Define Pydantic models once; use for API parse + validation  
**When to use:** Any Structured Outputs integration  
**Trade-offs:** Tight coupling to provider SDK; huge reliability win

**Example:**
```python
class Exercise(BaseModel):
    enunciado: str
    resposta: str
    explicacao: str

class ExerciseBatch(BaseModel):
    exercicios: list[Exercise]
```

### Pattern 3: Fail-Fast Validation

**What:** Validator returns `Result` with explicit error reasons  
**When to use:** Before trusting LLM output for downstream use  
**Trade-offs:** Extra code vs. silent bad data

## Data Flow

### Request Flow

```
User params (materia, topico, dificuldade, quantidade)
    ↓
main.py → prompts.build() → generator.generate()
    ↓
OpenAI API (Structured Output)
    ↓
Raw parsed model → validator.validate()
    ↓
Valid ExerciseBatch JSON → stdout / caller
```

### State Management

No persistent state in MVP. Future MySQL layer sits after validation:

```
Validator OK → repository.save() → MySQL
```

### Key Data Flows

1. **Generation:** Request dict → formatted prompt → API → Pydantic parse
2. **Validation:** Parsed object → check count/fields → pass or retry/error
3. **Retry (optional):** Validation error message → appended to prompt → regenerate (max 2)

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Single developer / CLI | Monolith modules sufficient |
| Small web API | Add FastAPI layer; reuse generator/validator |
| Multi-tenant SaaS | Add auth, rate limiting, async job queue |

### Scaling Priorities

1. **First bottleneck:** LLM latency/cost — cache by topic+difficulty hash if needed
2. **Second bottleneck:** DB writes when MySQL added — connection pooling

## Anti-Patterns

### Anti-Pattern 1: God Module

**What people do:** Put prompts, API calls, validation in `main.py`  
**Why it's wrong:** Untestable, hard to evolve  
**Do this instead:** One responsibility per file (AGENT.md)

### Anti-Pattern 2: Trusting LLM Output

**What people do:** Return API response directly to user  
**Why it's wrong:** Wrong count, empty fields, hallucinated format  
**Do this instead:** Always run validator; optional retry

### Anti-Pattern 3: Premature Agent Framework

**What people do:** LangChain agent for "generate exercises"  
**Why it's wrong:** Single-step task doesn't need agent loop  
**Do this instead:** Direct completion until multi-step decisions needed

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| OpenAI API | Sync `chat.completions.parse` | Set timeout; handle rate limits |
| MySQL (future) | SQLAlchemy or raw connector | After schema stable |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| main ↔ generator | Function call + typed request | No business logic in generator |
| generator ↔ validator | Pydantic model or dict | Validator has no API knowledge |

## Sources

- AGENT.md — prescribed module boundaries
- OpenAI Structured Outputs — schema-first parsing
- Pipeline architecture for LLM apps (2025–2026 best practices)

---
*Architecture research for: math exercise AI generator*
*Researched: 2026-09-01*
