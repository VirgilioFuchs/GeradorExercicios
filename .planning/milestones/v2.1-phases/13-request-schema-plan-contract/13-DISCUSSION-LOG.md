# Phase 13 Discussion Log

**Date:** 2026-09-21  
**Phase:** 13 — Request schema & plan contract

## Areas selected
1. Forma do plano  
2. Precedência uniforme × misto  
3. Echo em `Exercise`

## Forma do plano
| Q | Options | Choice |
|---|---------|--------|
| Shape | itens only / plano only / both | **both** (plano expands to itens) |
| Expansion order | band order / round-robin / decide | **band order** fácil→médio→difícil |
| Both plano+itens | error / prefer itens / prefer plano | **error** |
| Scalar dificuldade | forbid / ignore / dominant / … | User clarified → **`dificuldades` plural** summarizing bands used (1/2/3) |

## Precedência
| Q | Options | Choice |
|---|---------|--------|
| Mode detect | presence plano/itens / always plano | **presence** |
| Legacy scalar | accept normalize / reject | **accept → dificuldades:[one]** |
| dificuldades 2+ no plan | error / equal split | **equal split** |
| Remainder | last band / first / error | **last band** |

## Echo
| Q | Options | Choice |
|---|---------|--------|
| Per-exercise dificuldade | always required / mixed only / optional | **always required** |
| Batch dificuldades | yes / no | **yes** |
| Mismatch | fail+RELY / correct / accept LLM | **fail**; bounded RELY; **typed error to host**; postmortem on final fail (not interactive pause) |

## Deferred
- TIPO taxonomy; CAP-02; SEED-005 polish; wizard-only confirm-before-RELY
