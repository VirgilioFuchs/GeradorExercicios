"""LLM Generator using OpenAI Structured Outputs."""

import os
from openai import OpenAI, OpenAIError
from models import ExerciseBatch, GenerationRequest
import prompts


def get_client() -> OpenAI:
    """Inicializa o cliente OpenAI usando a variável LLM_API_KEY do ambiente."""
    api_key = os.getenv("LLM_API_KEY")
    if not api_key or not api_key.strip():
        raise ValueError(
            "Chave de API não configurada. Defina a variável LLM_API_KEY no arquivo .env."
        )
    return OpenAI(api_key=api_key.strip(), timeout=30.0)


def generate_exercises(request: GenerationRequest, model: str = "gpt-4o-mini") -> ExerciseBatch:
    """Gera exercícios matemáticos estruturados usando OpenAI Structured Outputs."""
    client = get_client()
    system_prompt, user_prompt = prompts.build_prompts(request)

    try:
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=ExerciseBatch,
        )

        message = completion.choices[0].message

        if message.refusal:
            raise RuntimeError(f"O modelo recusou a geração: {message.refusal}")

        if message.parsed is None:
            raise RuntimeError("Não foi possível obter a estrutura de exercícios da resposta do modelo.")

        return message.parsed

    except OpenAIError as exc:
        raise RuntimeError(f"Erro na chamada à API da OpenAI: {exc}") from exc
