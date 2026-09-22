"""Prompt templates and builders for math exercise generation."""

from models import DificuldadeEnum, GenerationRequest

SYSTEM_PROMPT = (
    "Você é um professor especialista na elaboração de exercícios educacionais de matemática no Brasil. "
    "Sua função é gerar exercícios didáticos, precisos, rigorosos e perfeitamente adequados ao nível de dificuldade solicitado. "
    "Respeite estritamente o tópico delimitado, a dificuldade e a quantidade exata de exercícios requerida. "
    "Cada exercício gerado deve conter enunciado claro, resposta final precisa e explicação passo a passo detalhada da resolução. "
    "Retorne estritamente os dados estruturados no formato solicitado, sem textos introdutórios ou conclusivos adicionais."
)

_HYBRID_LABELS: dict[DificuldadeEnum, str] = {
    DificuldadeEnum.FACIL: "fácil (facil)",
    DificuldadeEnum.MEDIO: "médio (medio)",
    DificuldadeEnum.DIFICIL: "difícil (dificil)",
}

USER_PROMPT_TEMPLATE = (
    "Gere exercícios de matemática com base nos seguintes parâmetros:\n"
    "- Matéria: {materia}\n"
    "- Tópico: {topico}\n"
    "- Quantidade: {quantidade}\n\n"
    "Plano de dificuldade por exercício (slot → faixa):\n"
    "{slot_list}\n\n"
    "Requisitos obrigatórios:\n"
    "1. Gere exatamente {quantidade} exercício(s), um por slot acima, "
    "respeitando a dificuldade indicada em cada linha.\n"
    "2. Todos os exercícios devem pertencer estritamente ao tópico '{topico}'.\n"
    "3. Utilize português brasileiro formal e didático.\n"
    "4. No lote, o campo dificuldades é o resumo das faixas distintas usadas "
    "(ordem fácil→médio→difícil), não um valor por exercício."
)


def _format_slot_list(request: GenerationRequest) -> str:
    """Numbered 1-based hybrid labels from itens_ordenados (D-01..D-04)."""
    lines = [
        f"{i}. {_HYBRID_LABELS[spec.dificuldade]}"
        for i, spec in enumerate(request.itens_ordenados, start=1)
    ]
    return "\n".join(lines)


def build_prompts(request: GenerationRequest) -> tuple[str, str]:
    """Constrói a tupla (system_prompt, user_prompt) formatada a partir de uma requisição."""
    user_prompt = USER_PROMPT_TEMPLATE.format(
        materia=request.materia,
        topico=request.topico,
        quantidade=request.quantidade,
        slot_list=_format_slot_list(request),
    )
    return SYSTEM_PROMPT, user_prompt
