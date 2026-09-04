# Gerador de Exercícios com IA

Aplicação Python que gera exercícios de matemática via LLM a partir de parâmetros simples (matéria, tópico, dificuldade, quantidade), retornando JSON estruturado com enunciado, resposta e explicação — com validação estrutural obrigatória antes do uso.

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

```bash
python exercise-ai/main.py
```

## Como testar

A suite usa mocks e dados estáticos — **não** chama LLMs reais:

```bash
pytest exercise-ai -q
```

## Stdout vs stderr

- **Sucesso:** apenas JSON UTF-8 do lote de exercícios em **stdout**.
- **Stderr:** rótulos de estágio (`Gerando…`, `Validando…`), eventos de desenvolvimento (início, parâmetros sem segredos, sucesso/falha) e detalhes `[VALIDAÇÃO]` / `[API:openai|gemini]`.

Exemplo mínimo de saída JSON (stdout):

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
