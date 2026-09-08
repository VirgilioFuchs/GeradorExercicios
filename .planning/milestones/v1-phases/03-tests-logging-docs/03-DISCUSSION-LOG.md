# Phase 3: Tests, Logging & Docs - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-04
**Phase:** 3-Tests, Logging & Docs
**Areas discussed:** (none selected — user deferred all to agent defaults)

---

## Formato e localização da suite

| Option | Description | Selected |
|--------|-------------|----------|
| `exercise-ai/tests/` + conftest | Co-located with package; matches requirements.txt location | ✓ |
| `tests/` na raiz | Layout monorepo clássico | |
| Só scripts em `.planning/` | Continuar verifies efêmeros | |

**User's choice:** Você decide (padrão recomendado)
**Notes:** D-01/D-02 locked — factories Pydantic + optional fixtures JSON

---

## Largura dos testes

| Option | Description | Selected |
|--------|-------------|----------|
| Só TEST-02 (validador) | Mínimo ROADMAP | |
| TEST-02 + EVAL remediação (mappers, stdout, anti-leak) | Fecha BLOCKER EVAL-REVIEW | ✓ |
| Suite completa + CI Actions | Escopo CI nesta fase | |

**User's choice:** Você decide (padrão recomendado)
**Notes:** D-03 — sem LLM real; CI excluído (D-10)

---

## Estilo de logging

| Option | Description | Selected |
|--------|-------------|----------|
| Só prints atuais | Não atende LOG-01 início/sucesso estruturado | |
| logging stdlib + prefixos existentes + redaction | LOG-01 + LOG-02 / WR-01 | ✓ |
| Phoenix / arquivos persistentes | Overkill MVP | |

**User's choice:** Você decide (padrão recomendado)
**Notes:** D-05–D-07

---

## README

| Option | Description | Selected |
|--------|-------------|----------|
| `README.md` raiz em PT | SCAF-04, onboarding GitHub | ✓ |
| Só `exercise-ai/README.md` | Menos visível no remote | |
| Docs só em inglês | Público-alvo BR | |

**User's choice:** Você decide (padrão recomendado)
**Notes:** D-08/D-09

---

## CI nesta fase

| Option | Description | Selected |
|--------|-------------|----------|
| GitHub Actions agora | | |
| Só documentar pytest no README | YAGNI lab MVP | ✓ |

**User's choice:** Você decide (padrão recomendado)
**Notes:** D-10 — CI deferred

---

## the agent's Discretion

- Nomes de arquivos de teste
- Forma exata do helper de logging
- Exemplo JSON no README
- Ordem das tasks no plano

## Deferred Ideas

- GitHub Actions CI
- Phoenix / log files
- RELY / failover / argparse / MATH-01
- WR-03/WR-04 se não couber no plano
