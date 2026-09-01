"""Prompt templates and builders for math exercise generation."""

from models import GenerationRequest

SYSTEM_PROMPT = (
    "Você é um professor especialista na elaboração de exercícios educacionais de matemática no Brasil. "
    "Sua função é gerar exercícios didáticos, precisos, rigorosos e perfeitamente adequados ao nível de dificuldade solicitado. "
    "Respeite estritamente o tópico delimitado, a dificuldade e a quantidade exata de exercícios requerida. "
    "Cada exercício gerado deve conter enunciado claro, resposta final precisa e explicação passo a passo detalhada da resolução. "
    "Retorne estritamente os dados estruturados no formato solicitado, sem textos introdutórios ou conclusivos adicionais."
)

USER_PROMPT_TEMPLATE = (
    "Gere exercícios de matemática com base nos seguintes parâmetros:\n"
    "- Matéria: {materia}\n"
    "- Tópico: {topico}\n"
    "- Dificuldade: {dificuldade}\n"
    "- Quantidade: {quantidade}\n\n"
    "Requisitos obrigatórios:\n"
    "1. Gere exatamente {quantidade} exercício(s).\n"
    "2. Todos os exercícios devem pertencer estritamente ao tópico '{topico}'.\n"
    "3. Para cada exercício, forneça obrigatoriamente:\n"
    "   - enunciado: o texto claro do problema ou questão;\n"
    "   - resposta: o resultado final ou solução direta;\n"
    "   - explicacao: o passo a passo completo da resolução.\n"
    "4. Utilize português brasileiro formal e didático."
)


def build_prompts(request: GenerationRequest) -> tuple[str, str]:
    """Constrói a tupla (system_prompt, user_prompt) formatada a partir de uma requisição."""
    dificuldade_str = (
        request.dificuldade.value
        if hasattr(request.dificuldade, "value")
        else str(request.dificuldade)
    )
    user_prompt = USER_PROMPT_TEMPLATE.format(
        materia=request.materia,
        topico=request.topico,
        dificuldade=dificuldade_str,
        quantidade=request.quantidade,
    )
    return SYSTEM_PROMPT, user_prompt
