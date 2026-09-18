# Phase 12: Local Embed Demo - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-18
**Phase:** 12-Local Embed Demo
**Areas discussed:** Page composition, Form field set, Busy & error UX, Throwaway chrome

---

## Page composition

| Option | Description | Selected |
|--------|-------------|----------|
| Single column | Form → results → JSON stacked | |
| Split panes | Form left, results+JSON right | |
| Form + exercises primary; JSON secondary | Toggle/tab for JSON | ✓ |
| Other | Freeform | |

**User's choice:** Form + exercises primary; JSON behind toggle/tab
**Notes:** Follow-up: tabs Exercícios \| JSON (not inline toggle). Empty Exercícios + JSON schema hint before first success. PT UI + EN technical labels.

---

## Form field set

| Option | Description | Selected |
|--------|-------------|----------|
| Contract-only | Four GenerationRequest fields | |
| Contract + provider + reasoning | Env before call, like wizard | ✓ |
| Contract + reasoning only | Skip provider picker | |
| Other | Freeform | |

**User's choice:** Contract + provider + reasoning
**Notes:** Separate Contrato vs Ambiente sections. Demo-ready presets. Mirror wizard provider/reasoning selects.

---

## Busy & error UX

| Option | Description | Selected |
|--------|-------------|----------|
| Disable submit + Gerando… | Fields stay editable | ✓ |
| Disable whole form + spinner | No mid-flight edits | |
| You decide | Agent discretion | |
| Other | Freeform | |

**User's choice:** Disable submit + Gerando…
**Notes:** Badge with exception class + PT message + kind. Explicit 409 sequential-contract copy. Keep last success on later failure.

---

## Throwaway chrome

| Option | Description | Selected |
|--------|-------------|----------|
| Persistent top banner only | Single loud signal | |
| Banner + footnote | Strong banner; footer repeat | ✓ |
| You decide | Banner enough if README has expiry | |
| Other | Freeform | |

**User's choice:** Banner + footnote
**Notes:** Full anti-accretion pack in `demo/README.md`. Short pointer in root README Embed. Banner dismissible until reload; footnote stays.

---

## the agent's Discretion

- Exact preset topic string; HTML/JS file layout under `demo/`
- Schema-hint wording; badge/banner CSS
- Empty vs “auto” label for provider control

## Deferred Ideas

None from this discussion (milestone deferred items unchanged).
