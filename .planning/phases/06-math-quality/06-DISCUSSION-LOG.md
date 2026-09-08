# Phase 6: Math Quality - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-08
**Phase:** 6-Math Quality
**Areas discussed:** Escopo dos casos básicos, Estratégia de checagem, Mensagem de erro matemática, Tipos de exercício cobertos

---

## Escopo dos casos básicos

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Só aritmética óbvia | |
| 2 | Aritmética + equações lineares simples | ✓ |
| 3 | + frações elementares | |
| 4 | Lista fechada de fixtures | |
| 5 | Você decide | |

**User's choice:** Q1=2; Q2=mistura 1+2 + postmortem para melhorar LLM; Q3=2 (report all); Q4=2 (estrito moderado)
**Notes:** Não interpretável → passa + postmortem; inconsistência clara → rejeita.

---

## Estratégia de checagem

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Heurísticas stdlib | |
| 2 | Biblioteca (ex. sympy) | |
| 3 | Só fixtures | |
| 4 | Híbrido fixtures + heurísticas | ✓ |
| 5 | Você decide | |

**User's choice:** Q1=4 (+ pin/vendor se lib); Q2=conforme arquitetura; Q3=3 (postmortem só falha final); Q4=3 (preferir stdlib)
**Notes:** Lib só se research exigir; então versão estável + vendored.

---

## Mensagem de erro matemática

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Prefixo fixo | |
| 2 | Prefixo + índice | parcial |
| 3 | Mesmo estilo estrutural | |
| 4 | stderr [MATH] + raise PT curto | ✓ (misturado com prefixo+índice) |

**User's choice:** Q1=4+prefixo/índice; Q2=4 (mínimo user, detalhe no postmortem); Q3=3 (raise truncado); Q4=2 (`após N regenerações`)
**Notes:** Detalhes (tipo, esperado vs obtido) no postmortem/log.

---

## Tipos de exercício cobertos

| Option | Description | Selected |
|--------|-------------|----------|
| Q1-3 | Inteiros + decimais simples | ✓ |
| Q2-1 | Só `ax+b=c` | ✓ |
| Q3-2 | Frações etc. fora; % simples ok | ✓ |
| Q4-3 | Fixtures mínimas; geradores deferred | ✓ |

**User's choice:** Q1=3; Q2=1; Q3=2; Q4=3 (após explicação das opções de teste)
**Notes:** User pediu explicação de Q4 antes de escolher.

---

## the agent's Discretion

- Local do código math vs extensão de `validator.py` (desde que no caminho `validate_exercise_batch`)
- Formato do artefato de postmortem
- Detalhe das heurísticas de parse

## Deferred Ideas

- Pipeline de treino/fine-tune LLM a partir do postmortem
- Geradores property-style nos testes
- CAS / frações / radicais / sistemas / inequações / geometria
- Prompt repair
