# Phase 4: CLI argparse - Context

**Gathered:** 2026-09-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Entregar CLI com `argparse` para os parâmetros de geração (com defaults da demo quando omitidos), flag `--provider`, saída **legível no stdout**, JSON persistido via **`--out` obrigatório**, help/erros em português, teto de quantidade 40 — sem mudar o prompt do LLM, sem BNCC, sem aprendizado automático a partir de erros da IA.

**In scope:** CLI-04 (ampliado pelas decisões abaixo: dual output texto+JSON file, `--provider`, teto 40).
**Out of scope:** retry/RELY (Phase 5), math validation (Phase 6), BNCC, DB, agente, CI, feedback loop de aprendizado se a IA errar (deferred).

</domain>

<decisions>
## Implementation Decisions

### Flags e idioma
- **D-01:** Flags em português: `--materia`, `--topico`, `--dificuldade`, `--quantidade` — **Reversibility:** costly — vira contrato público do CLI/README
- **D-02:** Apenas flags longas (sem `-m`/`-t`/`-d`/`-q`)
- **D-03:** Qualquer ordem de flags (argparse padrão); sem modo só-posicional
- **D-04:** `--dificuldade` aceita exatamente o enum: `facil` | `medio` | `dificil` (sem sinônimos/acentos)

### Obrigatórios vs defaults
- **D-05:** Parâmetros de geração omitidos usam **defaults da demo v1** (Matemática / Equação do primeiro grau / facil / 3)
- **D-06:** `python exercise-ai/main.py` sem flags de geração ainda roda com esses defaults (mas `--out` continua obrigatório — D-14)
- **D-07:** Valores inválidos de quantidade (não-int, ≤0) rejeitados pelo argparse **antes** de chamar o LLM
- **D-08:** Teto máximo: **40** exercícios; acima disso → erro PT claro via argparse

### Provider na CLI
- **D-09:** Incluir `--provider` com choices `openai` | `gemini` (override do env nesta execução)
- **D-10:** Valor inválido → argparse rejeita com choices + usage
- **D-11:** Provider escolhido sem a chave correspondente → mensagem **específica** (não só ERR-01 genérico), ex. indicar qual chave falta para aquele provider
- **D-12:** README documenta `--provider` e o restante das flags desta fase

### Entrada / pipeline / saída
- **D-13:** `argparse` em `main` → monta `GenerationRequest` → pipeline renomeado para `run(request)` (substituir `run_demo`); testes atualizam o nome — **Reversibility:** costly — renomeia API usada nos testes
- **D-14:** **Stdout = texto legível** (não JSON cru). JSON da resposta gravado em arquivo; **`--out` é obrigatório** (path do JSON) — **Reversibility:** one-way — quebra o contrato v1 “JSON-only stdout”; consumidores/scripts precisam adaptar
- **D-15:** Layout do texto (stdout):
  ```
  ### Exercício N
  Enunciado: ...
  Resposta: ...
  Explicação: ...
  ```
- **D-16:** Prompt do LLM **não muda** nesta fase — melhoria é na **apresentação** da saída
- **D-17:** Testes: fixture/batch mockado → assert no texto renderizado **e** no JSON escrito (sem LLM real); adaptar `test_main`

### Help / erros
- **D-18:** `--help` e mensagens argparse em **português**
- **D-19:** `--help` lista os defaults da demo
- **D-20:** Erro de teto (`quantidade > 40`) com mensagem PT explícita (`máximo 40`)

### Claude's Discretion
- Formatação exata de espaçamento/blank lines no renderer de texto
- Wording preciso das mensagens de erro (desde que PT e claras)
- Estrutura interna do módulo (helper `format_batch_text` vs inline) — YAGNI

</decisions>

<deferred>
## Deferred Ideas

- Feedback/aprendizado automático quando a saída da IA divergir do esperado (comparar terminal vs JSON para treinar/corrigir) — pós v1.1
- BNCC — fora do v1.1 (confirmado pelo usuário)
- Aliases curtos (`-m`, etc.)
- Sinônimos de dificuldade (`fácil`, `easy`)
- Saída JSON no stdout via `--format json` (não pedido; contrato agora é texto + arquivo)

</deferred>

<code_context>
## Existing Code Insights

### Reusable assets
- `exercise-ai/main.py` — entry + `run_demo()` hardcoded params; LOG-01 + stdout JSON hoje
- `models.GenerationRequest` / `DificuldadeEnum` — campos e enum já alinhados às flags PT
- `generate_exercises` / `validate_exercise_batch` — pipeline a reusar sem alteração de prompt
- `tests/test_main.py` — contrato atual JSON-only stdout (deverá mudar conforme D-14/D-17)
- `README.md` — seção “Como executar” a atualizar

### Established patterns
- Stderr: estágios + logs; não vazar API keys
- Fail-fast exit 1 em erros de usuário/API
- Defaults de demo documentados no AGENT.md / código atual

### Integration points
- `if __name__ == "__main__"` → argparse → `run(request)` → renderer texto + write JSON `--out`
- `--provider` deve influenciar resolução de provider (hoje `_resolve_provider` / env) nesta execução

</code_context>

<specifics>
## Specific Ideas to Capture

- Usuário quer leitura humana no terminal; JSON separado para comparação/fixture — não misturar JSON cru como UX principal
- Comparação texto↔JSON é para testes agora; aprendizado futuro se IA errar fica deferred

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

- `.planning/ROADMAP.md` — Phase 4 success criteria (atualizar mentalmente: stdout texto + `--out` JSON; critérios originais falavam JSON no stdout)
- `.planning/REQUIREMENTS.md` — CLI-04
- `.planning/PROJECT.md` — Current Milestone v1.1
- `exercise-ai/main.py` — entry atual
- `exercise-ai/models.py` — `GenerationRequest`, `DificuldadeEnum`
- `README.md` — docs de execução

</canonical_refs>

---

*Phase: 04-cli-argparse*
*Context gathered: 2026-09-04*
