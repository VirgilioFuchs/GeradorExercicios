# AGENT.md

## Objetivo do projeto

Construir uma implementação simples de IA para geração de exercícios de matemática.

O foco inicial NÃO é criar um sistema multiagente complexo. A primeira versão deve ser pequena, clara e fácil de evoluir.

A arquitetura deve começar com:

```text
Entrada do usuário
   ↓
Prompt estruturado
   ↓
LLM
   ↓
JSON estruturado
   ↓
Validação
   ↓
Exercícios
```

Depois o projeto poderá evoluir para uso de MySQL, análise de desempenho do aluno e, futuramente, um agente com ciclo de decisão.

---

## Escopo da primeira versão

Implementar um MVP em Python com:

- geração de exercícios de matemática via LLM;
- entrada contendo:
  - matéria;
  - tópico;
  - dificuldade;
  - quantidade;
- saída estruturada em JSON;
- cada exercício deve conter:
  - enunciado;
  - resposta;
  - explicação;
- validação básica da estrutura recebida;
- separação clara entre geração, prompts, modelos e validação.

Não adicionar frameworks de agentes neste momento.

Evitar inicialmente:

- LangChain;
- CrewAI;
- AutoGen;
- sistemas multiagentes;
- RAG;
- banco vetorial;
- filas;
- microsserviços;
- abstrações desnecessárias.

A ideia é entender primeiro o funcionamento fundamental.

---

## Estrutura sugerida

```text
exercise-ai/
│
├── main.py
├── generator.py
├── validator.py
├── prompts.py
├── models.py
├── requirements.txt
├── .env.example
└── README.md
```

### `main.py`

Responsável por:

- receber ou definir os parâmetros de entrada;
- chamar o gerador;
- executar a validação;
- exibir o resultado final;
- tratar erros de alto nível.

### `generator.py`

Responsável exclusivamente por:

- montar a requisição para o LLM;
- usar o prompt definido em `prompts.py`;
- enviar os parâmetros;
- receber a resposta;
- converter a resposta para a estrutura esperada.

Não colocar regras de negócio complexas aqui.

### `validator.py`

Responsável por validar:

- se o JSON é válido;
- se existe a chave `exercicios`;
- se a quantidade retornada é a solicitada;
- se cada exercício contém:
  - `enunciado`;
  - `resposta`;
  - `explicacao`;
- se campos obrigatórios estão vazios.

Preparar a estrutura para futura validação matemática.

### `prompts.py`

Centralizar templates de prompt.

O prompt deve instruir o modelo a:

- gerar apenas exercícios do tópico informado;
- respeitar a dificuldade;
- respeitar a quantidade;
- evitar conteúdo fora do escopo;
- retornar exclusivamente a estrutura solicitada;
- não inserir comentários fora do JSON.

### `models.py`

Definir as estruturas de dados.

Exemplo conceitual:

```python
class Exercise:
    statement: str
    answer: str
    explanation: str
```

Pode ser usado `dataclass`, `TypedDict`, Pydantic ou estrutura equivalente.

Para o MVP, preferir a solução mais simples e legível.

---

## Estrutura esperada da entrada

Exemplo:

```json
{
  "materia": "Matemática",
  "topico": "Equação do primeiro grau",
  "dificuldade": "facil",
  "quantidade": 3
}
```

---

## Estrutura esperada da saída

```json
{
  "exercicios": [
    {
      "enunciado": "Resolva: 2x + 4 = 10",
      "resposta": "x = 3",
      "explicacao": "Subtraia 4 dos dois lados e depois divida por 2."
    }
  ]
}
```

A resposta do modelo não deve conter texto fora dessa estrutura.

---

## Prompt inicial

Usar um prompt simples e explícito.

Exemplo de direção:

```text
Você é um gerador de exercícios de matemática.

Matéria: {materia}
Tópico: {topico}
Dificuldade: {dificuldade}
Quantidade: {quantidade}

Crie exatamente a quantidade solicitada de exercícios.

Cada exercício deve conter:
- enunciado;
- resposta;
- explicação.

Retorne somente JSON válido no formato especificado.
Não escreva nenhum texto antes ou depois do JSON.
```

Se a API/modelo utilizado oferecer Structured Outputs ou schema JSON nativo, preferir esse recurso em vez de depender apenas do texto do prompt.

---

## Regras de implementação

### Simplicidade

Aplicar YAGNI.

Não criar abstrações para problemas que ainda não existem.

### Responsabilidade única

Cada arquivo deve ter uma responsabilidade clara.

### DRY

Evitar duplicação de:

- prompts;
- validações;
- configurações;
- chamadas de API.

### Configuração

Chaves de API nunca devem ser hardcoded.

Usar variável de ambiente.

Exemplo:

```env
LLM_API_KEY=
```

Adicionar `.env` ao `.gitignore`.

Manter `.env.example` sem segredos.

### Tratamento de erro

Tratar pelo menos:

- chave de API ausente;
- erro de rede;
- timeout;
- rate limit;
- resposta vazia;
- JSON inválido;
- estrutura inválida;
- quantidade incorreta de exercícios.

Não esconder exceções silenciosamente.

Os erros devem ser claros para desenvolvimento.

---

## Validação

A geração de um LLM não deve ser tratada automaticamente como correta.

Fluxo desejado:

```text
LLM
 ↓
Resposta
 ↓
Validação estrutural
 ↓
válido?
 ├── sim → retornar
 └── não → erro ou tentativa controlada de regeneração
```

No MVP, implementar validação estrutural.

Mais adiante será implementada validação matemática.

---

## Política de retries

Não criar loop infinito.

Se houver regeneração automática:

- máximo de 1 ou 2 novas tentativas;
- registrar o motivo da falha;
- após o limite, encerrar com erro explícito.

---

## Logs

Criar logs simples para desenvolvimento.

Registrar:

- início da geração;
- tópico;
- dificuldade;
- quantidade;
- sucesso ou falha;
- motivo da validação falhar;
- duração da chamada, se simples de medir.

Não registrar:

- chave de API;
- segredos;
- dados sensíveis.

---

## Testes mínimos

Criar testes para o validador.

Casos importantes:

1. JSON válido;
2. JSON inválido;
3. chave `exercicios` ausente;
4. exercício sem resposta;
5. exercício sem explicação;
6. quantidade diferente da solicitada;
7. lista vazia.

Os testes de validação não devem depender de chamadas reais ao LLM.

Se necessário, usar respostas simuladas.

---

## Critério de pronto da primeira etapa

A primeira versão está pronta quando for possível executar algo equivalente a:

```bash
python main.py
```

e obter uma saída semelhante a:

```json
{
  "exercicios": [
    {
      "enunciado": "Resolva: x + 4 = 9",
      "resposta": "x = 5",
      "explicacao": "Subtraia 4 dos dois lados."
    }
  ]
}
```

com:

- JSON válido;
- tratamento de erro;
- validação estrutural;
- código separado por responsabilidades;
- chave de API fora do código.

---

# Evolução planejada

## Etapa 1 — Gerador simples

```text
Entrada
 ↓
LLM
 ↓
Exercício
```

## Etapa 2 — Validação

```text
Entrada
 ↓
LLM
 ↓
Exercício
 ↓
Validador
```

## Etapa 3 — MySQL

Adicionar persistência para:

- alunos;
- exercícios;
- respostas;
- notas;
- tentativas.

MySQL deve ser usado para os dados transacionais do projeto.

## Etapa 4 — Análise de desempenho

Fluxo futuro:

```text
MySQL
 ↓
notas do aluno
 ↓
identificar tópicos com pior desempenho
 ↓
selecionar tópico e dificuldade
 ↓
gerar exercício
```

## Etapa 5 — Personalização

Usar dados como:

- acertos;
- erros;
- nível;
- tópico;
- histórico recente.

Evitar enviar todo o histórico ao modelo sem necessidade.

Enviar apenas o contexto relevante.

## Etapa 6 — Agente

Somente depois das etapas anteriores.

Fluxo conceitual:

```text
Objetivo
 ↓
LLM
 ↓
decide próxima ação
 ↓
ferramenta
 ↓
observação
 ↓
LLM
 ↓
nova decisão
```

Possíveis ferramentas futuras:

- consultar notas no MySQL;
- buscar tópicos com pior desempenho;
- gerar exercício;
- validar exercício;
- salvar resultado;
- atualizar desempenho.

---

# Regra importante sobre agente

Não chamar a primeira versão de agente se ela apenas fizer:

```text
prompt → LLM → resposta
```

Ela é uma aplicação com LLM.

Considerar agente quando o modelo passar a controlar um workflow, decidir ações e utilizar ferramentas durante um ciclo.

---

# Diretriz para o Cursor

Ao desenvolver:

1. analisar primeiro o estado atual do projeto;
2. propor mudanças pequenas;
3. evitar reescrita desnecessária;
4. não adicionar dependências sem justificar;
5. explicar brevemente decisões arquiteturais importantes;
6. manter o código didático e legível;
7. implementar uma etapa por vez;
8. rodar testes após alterações relevantes;
9. informar claramente arquivos alterados;
10. não avançar automaticamente para MySQL ou agente antes do MVP funcionar.

Se uma decisão puder ser resolvida de forma simples ou complexa, escolher inicialmente a solução simples, desde que ela não comprometa segurança ou correção.

---

# Princípio central

O objetivo deste projeto não é apenas obter exercícios gerados.

O projeto também deve servir para estudar, de forma incremental:

- chamadas a LLM;
- prompt engineering;
- structured output;
- validação;
- confiabilidade;
- observabilidade;
- MySQL;
- ferramentas;
- agent loop;
- memória;
- avaliação;
- segurança.

Cada evolução deve tornar esses conceitos visíveis no código, em vez de escondê-los atrás de frameworks.
