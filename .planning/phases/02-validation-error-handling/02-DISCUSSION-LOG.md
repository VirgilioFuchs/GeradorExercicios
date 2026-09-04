# Phase 2: Validation & Error Handling - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-02
**Phase:** 02-validation-error-handling
**Areas discussed:** Profundidade da validação, Formato das mensagens de erro, Erros de API, Comportamento ao falhar

---

## Profundidade da validação

| Option | Description | Selected |
|--------|-------------|----------|
| Só objeto Pydantic | Structured Outputs + regras semânticas no tipado | ✓ |
| Pydantic + JSON bruto | Camada extra antes do parse | |
| Log JSON bruto em erro | stderr com dump para documentação | ✓ (freeform) |
| Quantidade exata | len == request.quantidade | ✓ |
| Trim whitespace | Campos só-espaço = vazio | ✓ |
| stderr raw dump | Mensagem + JSON bruto no terminal | ✓ |

**User's choice:** Pydantic + log JSON bruto em stderr; quantidade exata; trim whitespace.
**Notes:** Usuário enfatizou documentar tudo que acontece para o usuário/desenvolvedor.

---

## Formato das mensagens de erro

| Option | Description | Selected |
|--------|-------------|----------|
| Texto direto ao usuário | Sem prefixo na mensagem principal | ✓ (freeform) |
| Log com prefixos | [VALIDAÇÃO]/[API] + dados brutos no log | ✓ (freeform) |
| Campo com path | exercicios[i].campo | ✓ |
| Modo listar todos vs primeiro | Constante no código | ✓ (freeform) |
| Esperado vs recebido | Valores na mensagem | ✓ |

**User's choice:** Duas camadas — mensagem simples + log detalhado; path de campo; modo dual via constante no código.
**Notes:** Rejeitou env var para modo de reporte; prefere constante editável no fonte.

---

## Erros de API

| Option | Description | Selected |
|--------|-------------|----------|
| Usuário: mensagem necessária | Log: distinção por provedor | ✓ (freeform) |
| Ambas chaves na mensagem | GEMINI_API_KEY + LLM_API_KEY | ✓ |
| Tipos mapeados | timeout, rate limit, rede, auth | ✓ |
| Resposta vazia | RuntimeError + log | ✓ |

**User's choice:** Distinção nos logs; mensagem unificada simplificada ao usuário.

---

## Comportamento ao falhar

| Option | Description | Selected |
|--------|-------------|----------|
| Abort + exit 1 | Sem retry | ✓ |
| stdout UTF-8 JSON only | Sucesso formatado | ✓ (freeform) |
| Labels stderr | Gerando… / Validando… | ✓ |

**User's choice:** Abort imediato; JSON UTF-8 limpo no stdout; labels de etapa em stderr.

---

## Deferred Ideas

- Microserviços para escalabilidade de exercícios
- Barra de progresso com percentual por processo
- Não encerrar até entregar todas as atividades (retry/persistência)
- API reserva / failover automático entre provedores
