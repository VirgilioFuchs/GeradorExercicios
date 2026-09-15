# Phase 10 Verification — Interactive CLI Wizard

**Phase:** 10-interactive-cli-wizard  
**Plan:** 10-01  
**Verified:** 2026-09-15  
**Verifier:** gsd-verifier (generic-agent)

## Status

**passed**

## Score

**9/9** must_have truths · **4/4** artifacts · **3/3** key_links · prohibitions clean · ROADMAP success criteria 1–5 met · WIZ-01..03 + D-01..D-15 met

## Automated evidence

| Command | Result |
|---------|--------|
| `pytest exercise-ai -q` | **133 passed**, 2 warnings (pre-existing: google.genai deprecation; pydantic serializer in validator test), exit 0 (~3.1s) |

No live LLM; no real TTY required (injectable `input` / `isatty`).

## Must-have truths

| # | Truth | Result | Evidence |
|---|-------|--------|----------|
| 1 | First token `gerar` opens PT wizard on TTY; without `gerar`, argparse unchanged (D-01/02; WIZ-01/03) | **PASS** | `main.main` branches on `argv[0] == "gerar"` then `run_wizard()`; else `build_parser().parse_args`; `test_gerar_main_calls_run_with_mapped_request`, `test_argparse_path_does_not_invoke_wizard` |
| 2 | Non-TTY stdin fails fast with clear PT message; no `input()` hang (D-03) | **PASS** | `collect_wizard_answers` prints `_NON_TTY_MSG` to stderr + `SystemExit(1)` before `input`; `test_non_tty_fails_without_input` |
| 3 | Question order tipo→matéria→dificuldade→quantidade→provedor→reasoning→JSON; tips under each on stdout (D-04/10; WIZ-01) | **PASS** | `wizard.py` `_ask_*` sequence matches D-04; `_print_prompt` → stdout; tip constants `TIP_*`; `test_collect_defaults_and_all_tips` asserts tip substrings |
| 4 | Tipo maps only to `topico`; max-retries never asked (D-05/06) | **PASS** | First prompt → `WizardAnswers.topico`; no max-retries prompt; `run(..., max_retries=None)`; `test_no_profile_or_max_retries_prompts`; captured `max_retries is None` |
| 5 | Empty Enter → demo defaults except JSON path re-prompt (D-07/11; WIZ-02) | **PASS** | Defaults from `main._DEFAULT_*`; `_ask_out_path` loops until non-empty; `test_collect_defaults_and_all_tips` (7 empty + path), re-prompt path in same test |
| 6 | Reasoning always asked; Enter → medium; global `DEFAULT_REASONING_EFFORT = medium` (D-08; WIZ-02) | **PASS** | `reasoning.DEFAULT_REASONING_EFFORT = "medium"`; `_ask_reasoning` empty → `"medium"`; argparse help + `.env.example` + README say medium; `test_resolve_reasoning_default_medium`, `test_provider_enter_leaves_unset` |
| 7 | Reasoning tip: Grok/Gemini honor; OpenAI `gpt-4o-mini` may ignore (D-09) | **PASS** | `TIP_REASONING` contains both halves; tests assert `"Grok/Gemini"` and `"gpt-4o-mini"` in stdout |
| 8 | Wizard maps to `GenerationRequest` + env + `main.run` (no failover re-impl) (D-14/15; WIZ-02) | **PASS** | `run_wizard` builds `GenerationRequest`, sets `LLM_PROVIDER` / `LLM_REASONING_EFFORT`, calls `main_mod.run`; no direct `generate_with_failover` from wizard |
| 9 | No profiles UX; mock input/isatty; CI stays on argparse (D-12/13; WIZ-03) | **PASS** | No profile strings; `test_argparse_path_does_not_invoke_wizard`; suite offline 133 passed |

## Requirements WIZ-01..03

| ID | Result | Evidence |
|----|--------|----------|
| WIZ-01 | **PASS** | `gerar` + 7-question tip-backed flow on TTY; order locked in `collect_wizard_answers` |
| WIZ-02 | **PASS** | Answers → `run()`; Enter defaults; JSON required; reasoning default medium globally |
| WIZ-03 | **PASS** | Argparse path intact; `test_wizard.py` mocks `input`/`isatty`; patches `run` (no live LLM) |

## CONTEXT decisions D-01..D-15

| ID | Result | Notes |
|----|--------|-------|
| D-01 | **PASS** | First token `gerar` |
| D-02 | **PASS** | Argparse without `gerar` |
| D-03 | **PASS** | Non-TTY PT fail |
| D-04 | **PASS** | Exact 7-question order |
| D-05 | **PASS** | No max-retries prompt; `max_retries=None` |
| D-06 | **PASS** | Tipo → `topico` only |
| D-07 | **PASS** | Enter → demo defaults |
| D-08 | **PASS** | Reasoning always; default `medium` |
| D-09 | **PASS** | Tip includes Grok/Gemini + gpt-4o-mini |
| D-10 | **PASS** | Tips under prompts on stdout |
| D-11 | **PASS** | JSON path re-prompt; no invented filename |
| D-12 | **PASS** | No profiles |
| D-13 | **PASS** | Mocked tests; argparse for CI |
| D-14 | **PASS** | `wizard.py`; thin `main` dispatch |
| D-15 | **PASS** | Calls existing `run` only (failover stays inside `run`) |

## Artifacts

| Artifact | Result | Notes |
|----------|--------|-------|
| `exercise-ai/wizard.py` | **PASS** | `WizardAnswers`, `collect_wizard_answers`, `run_wizard`, TTY guard, tips, re-prompts |
| `exercise-ai/main.py` | **PASS** | `gerar` dispatch before argparse; argparse path preserved |
| `exercise-ai/reasoning.py` | **PASS** | `DEFAULT_REASONING_EFFORT = "medium"` |
| `exercise-ai/tests/test_wizard.py` | **PASS** | 8 tests: tips, TTY, mapping, argparse coexistence, re-prompt, no profiles/max-retries |

## Key links

| Link | Result | Notes |
|------|--------|-------|
| `main` first token `gerar` → wizard | **PASS** | Strip/reject extras; `run_wizard()` |
| Wizard answers → `main.run(...)` | **PASS** | Same entry as argparse; env for provider/reasoning |
| `DEFAULT_REASONING_EFFORT` ↔ wizard Enter + argparse omit | **PASS** | Both resolve to `medium` |

## Prohibitions / deferred (spot-check)

| Item | Result |
|------|--------|
| No GUI / web form | **PASS** — stdlib `input` only; no GUI deps |
| No saved profiles / profile UX | **PASS** — no profile prompts; test asserts absence |
| Do not ask max-retries in wizard | **PASS** — not in prompt sequence; `max_retries=None` |
| Do not remove argparse | **PASS** — `build_parser` + `--out` required still present |
| Do not re-implement Phase 8 failover in wizard | **PASS** — wizard calls `run` only; failover remains in `main.run` → `generate_with_failover` |
| No live LLM in pytest | **PASS** — suite green offline |
| No new PyPI deps for UX | **PASS** — stdlib only |

## ROADMAP success criteria

| # | Criterion | Result |
|---|-----------|--------|
| 1 | `gerar` starts wizard on TTY; locked sequence from 10-CONTEXT | **PASS** |
| 2 | Answers → `GenerationRequest` + provider + reasoning + `--out` → existing pipeline | **PASS** |
| 3 | Tips under each question; Enter defaults; JSON re-prompt if empty | **PASS** |
| 4 | Without `gerar`, argparse valid; CI tests need no real TTY/wizard | **PASS** |
| 5 | Global reasoning default aligned to `medium` | **PASS** |

## Spot checks (requested)

| Check | Result |
|-------|--------|
| `DEFAULT_REASONING_EFFORT` is `medium` | **PASS** — `reasoning.py` line + tests |
| Tips include D-09 (Grok/Gemini + gpt-4o-mini) | **PASS** — `TIP_REASONING` + stdout asserts |
| `gerar` vs argparse coexistence | **PASS** — branch + `test_argparse_path_does_not_invoke_wizard` + `test_gerar_rejects_extra_tokens` |

## Gaps

None blocking.

## Verdict

Phase 10 delivers WIZ-01/02/03 against plan must_haves, CONTEXT D-01…D-15, and ROADMAP criteria 1–5. Deferred items remain out of scope. Full suite green offline (133 passed).
