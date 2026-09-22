# Phase 14: Mixed prompt + plan-adherence + demo enablement - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-22
**Phase:** 14-mixed-prompt-plan-adherence-demo-enablement
**Areas discussed:** Prompt slot list, Validator / RELY hook, Demo band UX, Demo payload shape

---

## Prompt slot list

### How to surface slots in the prompt

| Option | Description | Selected |
|--------|-------------|----------|
| Numbered list from `itens_ordenados` | Slot index → dificuldade | ✓ |
| (Other shapes explored earlier in session) | Compact prose / table | |

**User's choice:** Numbered slots from `itens_ordenados`
**Notes:** Carry-forward from early discuss answers (`1`).

### When to enumerate

| Option | Description | Selected |
|--------|-------------|----------|
| Always (incl. uniform) | Same enumeration shape always | ✓ |
| Mixed only | Uniform keeps scalar template | |

**User's choice:** Always enumerate

### Field list (`enunciado` / `resposta` / `explicacao`) in prompt

| Option | Description | Selected |
|--------|-------------|----------|
| Keep listing fields | Prompt restates output fields | |
| Drop field list | Schema/`ExerciseBatch` authority | ✓ |
| You decide | — | |

**User's choice:** Drop field list → planted/aligned **SEED-008**

### Difficulty label language

| Option | Description | Selected |
|--------|-------------|----------|
| Enum as-is | `facil` / `medio` / `dificil` | |
| Portuguese display | `fácil` / `médio` / `difícil` | |
| Hybrid | PT display + enum, e.g. `fácil (facil)` | ✓ |
| You decide | — | |

**User's choice:** `hybrid` (free-text)

---

## Validator / RELY hook

### Where `verify_plan_echo` runs

| Option | Description | Selected |
|--------|-------------|----------|
| Inside `validate_exercise_batch` before math | | |
| Inside `validate_exercise_batch` after math | | |
| Separate call in `reliability.py` | Validator stays length/math; RELY owns echo | ✓ |
| You decide | — | |

**User's choice:** 3 — reliability.py

### Order vs `validate_exercise_batch`

| Option | Description | Selected |
|--------|-------------|----------|
| Echo first | | |
| Validate first, then echo | | ✓ |
| You decide | — | |

**User's choice:** 2

### Batch `dificuldades` summary

| Option | Description | Selected |
|--------|-------------|----------|
| Slots only | | |
| Slots + summary | Fail if batch summary ≠ request | ✓ |
| You decide | — | |

**User's choice:** 2

---

## Demo band UX

### Control surface

| Option | Description | Selected |
|--------|-------------|----------|
| Three count inputs; qty = sum | Hide/lock old qty | |
| Toggle Uniform \| Misto | | |
| Always three counts | Uniform = one band | ✓ (as “three counts”; qty kept editable below) |
| You decide | — | |

**User's choice:** 1 — three count inputs (then clarified qty stays editable)

### Client validation

| Option | Description | Selected |
|--------|-------------|----------|
| Hard client guards | Block submit on sum=0 / >40 | |
| Soft warn only | POST allowed; server hard gate | ✓ |
| You decide | — | |

**User's choice:** 2

### Old select / quantidade field

| Option | Description | Selected |
|--------|-------------|----------|
| Replace — remove select; read-only live sum | | |
| Keep quantidade editable + three counts | | ✓ |
| You decide | — | |

**User's choice:** 2

---

## Demo payload shape

### When to send `plano`

| Option | Description | Selected |
|--------|-------------|----------|
| Always `plano` | Omit scalar dificuldade | |
| `plano` only when mixed | Else legacy dificuldade+qty | ✓ |
| Passthrough | Client/serve map freely | |
| You decide | — | |

**User's choice:** 2

### Uniform dificuldade source

| Option | Description | Selected |
|--------|-------------|----------|
| Derive from sole non-zero band | | ✓ |
| Always require editable qty + derived band | | |
| You decide | — | |

**User's choice:** 1

### Uniform qty vs band count mismatch

| Option | Description | Selected |
|--------|-------------|----------|
| Prefer band count in payload | Ignore form qty for POST | ✓ |
| Prefer form qty | | |
| Soft warn; POST form as-is | | |
| You decide | — | |

**User's choice:** 1

---

## Claude's Discretion

- Exact prompt template wording for slot list
- Implementation of batch-summary check (extend `verify_plan_echo` vs helper)
- Soft-warn UI copy/placement

## Deferred Ideas

- Phase 15 CLI/wizard UX-01/UX-02
- SEED-005 / SEED-007
- Hard client block on invalid totals
- Always-send-`plano` for uniform
