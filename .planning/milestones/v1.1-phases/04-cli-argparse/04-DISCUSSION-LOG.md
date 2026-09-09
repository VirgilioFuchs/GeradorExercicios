# Phase 4: CLI argparse — Discussion Log

**Date:** 2026-09-04
**Areas discussed:** Flags; Defaults; Provider; Entrada/saída; Help/erros; Quantidade

## Summary of answers

| Area | Lock |
|------|------|
| Flags | PT longas; qualquer ordem; enum exact |
| Defaults | Demo defaults; bare main ok for gen params; argparse validates qty; max 40 |
| Provider | `--provider` openai\|gemini; specific missing-key msg; README |
| I/O | `run(request)`; stdout text layout; `--out` required JSON file; prompt unchanged; dual fixture tests |
| Help | PT; show defaults; max-40 PT message |
| Deferred | AI learning loop; BNCC; short aliases; difficulty synonyms |

## Notes

- User clarified: better “descrição” refers to **output presentation**, not prompt changes.
- Dual output: human text on stdout + JSON file for comparison/tests.
