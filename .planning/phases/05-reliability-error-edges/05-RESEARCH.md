# Phase 5: Reliability & Error Edges - Research

**Researched:** 2026-09-08  
**Domain:** Limited regeneration after retriable failures, aggregated LLM duration logging, unified API edge errors (ERR-05 / WR-03 / WR-04)  
**Confidence:** HIGH  

## User Constraints

### Locked Decisions
- **D-01:** Default de regenerações via env `RELY_MAX_RETRIES`; override por CLI `--max-retries` — **Reversibility:** costly — vira contrato público CLI/README/.env.example
- **D-02:** Hierarquia **CLI > env > default**; se env ausente, default **`1`** regeneração
- **D-03:** Semântica do valor = **número de regenerações após a primeira tentativa** (não o total de chamadas LLM). Total LLM = `1 + N`
- **D-04:** Faixa válida **`0|1|2|3`** para CLI e env (`0` = fail-fast como v1 Phase 2). Amplia o teto textual do PROJECT “1–2” para permitir até **3** regenerações
- **D-05:** Regenerar em: falha de **validação estrutural** (`ValueError` do validator) e **resposta LLM inválida/parse** (ex. empty `choices`, parsed None, unparseable após ERR-05)
- **D-06:** **Não** regenerar em erros “permanentes” de API: auth, timeout, rate-limit (e equivalentes mapeados)
- **D-07:** O loop desta fase é o **hook** que Phase 6 (math) deve reusar — falha matemática futura entra no mesmo caminho — **Reversibility:** costly — contrato entre fases 5 e 6
- **D-08:** Módulo dedicado (ex. `exercise-ai/reliability.py`); `main` apenas orquestra (chama o wrapper; argparse/`--out`/texto permanecem em `main`) — **Reversibility:** costly — novo módulo no boundary do pipeline
- **D-09:** Não colocar o loop em `generate_exercises` nem no `validator`
- **D-10:** Em toda regeneração, usar o **mesmo prompt** da primeira tentativa — **não** alterar `prompts.py` nesta fase
- **D-11:** Prompt “repair” / apêndice com erro de validação → **deferred** para milestone futuro (se precisar)
- **D-12:** Stderr mostra o fluxo: `Gerando…` → `Validando…`; em regeneração: **`1ª Regeneração`**, **`2ª Regeneração`**, … (contagem a partir das regenerações, não da 1ª tentativa)
- **D-13:** Mensagem de **erro** (motivo da falha) só quando as tentativas/regenerações **esgotarem** — PT clara com o último motivo
- **D-14:** **Stdout** (texto D-15 Phase 4) e escrita **`--out`** somente no **sucesso final**
- **D-15:** LOG-01 de desenvolvimento pode continuar (sem segredos), sem substituir o contrato de UX acima
- **D-16:** Log **agregado no fim** (sucesso ou falha final): duração total + número de chamadas LLM (ex. `total_ms` / equivalente e `chamadas=N`) — sem obrigação de logar duração por chamada intermediária nesta fase
- **D-17:** Sem segredos no log (alinha LOG-02)
- **D-18:** Empty OpenAI `choices` / parsed ausente / unparseable e falhas Gemini fora de `APIError` usam o **mesmo caminho tipado** (RuntimeError PT + detalhe `[API:openai|gemini]` sanitizado)
- **D-19:** Esses edges contam como **resposta inválida → retriáveis** (D-05); auth/timeout/rate-limit permanecem não retriáveis (D-06)
- **D-20:** Preferir helpers/mapper unificados + testes parametrizados cobrindo WR-03 e WR-04
- **D-21:** Documentar `RELY_MAX_RETRIES` e `--max-retries` no README e `.env.example` (nomes sem valores secretos)
- **D-22:** Preservar contrato Phase 4: dual-output texto + `--out`; não regressar para JSON-only stdout

### Discretion
- Nome exato do módulo (`reliability.py` vs `retry.py`) e formulação precisa das strings PT de regeneração/duração — planner/executor
- Unidade de duração (`ms` vs `s`) desde que agregada e sem segredos

### Deferred Ideas
- Estruturação de prompt / apêndice de erro / “repair prompt” na regeneração — milestone futuro
- Provider failover automático — já fora de v1.1
- Validação matemática — Phase 6 (reusa hook RELY)
- Duração por chamada intermediária — não exigida por D-16 nesta fase

## Standard Stack

**Phase 5 adds no new pip packages.** [VERIFIED: PROJECT.md Constraints + CONTEXT D-08/D-21 — stdlib + existing deps only]

### Already in project (do not reinstall for this phase)

| Library | Role in Phase 5 | Notes |
|---------|-----------------|-------|
| Python 3.11+ | Runtime | Typing, `Path`, exception groups unused |
| argparse | CLI `--max-retries` | Already used in `main.build_parser()` [VERIFIED: exercise-ai/main.py:105-150] |
| python-dotenv / `os.getenv` | `RELY_MAX_RETRIES` | Same env resolution pattern as keys |
| openai / google-genai | Unchanged generate path | Retry wraps calls; does not live inside SDKs |
| pydantic | Models unchanged | Validator still raises `ValueError` |
| pytest | Unit tests with mocks | No live LLM |

### Stdlib only for reliability work

| Module | Purpose | Why |
|--------|---------|-----|
| `time.perf_counter` | Wall duration for RELY-02 aggregate | Monotonic, no extra deps [CITED: Python docs perf_counter] |
| `logging` | Optional LOG-01 alongside UX stderr | Existing `exercise_ai` logger [VERIFIED: exercise-ai/main.py:29-56] |
| `os` | Read `RELY_MAX_RETRIES` | CLI > env > default (D-02) |
| `sys` | Stage/error lines on stderr | Match Phase 4 UX |

### Explicitly out of stack for Phase 5

| Avoid | Why |
|-------|-----|
| tenacity / backoff / retry libs | YAGNI; N∈{0..3}; hand loop in `reliability.py` (D-08) |
| New exception hierarchy packages | Keep `ValueError` / `RuntimeError` contract |
| Prompt-repair frameworks | Contradicts D-10 / D-11 |
| Provider failover libs | Deferred / out of v1.1 |

## Architecture Patterns

### Target pipeline (Phase 5)

```
main (argparse, --out, format_batch_text, exit codes)
  └─ reliability.generate_validated_batch(request, max_retries, …)
       ├─ for attempt in 0..max_retries:
       │    ├─ UX: "Gerando…" | "Nª Regeneração" then "Validando…"
       │    ├─ batch = generate_exercises(request)   # same prompt via prompts.build_prompts
       │    └─ return validate_exercise_batch(batch, request)
       ├─ classify: retriable vs permanent → break or continue
       └─ finally/end: log aggregate duration + chamadas=N (D-16)
main writes stdout text + --out JSON only after success (D-14)
```

[CITED: CONTEXT D-08, D-09, D-10, D-12–D-16]  
[VERIFIED current fail-fast loop: exercise-ai/main.py:153-196]

### Module boundary (D-08 / D-09)

| Module | Owns | Must NOT own |
|--------|------|--------------|
| `reliability.py` (preferred name; discretion allows `retry.py`) | Retry count resolution helpers optional; loop; retriable classification; stage labels for regen; aggregate timing | argparse, `--out` write, `format_batch_text`, exit codes |
| `main.py` | CLI, resolve max_retries, call reliability wrapper, dual-output, catch final errors → stderr + exit 1 | Retry loop body |
| `generator.py` / `generator_gemini.py` | Single LLM call; ERR-05 typed edges; mappers | Retry / sleep / max_retries |
| `validator.py` | Structural checks → `ValueError` | Retry |
| `prompts.py` | Unchanged | Repair appendices (D-11 deferred) |

**Phase 6 hook (D-07):** Prefer a single entry like `generate_validated_batch(...)` that always runs generate → validate. Phase 6 adds math checks either inside `validate_exercise_batch` (still `ValueError`) or as a post-step that raises the same retriable type — reliability loop stays unchanged.

### Retriable vs permanent (D-05 / D-06 / D-19)

| Signal | Today | Phase 5 | Retry? |
|--------|-------|---------|--------|
| Validator structural fail | `ValueError` [VERIFIED: validator.py:62-65] | Catch in reliability | Yes |
| OpenAI empty `choices` | `IndexError` → bare `Exception` in main [VERIFIED: generator.py:112; 02-REVIEW WR-03] | Guard → PT `RuntimeError` + `[API:openai]` | Yes (invalid response) |
| OpenAI `parsed is None` / unparseable Gemini | Already PT `RuntimeError` [VERIFIED: generator.py:122-129; generator_gemini.py:128-142] | Keep; mark retriable | Yes |
| Gemini non-`APIError` transport | Unmapped → generic main [VERIFIED: generator_gemini.py:125-126; WR-04] | Broaden map → PT `RuntimeError` | **Depends:** auth/timeout/rate/conn → **No**; other invalid/empty-like → **Yes** |
| Auth / timeout / rate-limit / connection (mapped) | PT `RuntimeError` via mappers [VERIFIED: generator.py:75-91; generator_gemini.py:88-104] | Detect as permanent | No |
| Missing API key / config | `ValueError` before LLM [VERIFIED: main.py:_ensure_provider_key; generator missing-key] | Not a regen case; fail immediately | No |

**Classification strategy (plan-ready):** Do not retry every `RuntimeError`. Prefer:

1. **Marker / helper** on invalid-response paths (e.g. raise via `invalid_llm_response(msg)` that sets an attribute, or a small dedicated exception subclass of `RuntimeError` still printed as plain PT) — keeps D-18 user message shape; OR
2. **Message/needle allowlist** for known invalid-response PT strings — fragile; less preferred than (1).

Permanent API errors: either subclass/`PermanentApiError` marker from mappers, or classify by known PT message constants / exception type before mapping. Planner should pick one approach and use it consistently for OpenAI + Gemini (D-20).

**Critical:** Config `ValueError` (missing key) must not enter the regen path even though validator also uses `ValueError`. Options: (a) only retry `ValueError` raised *after* a successful `generate_exercises` return inside the loop; (b) separate exception type for validation (Phase 6-friendly). Option (a) matches current code with least churn: catch generate errors and validate errors separately inside the attempt.

### Retry counting (D-01–D-04)

```
max_retries = CLI --max-retries  if set
           else int(env RELY_MAX_RETRIES) if set
           else 1
assert max_retries in {0,1,2,3}

LLM calls allowed = 1 + max_retries
# attempt 0: first generation (no "Nª Regeneração")
# attempts 1..max_retries: print "1ª Regeneração", "2ª Regeneração", …
```

`0` = Phase 2 fail-fast (one generate+validate, then surface error). Aligns ROADMAP “1–2” success criteria as default `1` with headroom to `3` per D-04. [CITED: ROADMAP Phase 5 SC1; REQUIREMENTS RELY-01]

### UX / I/O (D-12–D-15, D-22)

- First attempt: `Gerando…` then `Validando…` (same strings as today) [VERIFIED: main.py:167-171]
- Before each regen LLM call: `1ª Regeneração` / `2ª Regeneração` / … then again `Gerando…`/`Validando…` or regen label replacing the first-stage label — discretion on exact pairing; spirit is regen ordinal ≠ “Tentativa 1” for first try [CITED: CONTEXT Specifics]
- Do **not** print user-facing failure reason until loop exhausts (D-13). Ops `[VALIDAÇÃO]` / `[API:*]` from existing modules may still fire on intermediate fails (D-15 / LOG-01); that is detail layer, not the final plain PT error line from `main`
- `format_batch_text` + `out.write_text` stay in `main` **after** reliability returns success only [VERIFIED success write: main.py:173-182]

### Duration log (RELY-02 / D-16 / D-17)

- Start `perf_counter` when reliability loop starts (or first generate); stop on exit (success or final failure)
- Increment `chamadas` once per `generate_exercises` invocation (not per validate)
- One aggregate stderr or logger line, e.g. `duração total_ms=… chamadas=N` — no keys, no prompts, no batch JSON in that line
- Intermediate per-call timing optional / deferred [CITED: CONTEXT deferred]

### ERR-05 implementation locus

Fix edges **inside generators** (typed RuntimeError + sanitized `[API:*]`), then treat those RuntimeErrors as **retriable invalid response** in reliability (D-18/D-19). Do not leave IndexError/unmapped Exception for `main`’s bare handler [VERIFIED: main.py:193-196].

## Don't Hand-Roll

| Temptation | Use instead |
|------------|-------------|
| tenacity / exponential backoff / jitter | Fixed `for` with `max_retries`; no sleep required by CONTEXT |
| Retry inside `generate_exercises` | Wrapper in `reliability.py` (D-08/D-09) |
| Mutating prompt with last `ValueError` | Same `prompts.build_prompts(request)` every call (D-10) |
| New pip timer / metrics SDK | `time.perf_counter` + one log line |
| Rewriting dual-output to JSON stdout | Keep Phase 4 text stdout + `--out` JSON (D-22) |
| Catch-all `except Exception: retry` | Classify permanent vs retriable; re-raise permanent immediately |
| Provider failover on OpenAI fail | Out of scope / deferred |
| Silent swallow of last error | Preserve last retriable reason for D-13 final message |

## Common Pitfalls

1. **Infinite retry** — Bound by `max_retries ∈ 0..3` and a single `for`/`while` with hard stop; never `while True` without counter. Tests must assert `generate_exercises` call_count ≤ `1 + max_retries`.

2. **Retrying auth / timeout / rate-limit** — Mapped permanent API errors must abort the loop immediately (D-06). Burning retries on bad keys wastes time and confuses UX.

3. **Leaking secrets** — Keep LOG-02: `[API:*]` = type + status only; duration line must not include env values, prompts, or raw exception bodies [VERIFIED redaction helpers: generator.py:55-61, 64-72; generator_gemini.py:70-85]. Extend tests in `test_logging_security.py`.

4. **Writing `--out` (or stdout text) on failed attempts** — Intermediate validated-looking batches must not touch disk/stdout; only final success [CITED: D-14]. Current tests already assert no file on failure [VERIFIED: test_main.py:84-85] — extend for multi-attempt failure.

5. **Changing prompts on retry** — Do not edit `prompts.py` or pass error context into `build_prompts` (D-10/D-11).

6. **Treating config `ValueError` as validation retry** — Missing key before generate must exit once without regen labels.

7. **Off-by-one on regen labels** — Label `1ª Regeneração` is the **first retry**, not the initial attempt (D-03/D-12).

8. **Leaving WR-03 as IndexError** — Empty `choices` still unguarded [VERIFIED: generator.py:112]; must become typed invalid-response path before reliability can classify it.

9. **WR-04 only catching `APIError`** — Non-APIError Gemini failures still skip `map_gemini_error` [VERIFIED: generator_gemini.py:125-126]; broaden catch then classify permanent vs invalid.

## Code Examples / Skeletons

### 1. Resolve max retries (CLI > env > 1)

```python
# exercise-ai/reliability.py (or small helper used by main)
import os

_ALLOWED = frozenset({0, 1, 2, 3})
_DEFAULT = 1  # D-02


def resolve_max_retries(cli_value: int | None) -> int:
    if cli_value is not None:
        n = cli_value
    else:
        raw = os.getenv("RELY_MAX_RETRIES", "").strip()
        n = int(raw) if raw else _DEFAULT
    if n not in _ALLOWED:
        raise ValueError(
            f"max-retries inválido '{n}': use um inteiro 0, 1, 2 ou 3."
        )
    return n
```

[CITED: CONTEXT D-01–D-04]  
Argparse: add `--max-retries` with `type=int` + choices/`_positive` style validation mirroring `_positive_quantidade` [VERIFIED pattern: main.py:90-102, 105-150].

### 2. Reliability loop skeleton (D-08, D-05/D-06, D-12–D-16)

```python
# exercise-ai/reliability.py — illustrative; names discretionary
from __future__ import annotations

import sys
import time
from models import ExerciseBatch, GenerationRequest
from generator import generate_exercises
from validator import validate_exercise_batch


def is_permanent_api_error(exc: BaseException) -> bool:
    """True for auth/timeout/rate-limit/connection — do not regenerate (D-06)."""
    # Prefer explicit marker set by mappers / invalid_llm_response helper (D-20).
    return getattr(exc, "retriable", None) is False


def is_retriable_invalid_response(exc: BaseException) -> bool:
    """Empty choices / parsed None / unparseable / ERR-05 typed edges (D-05, D-19)."""
    return getattr(exc, "retriable", None) is True


def generate_validated_batch(
    request: GenerationRequest,
    max_retries: int,
) -> ExerciseBatch:
    """Hook for Phase 5 + Phase 6 (D-07). Same prompt every attempt (D-10)."""
    t0 = time.perf_counter()
    calls = 0
    last_err: BaseException | None = None

    try:
        for attempt in range(0, max_retries + 1):
            if attempt == 0:
                print("Gerando…", file=sys.stderr)
            else:
                print(f"{attempt}ª Regeneração", file=sys.stderr)
                print("Gerando…", file=sys.stderr)

            try:
                calls += 1
                batch = generate_exercises(request)
            except RuntimeError as exc:
                last_err = exc
                if is_permanent_api_error(exc):
                    raise
                if is_retriable_invalid_response(exc) and attempt < max_retries:
                    continue
                raise

            print("Validando…", file=sys.stderr)
            try:
                return validate_exercise_batch(batch, request)
            except ValueError as exc:
                last_err = exc
                if attempt < max_retries:
                    continue
                raise

        assert last_err is not None
        raise last_err
    finally:
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        # D-16 / D-17 — aggregate only; no secrets
        print(
            f"duração total_ms={elapsed_ms} chamadas={calls}",
            file=sys.stderr,
        )
```

[CITED: CONTEXT D-07–D-16]  
[VERIFIED generate/validate call sites today: main.py:167-171]

### 3. `main.run` orchestration after Phase 5

```python
# main.py — conceptual diff; keep dual-output in main (D-14, D-22)
from reliability import generate_validated_batch, resolve_max_retries

def run(request: GenerationRequest, out_path: Path | str, max_retries: int | None = None) -> None:
    _configure_logging()
    # ... existing LOG-01 params ...
    try:
        n = resolve_max_retries(max_retries)
        validated_batch = generate_validated_batch(request, max_retries=n)
        print(format_batch_text(validated_batch))
        Path(out_path).write_text(
            json.dumps(validated_batch.model_dump(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info("Geração concluída com sucesso")
    except ValueError as val_err:
        # final reason only once reliability exhausted (D-13)
        ...
```

[VERIFIED current run body: exercise-ai/main.py:153-196]

### 4. ERR-05 / WR-03 — empty OpenAI `choices`

```python
# generator._generate_with_openai — insert before choices[0]
# [VERIFIED gap: exercise-ai/generator.py:112]
if not completion.choices:
    print("[API:openai] empty choices", file=sys.stderr)
    err = RuntimeError(
        "Não foi possível obter a estrutura de exercícios da resposta do modelo."
    )
    err.retriable = True  # or raise invalid_llm_response(...)
    raise err

message = completion.choices[0].message
```

[CITED: 02-REVIEW.md WR-03; CONTEXT D-18/D-19]  
Mirror `retriable=True` on existing `parsed is None` path [VERIFIED: generator.py:122-129].

### 5. ERR-05 / WR-04 — Gemini non-`APIError`

```python
# generator_gemini.generate_exercises — broaden after APIError
# [VERIFIED narrow catch: exercise-ai/generator_gemini.py:125-126]
try:
    response = client.models.generate_content(...)
except genai_errors.APIError as exc:
    raise map_gemini_error(exc) from exc  # mapper sets retriable=False for auth/timeout/rate/conn
except Exception as exc:
    # Transport / unexpected: still typed PT path (D-18), sanitize detail
    raise map_gemini_error(exc) from exc
```

Ensure `map_gemini_error` / a sibling sets `retriable=False` for auth/timeout/rate/conn and `retriable=True` only when classifying as invalid/empty-like responses (empty text / unparseable already raise separate RuntimeErrors — mark those retriable). [CITED: CONTEXT D-18–D-20; 02-REVIEW WR-04]

### 6. Test shapes (extend existing suites)

```python
# Parametrize WR-03 / WR-04 (D-20); mock generate_exercises call_count
def test_retry_on_validation_then_success(monkeypatch, demo_batch, tmp_path):
    # side_effect: ValueError once, then good batch → call_count == 2, --out written

def test_no_retry_on_auth(monkeypatch, tmp_path):
    # RuntimeError auth (retriable=False) → call_count == 1, no "1ª Regeneração"

def test_empty_choices_typed_and_retriable():
    # completion.choices = [] → RuntimeError PT + "[API:openai] empty choices"

def test_max_retries_zero_fail_fast():
    # max_retries=0 → one call, final stderr reason, no --out
```

[VERIFIED test patterns: exercise-ai/tests/test_main.py; test_generators.py:175-217]

## Research findings (planning inputs)

1. **Loop belongs in new `reliability.py`; `main` stays dual-output owner** — Current `run` inlines generate→validate→write [VERIFIED: main.py:153-182]. Extracting the loop satisfies D-08/D-09 and gives Phase 6 a stable hook (D-07 / MATH-02). [CITED: ROADMAP Phase 6 depends on Phase 5]

2. **Retry budget is regenerations, not total attempts** — Default `1` → up to 2 LLM calls; CLI/env may set 0–3 (D-01–D-04). ROADMAP wording “1–2” is satisfied by default/policy, not by hardcoding max=2 only.

3. **ERR-05 is a generator fix + classification contract** — WR-03 still live (`choices[0]` ungarded) [VERIFIED: generator.py:112]. WR-04 still live (only `APIError` mapped) [VERIFIED: generator_gemini.py:125-126]. Both must become typed RuntimeError with sanitized `[API:*]`; invalid-response variants are retriable (D-19), permanent API categories are not (D-06).

4. **Same prompt every attempt** — `generate_exercises` already rebuilds prompts from `request` only [VERIFIED: generator.py:100; generator_gemini.py:113-114]. Reliability must not pass failure context; do not touch `prompts.py` (D-10).

5. **No new packages; argparse + env + `perf_counter` suffice** — RELY-01/02/ERR-05 are orchestration and edge mapping, not new dependencies. Document `RELY_MAX_RETRIES` / `--max-retries` in README + `.env.example` (D-21).

## Provenance legend

| Tag | Meaning |
|-----|---------|
| `[VERIFIED: path:lines]` | Confirmed by reading current source in this research pass |
| `[CITED: …]` | Taken from CONTEXT / ROADMAP / REQUIREMENTS / PROJECT / 02-REVIEW |
| `[ASSUMED: …]` | Reasonable default where CONTEXT left discretion (module name, exact duration unit string) |

---

*Phase: 5-Reliability & Error Edges*  
*Research completed: 2026-09-08*
