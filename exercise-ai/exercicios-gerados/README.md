# Exercícios gerados

Artefatos locais da CLI (conteúdo gerado não vai para o git — só `.gitkeep`).

| Pasta | Conteúdo |
|-------|----------|
| `success/` | JSON de lotes gerados com sucesso |
| `fail/erros/` | Logs de erro da run (texto) |
| `fail/postmortem/` | Postmortem math / falha final (jsonl) |

Roteamento automático (gravar sucesso em `success/`, falha em `fail/...`) ainda precisa de um `$gsd-quick` para ligar em `main.py` / wizard `gerar`.
