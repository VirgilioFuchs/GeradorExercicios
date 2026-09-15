# Gerador de Exercícios com IA

Aplicação Python que gera exercícios de matemática via LLM a partir de parâmetros simples (matéria, tópico, dificuldade, quantidade), com validação estrutural obrigatória. No sucesso, a CLI imprime texto legível no **stdout** e grava o JSON estruturado no arquivo indicado por **`--out`**.

## Setup

```bash
pip install -r exercise-ai/requirements.txt
```

## Variáveis de ambiente

Copie `exercise-ai/.env.example` para `exercise-ai/.env` (ou `.env` na raiz do repositório) e preencha as chaves. **Nunca** cole segredos reais neste README ou no código.

| Variável | Descrição |
|----------|-----------|
| `LLM_API_KEY` | Chave da API OpenAI (formato `sk-...`) |
| `GEMINI_API_KEY` | Chave da API Google Gemini (formato `AIza...`) |
| `GROK_API_KEY` | Chave da API xAI Grok |
| `LLM_PROVIDER` | Opcional: `openai`, `gemini` ou `grok`. Se omitido, o provedor é detectado pelas chaves disponíveis |
| `LLM_REASONING_EFFORT` | Opcional: `none` \| `low` \| `medium` \| `high` (padrão `low`). Sobrescrito por `--reasoning` |
| `RELY_MAX_RETRIES` | Regenerações após a primeira tentativa (`0`–`3`). Padrão `1` se omitido. Sobrescrito por `--max-retries` |

## Como executar

`--out` é **obrigatório**. Flags de geração omitidas usam os defaults da demo (Matemática / Equação do primeiro grau / facil / 3).

```bash
python exercise-ai/main.py --out exercicios.json
```

Com parâmetros explícitos:

```bash
python exercise-ai/main.py \
  --materia Matemática \
  --topico "Equação do primeiro grau" \
  --dificuldade facil \
  --quantidade 3 \
  --provider openai \
  --reasoning low \
  --max-retries 1 \
  --out exercicios.json
```

| Flag | Obrigatória | Descrição |
|------|-------------|-----------|
| `--out` | sim | Arquivo JSON. Relativo → `exercicios-gerados/success/<nome>`; absoluto permanece |
| `--materia` | não | Matéria (padrão: Matemática) |
| `--topico` | não | Tópico (padrão: Equação do primeiro grau) |
| `--dificuldade` | não | `facil` \| `medio` \| `dificil` (padrão: facil) |
| `--quantidade` | não | Inteiro de 1 a 40 (padrão: 3) |
| `--provider` | não | `openai` \| `gemini` \| `grok` para esta execução |
| `--reasoning` | não | Esforço de raciocínio: `none` \| `low` \| `medium` \| `high` (padrão `low`) |
| `--max-retries` | não | Regenerações após a 1ª tentativa (`0`–`3`). Se omitido: `RELY_MAX_RETRIES` ou padrão `1` |

**Reasoning / thinking:** Grok recebe `reasoning_effort` na API; Gemini usa `ThinkingConfig.thinking_level` (`none` → `minimal`). OpenAI só envia o param em modelos com suporte (ex. família `gpt-5` / `o*`); o default `gpt-4o-mini` **omite** o campo (não é reasoning model).

Ajuda em português: `python exercise-ai/main.py --help`

### Regeneração e Phase 6

Em falha de validação estrutural ou resposta LLM inválida, o gerador regenera até N vezes com o **mesmo prompt** (sem apêndice de erro). Falhas matemáticas futuras (Phase 6) reutilizarão o mesmo caminho (`generate_validated_batch`). Auth, timeout, rate-limit e conexão **não** regeneram.

## Como testar

A suite usa mocks e dados estáticos — **não** chama LLMs reais:

```bash
pytest exercise-ai -q
```

Em push/PR para `master`, o workflow GitHub Actions `CI` executa o mesmo comando.

## Observabilidade de tokens

Cada chamada LLM grava um evento em memória; no fim da run a CLI faz **append** NDJSON em:

`exercise-ai/token-usage/{YYYY-MM-DD}/{provider}.ndjson`

- **Dia** = data civil no fuso local da máquina do operator.
- **Stderr:** linhas `[USAGE]` com tokens de entrada/saída, total, `duration_ms` e USD quando calculável (`indisponível` se ausente — nunca inventa `0`).
- **USD:** Grok preferencialmente via `cost_in_usd_ticks`; OpenAI/Gemini via tabela local aproximada (atualizar manualmente; sem scrape de pricing).
- Artefatos gerados estão no `.gitignore`; a pasta permanece via `.gitkeep`.
- Testes de usage usam mocks e `TOKEN_USAGE_DIR` injetável — sem LLM e sem arquivos locais de usage commitados.

## Stdout vs stderr

- **Sucesso (stdout):** texto legível por exercício (`### Exercício N`, `Enunciado:`, `Resposta:`, `Explicação:`).
- **Sucesso (arquivo `--out`):** JSON UTF-8 do lote (`exercicios`), indentado, `ensure_ascii=False`.
- **Stderr:** rótulos de estágio (`Gerando…`, `Validando…`, `Nª Regeneração`), duração agregada (`total_ms` + `chamadas`), eventos `[USAGE]` (tokens/custo), eventos de desenvolvimento (início, parâmetros sem segredos, sucesso/falha) e detalhes `[VALIDAÇÃO]` / `[API:openai|gemini|grok]`. O motivo de erro só aparece após esgotar regenerações.

Exemplo mínimo do JSON em `--out`:

```json
{
  "exercicios": [
    {
      "enunciado": "...",
      "resposta": "...",
      "explicacao": "..."
    }
  ]
}
```
