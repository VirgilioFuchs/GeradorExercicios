# Exercicios gerados

Artefatos locais da CLI (conteudo gerado nao vai para o git — so `.gitkeep`).

| Pasta | Conteudo |
|-------|----------|
| `success/` | JSON de lotes com sucesso (`--out` relativo ? aqui) |
| `fail/erros/` | Log texto de cada falha de run |
| `fail/postmortem/` | `math_postmortem.jsonl` (falha math/validacao final) |

`--out` absoluto (ex. testes/`tmp`) nao e redirecionado. Relativo usa so o nome do arquivo sob `success/`.
