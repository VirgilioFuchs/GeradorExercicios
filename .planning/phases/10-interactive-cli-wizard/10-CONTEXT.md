# Phase 10: Interactive CLI Wizard - Context

**Gathered:** 2026-09-15  
**Status:** Ready for planning  
**Promoted from:** SEED-004

<domain>
## Phase Boundary

Add an interactive, Portuguese Q&A flow to generate exercises by invoking a **`gerar`** tag on the project entrypoint — each question shows a short **tip** underneath. Map answers into the existing pipeline (`GenerationRequest`, provider, `--reasoning`, JSON `--out`). Keep argparse for scripts/CI. Does **not** implement Phase 8 failover, GUI, or saved profiles.

</domain>

<decisions>
## Implementation Decisions

### Activation
- **D-01:** Wizard opens when the first CLI token is **`gerar`** (ex.: `python exercise-ai/main.py gerar`). That “abre” o fluxo interativo do lab.
- **D-02:** Without `gerar`, keep the current argparse path (`--out` obrigatório, flags `--materia`, `--reasoning`, etc.) for automação/CI.
- **D-03:** Wizard requires an interactive TTY; if stdin is not a TTY, fail with a clear PT message (do not hang).

### Question sequence (locked)
- **D-04:** Exact order:
  1. Tipo de exercício → maps to **`topico`** only
  2. Matéria
  3. Dificuldade
  4. Quantidade
  5. Provedor
  6. Reasoning (`none|low|medium|high`)
  7. Nome do JSON (`--out` path)
- **D-05:** Do **not** ask `max-retries` in the wizard (use existing default / `RELY_MAX_RETRIES`).

### Field mapping
- **D-06:** “Tipo de exercício” = **`topico`** only (no new schema field).
- **D-07:** Empty **Enter** on any prompt accepts the **demo defaults** (same as argparse defaults today), and the tip must state the default value.
- **D-08:** Reasoning is **always** asked; Enter → default **`medium`**. Align global `DEFAULT_REASONING_EFFORT` / env default to **`medium`** in this phase (was `low` after quick 260915-d26) so wizard and flags match.
- **D-09:** Tip under reasoning notes that Grok/Gemini honor the level; OpenAI `gpt-4o-mini` may ignore (capability gate already shipped).

### UX / tips (draft — operator may tweak later via `$gsd-fast`)
- **D-10:** Show tip **under** each prompt (stderr or stdout — prefer stdout for the question+tip block so the conversation reads as one stream; errors still stderr). Suggested tips (PT):

| Prompt | Tip (draft) |
|--------|-------------|
| Tipo / tópico | `Ex.: Equação do primeiro grau. Enter = "Equação do primeiro grau".` |
| Matéria | `Ex.: Matemática. Enter = "Matemática".` |
| Dificuldade | `Digite facil, medio ou dificil. Enter = facil.` |
| Quantidade | `Inteiro 1–40. Enter = 3.` |
| Provedor | `openai, gemini ou grok (precisa da chave no .env). Enter = auto-detect pela chave.` |
| Reasoning | `none / low / medium / high — quanto o modelo “pensa”. Enter = medium. (gpt-4o-mini pode ignorar.)` |
| Nome do JSON | `Arquivo de saída, ex.: exercicios.json ou pasta/saida.json. Obrigatório ter um caminho válido.` |

- **D-11:** For **Nome do JSON**, empty Enter should still require a path — if demo has no file default for `--out` (required today), **re-prompt** until non-empty valid path (exception to D-07 for this field only). Soft-confirm with operator if they insist Enter invents `exercicios.json` — **locked:** re-prompt until provided (safer than writing a surprise file).

### Coexistence / quality
- **D-12:** No saved profiles / no “profile (--)” UX.
- **D-13:** Tests: mock `input()`; assert mapping to run kwargs; no live LLM; CI still uses argparse flags.
- **D-14:** Module preference: `exercise-ai/wizard.py` (or `cli_wizard.py`) called from `main.py` when argv[0]/first token is `gerar` — keep `main.py` thin.

### Roadmap placement
- **D-15:** Phase **10** on milestone **v1.2** (UX), can proceed independently of Phase 8 Failover; operator may prioritize this before failover.

</decisions>

<canonical_refs>
- `.planning/seeds/SEED-004-interactive-cli-wizard.md`
- `exercise-ai/main.py` — argparse + `run()`
- `exercise-ai/reasoning.py` — `resolve_reasoning_effort`, levels
- `exercise-ai/models.py` — `GenerationRequest`, `DificuldadeEnum`
- README — CLI table / defaults
</canonical_refs>

<code_context>
- Today `--out` is required in argparse; wizard must collect an equivalent path.
- Provider auto-detect already exists when `LLM_PROVIDER` unset.
- Reasoning default currently `low` in `reasoning.py` — Phase 10 changes default to `medium` (D-08).
</code_context>

<specifics>
Operator answers (2026-09-15):
1. Tag **`gerar`** to open the project interactive flow
2. Sequence as proposed (incl. reasoning)
3. Tipo = tópico only
4. Enter = defaults
5. Reasoning always; default **medium**
6. Phase 10 on v1.2 now
7. Tips drafted by agent; tweak later with `$gsd-fast` if needed
</specifics>

<deferred>
- GUI / web form
- Profiles on disk
- Asking max-retries in wizard
- Replacing argparse entirely
- Phase 8 failover
</deferred>
