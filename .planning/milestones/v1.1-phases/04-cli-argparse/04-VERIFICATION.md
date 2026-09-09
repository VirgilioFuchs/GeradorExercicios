---
phase: 04-cli-argparse
verified: 2026-09-08T12:50:00Z
status: passed
score: 7/7 must-haves verified
behavior_unverified: 0
behavior_unverified_items: []
coincidental_reliance_items: []
---

# Phase 4: CLI argparse Verification Report

**Phase Goal:** Usuário passa matéria, tópico, dificuldade e quantidade via argumentos de linha de comando sem editar código  
**Verified:** 2026-09-08T12:50:00Z  
**Status:** passed

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Flags PT long-only em qualquer ordem; gera sem editar código | ✓ VERIFIED | `build_parser` + `test_cli_demo_defaults_with_out`; pytest green |
| 2 | Defaults demo quando omitidos; `--out` obrigatório | ✓ VERIFIED | `test_cli_requires_out_before_llm`, `test_cli_demo_defaults_with_out` |
| 3 | Stdout texto D-15; JSON só em `--out` | ✓ VERIFIED | `test_run_success_text_stdout_and_json_out` |
| 4 | quantidade/dificuldade/provider inválidos rejeitados pré-LLM (PT) | ✓ VERIFIED | testes `test_cli_rejects_*` + `máximo 40` |
| 5 | `--provider` + mensagem D-11 de chave ausente | ✓ VERIFIED | `test_cli_provider_override_sets_env`, `test_cli_missing_provider_key_specific_message` |
| 6 | `run(request)`; testes mockados; prompts intactos | ✓ VERIFIED | `run_demo` ausente; `prompts.py` não no diff de produção |
| 7 | README + ROADMAP alinhados a D-14 | ✓ VERIFIED | README flags/`--out`; ROADMAP critério #1 texto+`--out` |

**Score:** 7/7 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `exercise-ai/main.py` | argparse, run, text, --out | ✓ EXISTS + SUBSTANTIVE | `build_parser`, `run`, `format_batch_text`, `main` |
| `exercise-ai/tests/test_main.py` | dual-output + argparse tests | ✓ EXISTS + SUBSTANTIVE | 11 testes |
| `README.md` | docs flags | ✓ EXISTS + SUBSTANTIVE | tabela de flags + exemplos |
| `.planning/ROADMAP.md` | D-14 criteria | ✓ EXISTS + SUBSTANTIVE | critério #1 atualizado |

**Artifacts:** 4/4 verified

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| argparse | GenerationRequest | main() | ✓ WIRED | flags → request → run |
| run | generate/validate | pipeline | ✓ WIRED | unchanged generate_exercises |
| validated batch | stdout + --out | format + dump | ✓ WIRED | text print + Path.write_text JSON |

**Wiring:** 3/3 connections verified

## Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|----------------|
| CLI-04 | ✓ SATISFIED | - |

**Coverage:** 1/1 requirements satisfied

## Anti-Patterns Found

None.

## Human Verification Required

None — all verifiable items checked programmatically (`pytest exercise-ai -q` → 39 passed).

## Gaps

None.

## Next Action

Phase goal achieved — ready for `phase.complete` / transition.
