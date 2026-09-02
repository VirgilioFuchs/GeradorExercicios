"""LLM Generator using Google Gemini structured JSON output."""

import json
import os

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from models import ExerciseBatch, GenerationRequest
import prompts

DEFAULT_GEMINI_MODEL = "gemini-2.5-pro"


def get_client() -> genai.Client:
    """Inicializa o cliente Gemini usando GEMINI_API_KEY do ambiente."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        raise ValueError(
            "Chave de API do Gemini não configurada. "
            "Defina a variável GEMINI_API_KEY no arquivo .env."
        )
    return genai.Client(api_key=api_key.strip())


def generate_exercises(
    request: GenerationRequest,
    model: str = DEFAULT_GEMINI_MODEL,
) -> ExerciseBatch:
    """Gera exercícios matemáticos estruturados usando Google Gemini."""
    client = get_client()
    system_prompt, user_prompt = prompts.build_prompts(request)
    prompt = f"{system_prompt}\n\n{user_prompt}"

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=ExerciseBatch.model_json_schema(),
            ),
        )
    except genai_errors.APIError as exc:
        raise RuntimeError(f"Erro na chamada à API do Gemini: {exc}") from exc

    if not response.text:
        raise RuntimeError("A API do Gemini retornou uma resposta vazia.")

    try:
        return ExerciseBatch.model_validate(json.loads(response.text))
    except (json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError(
            "Não foi possível interpretar a estrutura de exercícios retornada pelo Gemini."
        ) from exc
