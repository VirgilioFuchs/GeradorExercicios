# Phase 8: Provider Failover - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-15
**Phase:** 8-Provider Failover
**Areas discussed:** Gatilho; Primário/par; Envelope vs RELY; CLI/logs (todas via KISS)

---

## Gatilho do failover

| Option | Description | Selected |
|--------|-------------|----------|
| API unavailable only (timeout/rate/conn/generic), not auth/math | KISS + bate com “indisponibilidade”; auth = config | ✓ |
| Failover também em auth se secundário tiver key | Mais resiliência, menos previsível | |
| Failover em math exhaustion | Scope creep / outro modelo | |

**User's choice:** “responda com KISS de acordo com o projeto atual” (todas as áreas)
**Notes:** Auth e math ficam fora; secundário sem key → erro PT claro.

---

## Primário e par

| Option | Description | Selected |
|--------|-------------|----------|
| OpenAI ↔ Gemini only; Grok out; primary = flag/env else resolve | FAILOVER-01 + quick Grok deferred | ✓ |
| Incluir Grok na cadeia | Adiado explicitamente | |
| Primário sempre Gemini se ambas keys | Mudaria contrato atual de resolve | |

**User's choice:** KISS / requisitos atuais
**Notes:** Primário Grok → sem failover nesta fase.

---

## Envelope vs RELY

| Option | Description | Selected |
|--------|-------------|----------|
| Uma chamada `generate_validated_batch` por provider; máx. 1 troca | Reusa caminho; sem segundo loop aninhado | ✓ |
| Failover mid-RELY attempt-by-attempt | Mais complexo | |
| Reset max_retries no secundário com loop separado documentado como “novo” | Viola espírito FAILOVER-02 se parecer segundo loop de produto | |

**User's choice:** KISS
**Notes:** Math/validation no primário não troca provider.

---

## CLI e logs

| Option | Description | Selected |
|--------|-------------|----------|
| `--provider` ainda permite failover; `[FAILOVER] a → b (motivo)` | Lab resiliência + FAILOVER-03 | ✓ |
| `--provider` trava sem failover | Mais previsível, menos útil no lab | |
| Sem tag dedicada | Viola FAILOVER-03 | |

**User's choice:** KISS
**Notes:** Testes mockados obrigatórios.

---

## Agent Discretion

- Onde colocar o envelope (`main` vs `reliability` wrapper)
- Copy exato das mensagens PT / nome do helper

## Deferred Ideas

- Grok na cadeia; failover por math; `--no-failover`; token-driven routing
