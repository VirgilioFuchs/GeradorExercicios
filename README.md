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
  --max-retries 1 \
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
| `--max-retries` | não | Regenerações após a 1ª tentativa (`0`–`3`). Se omitido: `RELY_MAX_RETRIES` ou padrão `1` |

Ajuda em português: `python exercise-ai/main.py --help`

### Regeneração e Phase 6

Em falha de validação estrutural ou resposta LLM inválida, o gerador regenera até N vezes com o **mesmo prompt** (sem apêndice de erro). Falhas matemáticas futuras (Phase 6) reutilizarão o mesmo caminho (`generate_validated_batch`). Auth, timeout, rate-limit e conexão **não** regeneram.

## Como testar

A suite usa mocks e dados estáticos — **não** chama LLMs reais:

```bash
pytest exercise-ai -q
```

Em push/PR para `master`, o workflow GitHub Actions `CI` executa o mesmo comando.

## Stdout vs stderr

- **Sucesso (stdout):** texto legível por exercício (`### Exercício N`, `Enunciado:`, `Resposta:`, `Explicação:`).
- **Sucesso (arquivo `--out`):** JSON UTF-8 do lote (`exercicios`), indentado, `ensure_ascii=False`.
- **Stderr:** rótulos de estágio (`Gerando…`, `Validando…`, `Nª Regeneração`), duração agregada (`total_ms` + `chamadas`), eventos de desenvolvimento (início, parâmetros sem segredos, sucesso/falha) e detalhes `[VALIDAÇÃO]` / `[API:openai|gemini]`. O motivo de erro só aparece após esgotar regenerações.

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
