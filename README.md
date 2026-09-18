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
| `LLM_REASONING_EFFORT` | Opcional: `none` \| `low` \| `medium` \| `high` (padrão `medium`). Sobrescrito por `--reasoning` |
| `RELY_MAX_RETRIES` | Regenerações após a primeira tentativa (`0`–`3`). Padrão `1` se omitido. Sobrescrito por `--max-retries` |

## Como executar

`--out` é **obrigatório** no modo argparse. Flags de geração omitidas usam os defaults da demo (Matemática / Equação do primeiro grau / facil / 3).

### Wizard interativo (`gerar`)

Em um terminal interativo (TTY):

```bash
python exercise-ai/main.py gerar
```

O fluxo pergunta (com tip sob cada campo): matéria → tipo/tópico → dificuldade → quantidade → provedor → reasoning → nome do JSON. **Enter** aceita o default da demo; o caminho do JSON é obrigatório (re-pergunta se vazio). Reasoning padrão do Enter e do env: **`medium`**.

Para CI/scripts, continue usando as flags argparse (não use `gerar`).

### Argparse (CI / scripts)

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
  --reasoning medium \
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
| `--reasoning` | não | Esforço de raciocínio: `none` \| `low` \| `medium` \| `high` (padrão `medium`) |
| `--max-retries` | não | Regenerações após a 1ª tentativa (`0`–`3`). Se omitido: `RELY_MAX_RETRIES` ou padrão `1` |

**Reasoning / thinking:** Grok recebe `reasoning_effort` na API; Gemini usa `ThinkingConfig.thinking_level` (`none` → `minimal`). OpenAI só envia o param em modelos com suporte (ex. família `gpt-5` / `o*`); o default `gpt-4o-mini` **omite** o campo (não é reasoning model).

Ajuda em português: `python exercise-ai/main.py --help`

### Regeneração e Phase 6

Em falha de validação estrutural ou resposta LLM inválida, o gerador regenera até N vezes com o **mesmo prompt** (sem apêndice de erro). Falhas matemáticas reutilizam o mesmo caminho (`generate_validated_batch`). Auth, timeout, rate-limit e conexão **não** regeneram no mesmo provider.

### Failover OpenAI ↔ Gemini

Se o provider primário falhar com erro de API de disponibilidade (`timeout`, `rate_limit`, `connection` ou `generic`), o lab tenta **uma vez** o outro do par OpenAI ↔ Gemini, reusando `generate_validated_batch` (sem segundo loop math/RELY). Em stderr: `[FAILOVER] openai -> gemini (timeout)` (ou o par inverso) e `[FAILOVER] usado: …` no sucesso — sem secrets.

- **Sem failover** em auth, recusa do modelo, resposta inválida tipada ou falha de validação/math.
- **Grok** fica fora da cadeia (single-provider).
- `--provider openai|gemini` **não** desliga o failover; não há flag `--no-failover` nesta fase.

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

## Embed / biblioteca

Contrato para um host embutir o gerador **in-process** (sem packaging nesta milestone — não importe `exercise_ai` como pacote instalado).

### Demo local (throwaway)

Há um demo stdlib em [`demo/`](demo/) para ver o fluxo embed end-to-end:
`python demo/serve.py` → abra **http://[::1]:8642/**. É throwaway — **delete at
v2.0 close**; fora do CI. Detalhes anti-accretion em [`demo/README.md`](demo/README.md).

### Como chamar

Coloque `exercise-ai/` em `sys.path` e chame a API pública:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path("exercise-ai").resolve()))

from models import GenerationRequest, DificuldadeEnum
from service import (
    generate_batch,
    ConfigError,
    InvalidRequestError,
    GenerationFailedError,
)

batch = generate_batch(
    GenerationRequest(
        materia="Matemática",
        topico="Equação do primeiro grau",
        dificuldade=DificuldadeEnum.FACIL,
        quantidade=3,
    )
)
# Sucesso: ExerciseBatch — serializável via batch.model_dump()
data = batch.model_dump()  # {"exercicios": [{"enunciado", "resposta", "explicacao"}, ...]}
```

Assinatura: `generate_batch(request: GenerationRequest) -> ExerciseBatch` — **somente** `request` (sem kwargs `max_retries` / `provider` / `reasoning` nesta fase).

### Erros (três subclasses)

O host deve ramificar por **classe** (e opcionalmente `.kind` / attrs), não por matching de mensagem PT:

| Exceção | Base | Quando | Attrs úteis |
|---------|------|--------|-------------|
| `ConfigError` | `ValueError` | Chave/config ausente ou inválida | `.kind` (ex. `missing_key`) |
| `InvalidRequestError` | `ValueError` | Pedido/lote rejeitado (incl. esgotamento de validação) | `.kind` (ex. `validation_exhausted`) |
| `GenerationFailedError` | `RuntimeError` | Falha de API/provedor após o pipeline | `.retriable`, `.api_error_kind` |

Não trate `ValueError` genérico como contrato de host para esgotamento de validação — use `InvalidRequestError`.

Diagnósticos internos ainda usam `print` em stderr; o host pode usar `contextlib.redirect_stderr` até LOG-01.

### Contrato sequencial

**Uma geração por vez por processo.** Não há suporte a concorrência nesta fase — não chame `generate_batch` em paralelo no mesmo processo.

### Nomes de módulo reservados

Enquanto o packaging estiver parkado (PKG-01), os módulos flat publicados via `sys.path` colidem com nomes homônimos no host. Reserve / detecte:

`main`, `models`, `prompts`, `validator`, `generator`, `generator_gemini`, `failover`, `reliability`, `reasoning`, `math_check`, `output_paths`, `wizard`, `token_usage`, `service`

Detecção opcional (exemplo): `set(sys.modules) & {"models", "service", ...}` antes de inserir `exercise-ai/` no path.

### Timeout Gemini e pior caso

O client Gemini usa `HttpOptions.timeout=30000` (**milissegundos** ≈ 30s, alinhado ao OpenAI `timeout=30.0`). Em pior caso o host pode esperar **vários minutos**: até `(max_retries+1)` tentativas × até 5 fallbacks de modelo Gemini × um hop de failover × 30s de timeout HTTP — ordem de grandeza, não SLA.

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
