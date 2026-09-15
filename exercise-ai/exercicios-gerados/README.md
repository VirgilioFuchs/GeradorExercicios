# Exercícios gerados

Artefatos locais da CLI (conteúdo gerado não vai para o git — só `.gitkeep`).

| Pasta | Conteúdo |
|-------|----------|
| `success/` | JSON de lotes com sucesso (`--out` relativo ? aqui) |
| `fail/erros/` | Log texto de cada falha de run |
| `fail/postmortem/` | `math_postmortem.jsonl` (falha math/validação final) |

`--out` absoluto (ex. testes/`tmp`) não é redirecionado. Relativo usa só o nome do arquivo sob `success/`.
