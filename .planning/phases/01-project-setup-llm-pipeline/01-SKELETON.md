# Walking Skeleton — Gerador de Exercícios com IA

**Phase:** 1
**Generated:** 2026-09-01

## Capability Proven End-to-End

O usuário executa o pipeline via CLI (`python exercise-ai/main.py`), enviando parâmetros matemáticos (`materia`, `topico`, `dificuldade`, `quantidade`) para a API OpenAI via Structured Outputs, recebendo como saída no terminal um JSON formatado contendo uma lista de exercícios com `enunciado`, `resposta` e `explicacao` em português brasileiro.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| LLM Client & Protocol | OpenAI Python SDK (`>=1.50.0`) com Structured Outputs (`client.beta.chat.completions.parse`) | Garante aderência estrita de 100% ao schema JSON sem parsing manual frágil ou markdown stripping. |
| LLM Model | `gpt-4o-mini` | Baixo custo, baixa latência e suporte nativo a schemas estruturados estritos. |
| Schema & Data Models | Pydantic v2 (`BaseModel`, `Field`, `str, Enum`) | Fonte única de verdade para tipos Python e geração de JSON schema compatível com OpenAI. |
| Configuration & Secrets | `python-dotenv` lendo `LLM_API_KEY` de `.env` | Segurança (chaves fora do código/git) e flexibilidade para execução local e CI. |
| Directory Layout | Subdiretório `exercise-ai/` com módulos dedicados | Separação explícita de responsabilidades (`main.py`, `generator.py`, `validator.py`, `prompts.py`, `models.py`) conforme `AGENT.md`. |
| Validation Strategy | Validador em duas fases (stub de tipo na Fase 1; validação estrutural profunda na Fase 2) | Permite validar o tracer slice completo no MVP sem misturar complexidade de regras antes da geração estar operacional. |
| CLI Output & Encoding | `json.dumps(..., indent=2, ensure_ascii=False)` em stdout | Garante renderização legível de caracteres acentuados em português brasileiro sem escapes `\uXXXX`. |

## Stack Touched in Phase 1

- [x] Project scaffold (`requirements.txt`, `.gitignore`, `.env.example`, `models.py`)
- [x] Prompt engine (`prompts.py` centralizando templates didáticos em português)
- [x] LLM Integration (`generator.py` chamando OpenAI Structured Outputs com `gpt-4o-mini`)
- [x] Validation Stub (`validator.py` para verificação básica de tipo e não-vazio)
- [x] CLI / Pipeline Runner (`main.py` com carregamento de `.env`, orquestração do fluxo e saída JSON)

## Out of Scope (Deferred to Later Slices)

O Walking Skeleton foca estritamente na menor capacidade ponta a ponta funcional. Foram explicitamente postergados:

- **Validação estrutural profunda:** Verificação de contagem exata, campos vazios e códigos específicos de erro (Fase 2)
- **Tratamento avançado de resiliência:** Retries automáticos (1–2 tentativas) e backoff exponencial (v2 / Fase 2+)
- **Testes automatizados unitários:** Testes do validador com mocks em pytest sem chamadas reais (Fase 3)
- **Observabilidade:** Logging estruturado e medição de latência da chamada (Fase 3)
- **Documentação de onboarding:** README detalhado de instalação e uso (Fase 3)
- **Argumentos de linha de comando:** Parser CLI interativo com `argparse` / `click` (v2)
- **Validação matemática:** Verificação matemática independente de enunciados e respostas (v2)
- **Persistência de dados:** Banco relacional MySQL para alunos, exercícios e notas (v2)
- **Agente autônomo:** Loop de decisão com uso de ferramentas e memória contextual (v2)

## Subsequent Slice Plan

Cada fase posterior adiciona uma fatia vertical sobre este skeleton sem quebrar suas decisões arquiteturais:

- **Phase 2 (Validation & Error Handling):** Transforma o stub `validator.py` em um validador estrutural robusto e adiciona tratamento granular para falhas de rede, recusa de modelo e JSON malformado.
- **Phase 3 (Tests, Logging & Docs):** Adiciona suite de testes unitários isolados com `pytest`, módulo de logging sem vazamento de segredos e documentação `README.md`.
- **v2 Milestones (Persistence, Analytics & Agent):** Adiciona camada MySQL, histórico de erros e loop de agente orientado a metas.
