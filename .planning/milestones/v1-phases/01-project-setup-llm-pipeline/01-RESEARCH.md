# Phase 1: Project Setup & LLM Pipeline - Research

**Researched:** 2026-09-01  
**Domain:** Python LLM Integration, Structured Outputs, Pydantic v2, CLI Pipeline  
**Confidence:** HIGH  

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Usar OpenAI API com Structured Outputs (`chat.completions.parse` + Pydantic) — **Reversibility:** costly — trocar provider exige refatorar `generator.py`
- **D-02:** Modelo padrão `gpt-4o-mini` (custo baixo, suporta schema strict) — **Reversibility:** reversible
- **D-03:** Variável de ambiente `LLM_API_KEY` via `python-dotenv` — **Reversibility:** reversible
- **D-04:** Pydantic v2 para `Exercise`, `ExerciseBatch`, `GenerationRequest` — **Reversibility:** costly — models são contrato central
- **D-05:** Campos em português no JSON de saída: `enunciado`, `resposta`, `explicacao`, `exercicios` — **Reversibility:** one-way — contrato público de saída
- **D-06:** `dificuldade` como enum: `facil`, `medio`, `dificil` — **Reversibility:** reversible
- **D-07:** Código em diretório `exercise-ai/` na raiz do repositório conforme AGENT.md — **Reversibility:** reversible
- **D-08:** Arquivos: `main.py`, `generator.py`, `validator.py` (stub mínimo), `prompts.py`, `models.py`, `requirements.txt`, `.env.example`, `README.md` — **Reversibility:** reversible
- **D-09:** `validator.py` nesta fase pode ser pass-through ou validação mínima inline em `main.py`; validação completa é Fase 2 — **Reversibility:** reversible
- **D-10:** Entrada hardcoded/demonstração em `main.py` para MVP (exemplo do AGENT.md: equação 1º grau, fácil, quantidade 3) — **Reversibility:** reversible
- **D-11:** Saída: JSON impresso em stdout — **Reversibility:** reversible
- **D-12:** argparse fica para v2 (RELY/CLI-04) — **Reversibility:** reversible
- **D-13:** Template centralizado em `prompts.py` com instruções em português — **Reversibility:** reversible
- **D-14:** Prompt exige quantidade exata, tópico restrito, somente JSON — **Reversibility:** reversible
- **D-15:** Tratar ausência de API key e erros de API no `generator.py`/`main.py` com mensagens claras — **Reversibility:** reversible
- **D-16:** Não silenciar exceções — **Reversibility:** reversible

### the agent's Discretion
- Escolha de timeout do cliente HTTP (recomendado: 30s) e mensagens de erro exatas
- Se `validator.py` faz pass-through ou checagem mínima de tipo até Fase 2

### Deferred Ideas (OUT OF SCOPE)
- Validação estrutural completa com testes → Fase 2
- Retry automático (1–2 tentativas) → v2 / Fase 2+
- argparse CLI → v2
- Validação matemática → milestone futuro
- MySQL, analytics, agente → roadmap v2+
</user_constraints>

<architectural_responsibility_map>
## Architectural Responsibility Map

Single-tier application (CLI / Local Pipeline) — all capabilities reside in Application / CLI tier.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Project Scaffolding & Config | Application / CLI | OS Environment | Loads `.env` via `python-dotenv`, enforces `.gitignore` |
| Data Contract Models | Models (`models.py`) | Application | Defines Pydantic schemas for request, exercises, and batch |
| Prompt Construction | Prompts (`prompts.py`) | Generator | Centralizes localized prompt templates for math exercise generation |
| LLM API Invocation | Generator (`generator.py`) | External API (OpenAI) | Communicates with OpenAI SDK using Structured Outputs |
| Initial Validation Stub | Validator (`validator.py`) | Application | Minimal pass-through / type check before full validation in Phase 2 |
| Orchestration & CLI Output | Main (`main.py`) | stdout | Top-level execution, error handling, formatting JSON output |
</architectural_responsibility_map>

<research_summary>
## Summary

Phase 1 establishes the core foundation of the *Gerador de Exercícios com IA* project. The objective is to build a clean, modular Python application inside `exercise-ai/` capable of taking generation parameters (`materia`, `topico`, `dificuldade`, `quantidade`), formatting a Portuguese prompt, calling the OpenAI API using Structured Outputs (`client.beta.chat.completions.parse` with Pydantic v2), and outputting valid structured JSON to `stdout`.

To guarantee reliability without complex agent frameworks (strictly following `AGENT.md`), the architecture uses a deterministic linear pipeline: `main.py` -> `prompts.py` -> `generator.py` -> OpenAI API -> `models.py` (`ExerciseBatch`) -> `validator.py` (stub) -> `stdout`. Configuration is loaded securely from `.env` using `python-dotenv` with the key name `LLM_API_KEY`.

Key recommendations for Phase 1 include:
1. Use Pydantic v2 models with Brazilian Portuguese field names (`enunciado`, `resposta`, `explicacao`, `exercicios`) matching project requirements exactly.
2. Utilize OpenAI Structured Outputs with `model="gpt-4o-mini"` to guarantee strict JSON schema compliance natively without fragile regex or markdown stripping.
3. Keep module responsibilities strictly isolated: `generator.py` only talks to the API, `prompts.py` only formats text, `models.py` only defines schemas, and `main.py` orchestrates the flow.
4. Implement baseline error handling for missing API keys, network issues, timeouts, and API refusals without silencing exceptions.

**Primary recommendation:** Implement modular components inside `exercise-ai/` using Pydantic v2 data models and OpenAI Structured Outputs (`client.beta.chat.completions.parse`), loading `LLM_API_KEY` from `.env`, and displaying formatted JSON output with Portuguese UTF-8 characters preserved.
</research_summary>

<standard_stack>
## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | ≥3.11 (tested on 3.14) | Runtime | Modern type annotations, performance, standard library support |
| openai | ≥1.50.0 | LLM Client SDK | Official OpenAI client providing native Structured Outputs via `chat.completions.parse` / `beta.chat.completions.parse` |
| pydantic | ≥2.0.0 | Schema & Data Models | Industry standard for Python validation and strict JSON schema generation for OpenAI |
| python-dotenv | ≥1.0.0 | Configuration | Loads environment variables from `.env` without exposing secrets |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | ≥8.0.0 | Unit Testing | Development dependency for Phase 2 & 3 validator tests |
| json (stdlib) | — | JSON Serialization | Printing formatted JSON to stdout with `ensure_ascii=False` |
| enum (stdlib) | — | Enumerations | Defining allowed difficulty levels (`facil`, `medio`, `dificil`) |
| pathlib / os (stdlib) | — | File/Path resolution | Reliable `.env` path resolution across execution directories |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `openai` SDK Structured Outputs | `requests` / `httpx` raw HTTP + manual parsing | Manual parsing requires handling JSON markdown wrapping, schema validation, and tool format boilerplate manually. SDK `.parse()` is strict, typed, and maintained. |
| Pydantic v2 | Standard library `dataclasses` / `TypedDict` | `dataclasses` lack native strict JSON schema extraction compatible with OpenAI Structured Outputs without extra libraries. |
| `LLM_API_KEY` variable | `OPENAI_API_KEY` default SDK variable | `LLM_API_KEY` is explicitly required by `AGENT.md` to remain provider-agnostic and explicit in config. |

**Installation (`requirements.txt`):**
```text
openai>=1.50.0
pydantic>=2.0.0
python-dotenv>=1.0.0
pytest>=8.0.0
```
</standard_stack>

<architecture_patterns>
## Architecture Patterns

### System Architecture Diagram

```
                ┌──────────────────────────────────────────────┐
                │             CLI / Entry (main.py)            │
                └──────────────────────┬───────────────────────┘
                                       │
                         1. Load Config (.env)
                         2. Define Demo GenerationRequest
                                       │
                                       ▼
                     ┌────────────────────────────────────┐
                     │         prompts.py                 │
                     │  - build_exercise_prompt(request)  │
                     └─────────────────┬──────────────────┘
                                       │ Returns (system_prompt, user_prompt)
                                       ▼
                     ┌────────────────────────────────────┐
                     │         generator.py               │
                     │  - generate_exercises(request)     │
                     └─────────────────┬──────────────────┘
                                       │ Calls OpenAI API
                                       ▼
                     ┌────────────────────────────────────┐
                     │    External OpenAI API (gpt-4o-mini│
                     │    response_format=ExerciseBatch)  │
                     └─────────────────┬──────────────────┘
                                       │ Returns Parsed ExerciseBatch
                                       ▼
                     ┌────────────────────────────────────┐
                     │         validator.py               │
                     │  - validate_batch(batch, request)  │ (Stub / Pass-through in Phase 1)
                     └─────────────────┬──────────────────┘
                                       │ Returns Valid Batch or Error
                                       ▼
                     ┌────────────────────────────────────┐
                     │      main.py: Print JSON (stdout)  │
                     └────────────────────────────────────┘
```

### Recommended Project Structure

```text
exercise-ai/
├── main.py              # CLI entry point, demo input, orchestration, error handling
├── generator.py         # LLM API client wrapper with Structured Outputs
├── validator.py         # Validator stub (Phase 1 pass-through; Phase 2 full implementation)
├── prompts.py           # Portuguese prompt templates and builder functions
├── models.py            # Pydantic models (Exercise, ExerciseBatch, GenerationRequest, DificuldadeEnum)
├── requirements.txt     # Python dependencies
├── .env.example         # Template for environment variables (LLM_API_KEY=)
├── .gitignore           # Ignores .env, __pycache__, .pytest_cache
└── README.md            # Setup and execution instructions
```

### Pattern 1: Pydantic v2 Models for Strict Schema Integration
**What:** Define structured contracts using Pydantic `BaseModel` and `str, Enum` for OpenAI Structured Outputs.
**When to use:** Defining input requests and output exercise formats.
**Example:**
```python
from enum import Enum
from pydantic import BaseModel, Field


class DificuldadeEnum(str, Enum):
    FACIL = "facil"
    MEDIO = "medio"
    DIFICIL = "dificil"


class GenerationRequest(BaseModel):
    materia: str = Field(default="Matemática", description="Matéria dos exercícios")
    topico: str = Field(..., description="Tópico específico da matéria")
    dificuldade: DificuldadeEnum = Field(..., description="Nível de dificuldade")
    quantidade: int = Field(..., gt=0, description="Quantidade exata de exercícios a gerar")


class Exercise(BaseModel):
    enunciado: str = Field(..., description="Texto do problema ou questão matemática")
    resposta: str = Field(..., description="Resposta final ou solução direta")
    explicacao: str = Field(..., description="Passo a passo ou justificativa da resolução")


class ExerciseBatch(BaseModel):
    exercicios: list[Exercise] = Field(..., description="Lista contendo todos os exercícios gerados")
```

### Pattern 2: Generator with Structured Parsing & Error Boundaries
**What:** Use `client.beta.chat.completions.parse` with explicit model parameter, timeout, and custom error translation.
**When to use:** Inside `generator.py`.
**Example:**
```python
import os
from openai import OpenAI, OpenAIError
from models import ExerciseBatch, GenerationRequest
import prompts


def get_openai_client() -> OpenAI:
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise ValueError(
            "Chave de API não encontrada. Defina a variável LLM_API_KEY no arquivo .env."
        )
    return OpenAI(api_key=api_key, timeout=30.0)


def generate_exercises(request: GenerationRequest) -> ExerciseBatch:
    client = get_openai_client()
    system_prompt, user_prompt = prompts.build_prompts(request)

    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=ExerciseBatch,
        )
        
        message = completion.choices[0].message
        if message.refusal:
            raise RuntimeError(f"O modelo recusou a geração: {message.refusal}")
            
        if message.parsed is None:
            raise RuntimeError("O modelo não retornou uma estrutura de dados válida.")

        return message.parsed

    except OpenAIError as exc:
        raise RuntimeError(f"Erro na comunicação com a API da OpenAI: {exc}") from exc
```

### Pattern 3: Template Centralization in `prompts.py`
**What:** Isolate all system instructions and user prompt formatting from execution code.
**When to use:** Inside `prompts.py`.
**Example:**
```python
from models import GenerationRequest

SYSTEM_PROMPT = (
    "Você é um gerador especializado de exercícios educacionais de matemática. "
    "Sua função é gerar exercícios claros, corretos e adequados ao nível de dificuldade solicitado. "
    "Você deve retornar estritamente a estrutura solicitada, sem nenhum texto introdutório ou conclusivo."
)

USER_PROMPT_TEMPLATE = (
    "Gere exatamente {quantidade} exercício(s) de {materia}.\n"
    "Tópico: {topico}\n"
    "Dificuldade: {dificuldade}\n\n"
    "Requisitos obrigatórios:\n"
    "1. Crie exatamente a quantidade solicitada de exercícios.\n"
    "2. Todos os exercícios devem pertencer exclusivamente ao tópico indicado.\n"
    "3. Cada exercício deve conter 'enunciado', 'resposta' e 'explicacao' detalhada passo a passo.\n"
    "4. Os textos devem estar em português brasileiro e com linguagem didática."
)


def build_prompts(request: GenerationRequest) -> tuple[str, str]:
    user_prompt = USER_PROMPT_TEMPLATE.format(
        materia=request.materia,
        topico=request.topico,
        dificuldade=request.dificuldade.value if hasattr(request.dificuldade, "value") else str(request.dificuldade),
        quantidade=request.quantidade,
    )
    return SYSTEM_PROMPT, user_prompt
```

### Anti-Patterns to Avoid
- **God Module in `main.py`:** Writing prompts, API client initialization, and validation logic in `main.py`. Keep each module focused on its single responsibility.
- **Unstructured Prompting (`json.loads` on free text):** Relying solely on prompt wording to output JSON without Structured Outputs. This frequently produces markdown backticks (`` ```json ``) and invalid syntax.
- **Silent Exception Swallowing:** Using `except Exception: pass` or returning `None` without logging or raising actionable error messages.
- **Hardcoded Secrets:** Writing API keys into `.py` files or committing `.env` to git.
- **ASCII Escaping in Output:** Using `json.dumps()` without `ensure_ascii=False`, which renders Portuguese characters as `\u00e7\u00e3o`.
</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON Schema extraction | Manual JSON Schema dictionaries | Pydantic v2 `BaseModel` + OpenAI `.parse()` | OpenAI Structured Outputs requires strict JSON schema compliance (no optional fields without null, `additionalProperties: false`). Pydantic models automatically produce valid strict schemas. |
| Environment variable loading | Custom `.env` line parser | `python-dotenv` (`load_dotenv()`) | Custom parsers fail on quotes, comments, multiline values, and whitespace. |
| API Communication & Retries | Raw `urllib` / `requests` calls | `openai.OpenAI` SDK | Handles connection pooling, serialization, authentication headers, and Structured Output type conversion. |
| CLI JSON Formatting | String concatenation | `model.model_dump_json(indent=2)` or `json.dumps(model.model_dump(), indent=2, ensure_ascii=False)` | Custom string manipulation leads to invalid escaping and trailing commas. |

**Key insight:** LLM outputs are probabilistic, but the schema contract should not be. Using Pydantic together with OpenAI Structured Outputs shifts structural validation from fragile post-processing to schema-enforced API decoding.
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Missing API Key Configuration
**What goes wrong:** User runs `python main.py` without setting up `.env` or `LLM_API_KEY`, causing an unhandled traceback or vague crash.
**Why it happens:** Missing defensive validation before client instantiation.
**How to avoid:** Check `os.getenv("LLM_API_KEY")` explicitly before invoking the client; display a clear error message instructing how to copy `.env.example` to `.env` and fill the key.
**Warning signs:** `openai.OpenAIError: The api_key client option must be set` traceback seen in console.

### Pitfall 2: Working Directory `.env` Resolution
**What goes wrong:** Running `python exercise-ai/main.py` from repository root fails to load `.env` if `.env` is located inside `exercise-ai/` (or vice-versa).
**Why it happens:** Default `load_dotenv()` looks only in current working directory `cwd`.
**How to avoid:** Use `Path(__file__).resolve().parent / ".env"` or `find_dotenv()` to locate `.env` relative to the script directory or root.
**Warning signs:** `LLM_API_KEY` is present in file but `os.getenv("LLM_API_KEY")` returns `None`.

### Pitfall 3: Model Refusal Handling
**What goes wrong:** If a prompt triggers content moderation or refusal, `message.parsed` is `None` and attempting to access fields raises an `AttributeError`.
**Why it happens:** OpenAI Structured Outputs populates `message.refusal` instead of `message.parsed` when the model refuses.
**How to avoid:** Check `if message.refusal:` immediately after obtaining completion choices and raise an explicit descriptive error.
**Warning signs:** `TypeError: 'NoneType' object is not subscriptable` or `AttributeError: 'NoneType' object has no attribute 'exercicios'`.

### Pitfall 4: Unicode Escaping in Portuguese Output
**What goes wrong:** The CLI prints `{"enunciado": "Resolva a equa\u00e7\u00e3o..."}` instead of `{"enunciado": "Resolva a equação..."}`.
**Why it happens:** Default `json.dumps` sets `ensure_ascii=True`.
**How to avoid:** Use `json.dumps(batch.model_dump(), indent=2, ensure_ascii=False)` or print UTF-8 formatted JSON.
**Warning signs:** Unicode escape sequences `\uXXXX` in terminal output.

### Pitfall 5: Model Selection Incompatibility
**What goes wrong:** Setting `model="gpt-3.5-turbo"` fails when calling `.parse()` with `response_format`.
**Why it happens:** Older models do not support `strict: true` Structured Outputs.
**How to avoid:** Pin default model to `gpt-4o-mini` (or `gpt-4o-2024-08-06`).
**Warning signs:** API error stating `response_format of type json_schema is not supported with this model`.
</common_pitfalls>

<code_examples>
## Code Examples

### 1. `exercise-ai/models.py`
```python
"""Data models for exercise generation."""

from enum import Enum
from pydantic import BaseModel, Field


class DificuldadeEnum(str, Enum):
    FACIL = "facil"
    MEDIO = "medio"
    DIFICIL = "dificil"


class GenerationRequest(BaseModel):
    """Input parameters for exercise generation."""
    materia: str = Field(default="Matemática", description="Matéria dos exercícios")
    topico: str = Field(..., description="Tópico específico da matéria")
    dificuldade: DificuldadeEnum = Field(..., description="Nível de dificuldade")
    quantidade: int = Field(..., gt=0, description="Quantidade de exercícios a serem gerados")


class Exercise(BaseModel):
    """Single exercise structure."""
    enunciado: str = Field(..., description="Texto do enunciado do exercício")
    resposta: str = Field(..., description="Resposta correta ou solução")
    explicacao: str = Field(..., description="Explicação passo a passo da resolução")


class ExerciseBatch(BaseModel):
    """Batch containing a list of generated exercises."""
    exercicios: list[Exercise] = Field(..., description="Lista de exercícios gerados")
```

### 2. `exercise-ai/prompts.py`
```python
"""Prompt templates for exercise generation."""

from models import GenerationRequest

SYSTEM_PROMPT = (
    "Você é um professor e especialista na criação de exercícios educacionais de matemática. "
    "Sua função é gerar exercícios didáticos, precisos e contextualizados no tópico solicitado. "
    "Respeite estritamente o nível de dificuldade e gere exatamente a quantidade de exercícios solicitada. "
    "Forneça explicações passo a passo claras e fáceis de entender. "
    "Retorne exclusivamente os dados no formato estruturado especificado."
)

USER_PROMPT_TEMPLATE = (
    "Gere exercícios de matemática com base nos seguintes parâmetros:\n"
    "- Matéria: {materia}\n"
    "- Tópico: {topico}\n"
    "- Dificuldade: {dificuldade}\n"
    "- Quantidade: {quantidade}\n\n"
    "Diretrizes:\n"
    "1. Gere exatamente {quantidade} exercício(s).\n"
    "2. Todos os exercícios devem ser exclusivamente sobre o tópico '{topico}'.\n"
    "3. Para cada exercício, forneça enunciado claro, resposta final e explicação detalhada.\n"
    "4. Utilize português brasileiro correto e formal."
)


def build_prompts(request: GenerationRequest) -> tuple[str, str]:
    """Builds (system_prompt, user_prompt) tuple from a GenerationRequest."""
    dificuldade_str = (
        request.dificuldade.value
        if hasattr(request.dificuldade, "value")
        else str(request.dificuldade)
    )
    user_prompt = USER_PROMPT_TEMPLATE.format(
        materia=request.materia,
        topico=request.topico,
        dificuldade=dificuldade_str,
        quantidade=request.quantidade,
    )
    return SYSTEM_PROMPT, user_prompt
```

### 3. `exercise-ai/generator.py`
```python
"""LLM Generator using OpenAI Structured Outputs."""

import os
from openai import OpenAI, OpenAIError
from models import ExerciseBatch, GenerationRequest
import prompts


def get_client() -> OpenAI:
    """Initializes OpenAI client with LLM_API_KEY from environment."""
    api_key = os.getenv("LLM_API_KEY")
    if not api_key or not api_key.strip():
        raise ValueError(
            "Chave de API não configurada. Defina a variável LLM_API_KEY no arquivo .env."
        )
    return OpenAI(api_key=api_key.strip(), timeout=30.0)


def generate_exercises(request: GenerationRequest, model: str = "gpt-4o-mini") -> ExerciseBatch:
    """Generates exercises via OpenAI Structured Outputs."""
    client = get_client()
    system_prompt, user_prompt = prompts.build_prompts(request)

    try:
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=ExerciseBatch,
        )

        message = completion.choices[0].message

        if message.refusal:
            raise RuntimeError(f"O modelo recusou a geração: {message.refusal}")

        if message.parsed is None:
            raise RuntimeError("Não foi possível obter a estrutura de exercícios da resposta do modelo.")

        return message.parsed

    except OpenAIError as exc:
        raise RuntimeError(f"Erro na chamada à API da OpenAI: {exc}") from exc
```

### 4. `exercise-ai/validator.py` (Phase 1 Stub)
```python
"""Validator module for exercises.

Phase 1 provides a baseline validation stub / pass-through.
Full validation (count checks, field emptiness, tests) is expanded in Phase 2.
"""

from models import ExerciseBatch, GenerationRequest


def validate_exercise_batch(batch: ExerciseBatch, request: GenerationRequest) -> ExerciseBatch:
    """Validates the generated exercise batch.
    
    Phase 1: Verifies basic batch structure and non-empty list.
    Phase 2: Comprehensive validation with detailed error reason codes.
    """
    if not isinstance(batch, ExerciseBatch):
        raise ValueError("O lote retornado não é uma instância válida de ExerciseBatch.")
    
    if not batch.exercicios:
        raise ValueError("A lista de exercícios retornada está vazia.")

    return batch
```

### 5. `exercise-ai/main.py`
```python
"""CLI entry point for exercise generation."""

import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env in exercise-ai/ or project root
env_path = Path(__file__).resolve().parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from models import DificuldadeEnum, GenerationRequest
from generator import generate_exercises
from validator import validate_exercise_batch


def run_demo() -> None:
    """Executes the standard demo generation flow."""
    # Demo request per AGENT.md specification
    request = GenerationRequest(
        materia="Matemática",
        topico="Equação do primeiro grau",
        dificuldade=DificuldadeEnum.FACIL,
        quantidade=3,
    )

    try:
        # Step 1: Generate via LLM
        batch = generate_exercises(request)

        # Step 2: Validate batch (Phase 1 baseline)
        validated_batch = validate_exercise_batch(batch, request)

        # Step 3: Print formatted JSON output
        output_json = json.dumps(
            validated_batch.model_dump(),
            indent=2,
            ensure_ascii=False,
        )
        print(output_json)

    except ValueError as val_err:
        print(f"Erro de configuração ou validação: {val_err}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as run_err:
        print(f"Erro na execução da geração: {run_err}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Erro inesperado: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_demo()
```
</code_examples>

<sota_updates>
## State of the Art (2024-2026)

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Prompt-only JSON instructions (`"return JSON only"`) | OpenAI Structured Outputs (`response_format=PydanticModel` with `strict: true`) | August 2024 (OpenAI SDK v1.40+) | Eliminates markdown wrapping, JSON decode errors, and key hallucination |
| Pydantic v1 (`.dict()`, `.json()`, `class Config`) | Pydantic v2 (`.model_dump()`, `.model_dump_json()`, `model_config`) | 2023–2024 | Faster serialization, strict typing support, official SDK compatibility |
| Hardcoded environment keys or generic `OPENAI_API_KEY` | Explicit `.env` management with `python-dotenv` | Standard practice | Secure separation of credentials, portable between environments |

**New tools/patterns to consider:**
- `client.beta.chat.completions.parse`: Native OpenAI helper that combines JSON schema extraction from Pydantic and response parsing into a single call.
- `model_dump(mode='json')` / `model_dump_json()`: Standard Pydantic v2 dump methods ensuring datetime/enum conversion.

**Deprecated/outdated:**
- `response_format={"type": "json_object"}`: Deprecated in favor of typed strict JSON schema when schema is known.
- Manual regex extraction (`re.search(r'\{.*\}', text, re.DOTALL)`): Unnecessary when using Structured Outputs.
</sota_updates>

<open_questions>
## Open Questions

1. **OpenAI SDK Method Syntax (`beta.chat.completions.parse` vs `chat.completions.parse`)**
   - What we know: In OpenAI Python SDK (1.40+ through 1.50+), `client.beta.chat.completions.parse()` is the canonical entry point for Structured Outputs with Pydantic models.
   - What's unclear: In some future SDK versions, `beta` methods may graduate to root namespace.
   - Recommendation: Use `client.beta.chat.completions.parse()`, which is fully supported and stable across `openai>=1.50.0`.

2. **Execution Context Pathing**
   - What we know: Users may run `python main.py` from inside `exercise-ai/` or `python exercise-ai/main.py` from repository root.
   - Recommendation: Use `Path(__file__).resolve().parent` to resolve `.env` and imports reliably regardless of working directory.
</open_questions>

<sources>
## Sources

### Primary (HIGH confidence)
- OpenAI Structured Outputs Official Documentation & Cookbook (`response_format`, `strict: true`, Pydantic `.parse()`)
- Pydantic v2 Official Documentation (BaseModel, Field, Enum serialization)
- `AGENT.md` (Project specification, folder layout, input/output contract, and constraints)
- `.planning/phases/01-project-setup-llm-pipeline/01-CONTEXT.md` (User decisions and scope boundaries)

### Secondary (MEDIUM confidence)
- Python 3.11+ / 3.14 typing and stdlib conventions
- `python-dotenv` documentation for multi-directory dotenv discovery

### Tertiary (LOW confidence - needs validation)
- None — all patterns are established and verified against official documentation.
</sources>

<metadata>
## Metadata

**Research scope:**
- Core technology: Python 3.11+, OpenAI SDK (`openai>=1.50.0`), Pydantic v2 (`pydantic>=2.0.0`), `python-dotenv`
- Ecosystem: CLI pipeline, prompt management, environment variable configuration
- Patterns: Structured Outputs parsing, linear orchestration pipeline, modular architecture
- Pitfalls: Missing API keys, Unicode formatting, refusal handling, path resolution

**Confidence breakdown:**
- Standard stack: HIGH — pinned, standard modern Python AI stack
- Architecture: HIGH — directly conforms to `AGENT.md` and user decisions
- Pitfalls: HIGH — well-known failure modes documented with preventative patterns
- Code examples: HIGH — verified syntax for Pydantic v2 and OpenAI SDK

**Research date:** 2026-09-01  
**Valid until:** 2026-10-01  
</metadata>

---

*Phase: 01-project-setup-llm-pipeline*  
*Research completed: 2026-09-01*  
*Ready for planning: yes*  
