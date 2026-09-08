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
| `LLM_PROVIDER` | Opcional: `openai` ou `gemini`. Se omitido, o provedor é detectado pelas chaves disponíveis |

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
  --out exercicios.json
```

| Flag | Obrigatória | Descrição |
|------|-------------|-----------|
| `--out` | sim | Caminho do arquivo JSON de saída |
| `--materia` | não | Matéria (padrão: Matemática) |
| `--topico` | não | Tópico (padrão: Equação do primeiro grau) |
| `--dificuldade` | não | `facil` \| `medio` \| `dificil` (padrão: facil) |
| `--quantidade` | não | Inteiro de 1 a 40 (padrão: 3) |
| `--provider` | não | `openai` \| `gemini` para esta execução |

Ajuda em português: `python exercise-ai/main.py --help`

## Como testar

A suite usa mocks e dados estáticos — **não** chama LLMs reais:

```bash
pytest exercise-ai -q
```

## Stdout vs stderr

- **Sucesso (stdout):** texto legível por exercício (`### Exercício N`, `Enunciado:`, `Resposta:`, `Explicação:`).
- **Sucesso (arquivo `--out`):** JSON UTF-8 do lote (`exercicios`), indentado, `ensure_ascii=False`.
- **Stderr:** rótulos de estágio (`Gerando…`, `Validando…`), eventos de desenvolvimento (início, parâmetros sem segredos, sucesso/falha) e detalhes `[VALIDAÇÃO]` / `[API:openai|gemini]`.

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
