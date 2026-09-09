---
phase: 04-cli-argparse
status: clean
depth: standard
reviewed: 2026-09-08T12:50:00Z
---

# Phase 4 Code Review

**Scope:** `exercise-ai/main.py`, `exercise-ai/tests/test_main.py`, `exercise-ai/tests/test_logging_security.py`, `README.md`

## Summary

Nenhum blocker. Contrato D-14/D-15, argparse PT e anti-leakage de chaves estão coerentes com os testes.

## Findings

| Severity | File | Issue | Notes |
|----------|------|-------|-------|
| Info | `main.py` | `os.environ["LLM_PROVIDER"]` muta o processo | Intencional (D-09); ok para CLI one-shot; testes de suite subsequentes herdam o env se não limparem |
| Info | `main.py` | Mensagem de teto de quantidade um pouco verbosa | Contém `máximo 40` (D-20); ok |

## Security

- Valores de `LLM_API_KEY` / `GEMINI_API_KEY` não são logados; mensagens D-11 citam só o **nome** da variável.
- `--out` escreve apenas `model_dump()` do batch validado.

## Verdict

`clean` — sem Critical/Warning acionáveis.
