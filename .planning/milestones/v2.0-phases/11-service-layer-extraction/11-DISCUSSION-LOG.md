# Phase 11: Service Layer Extraction - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-16
**Phase:** 11-Service Layer Extraction
**Areas discussed:** Forma do contrato de erro, Side-effects de filesystem, Assinatura de generate_batch, Onde vive a doc do contrato

---

## Forma do contrato de erro

| Option | Description | Selected |
|--------|-------------|----------|
| Só atributo `kind` em ValueError | Discriminador string sem hierarquia nova | |
| Subclasses (ConfigError / InvalidRequestError / GenerationFailedError) | Mantém except ValueError do CLI; host faz except tipado | ✓ |

**User's choice:** subclasses — “quanto mais detalhado o log, melhor”
**Follow-up:** Logging detalhado = atributos ricos + logger no service/adapter (não converter ~33 prints nesta fase)

---

## Side-effects de filesystem no caminho do service

| Option | Description | Selected |
|--------|-------------|----------|
| CLI-only (service nunca escreve) | Postmortem/fail-log/flush só no adapter | |
| Flush guardado; postmortem/fail-log só no CLI | Necessário para observabilidade existente sem mascarar erros | ✓ (agent discretion) |
| Diretório via env / flag nova | Abstração prematura | |

**User's choice:** “deixo a teu critério (não quero algo atoa mas o necessário)”
**Notes:** Agent locked D-06/D-07 accordingly

---

## Assinatura de generate_batch

| Option | Description | Selected |
|--------|-------------|----------|
| Só `(request)` | Mínimo; kwargs depois | ✓ |
| Também kwargs max_retries/provider/reasoning | Per-call overrides agora | |

**User's choice:** “por enquanto só request, se o projeto evoluir mais, adicionamos o kwargs”

---

## Onde vive a doc do contrato (EMBED-07)

| Option | Description | Selected |
|--------|-------------|----------|
| Seção curta no README | Assinatura + JSON + erros + nomes reservados + sequencial | ✓ |
| CONTRACT.md separado | Arquivo novo | |
| Só docstring | Sem superfície de doc para o host | |

**User's choice:** “Reame” (interpretado como README)
**Follow-up:** Confirmado conteúdo = seção curta completa (opção 1/1)

---

## the agent's Discretion

- FS side-effects (D-06, D-07)
- Nomes finais das classes de erro; valor exato do timeout Gemini; forma mínima do name-collision check

## Deferred Ideas

- kwargs na assinatura; OBS-01 usage return; LOG-01 print→logging; PKG-01 packaging
