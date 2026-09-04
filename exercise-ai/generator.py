"""LLM Generator — dispatches to OpenAI or Gemini based on environment."""

from __future__ import annotations

import os
import sys

from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    OpenAIError,
    RateLimitError,
)

from models import ExerciseBatch, GenerationRequest
import prompts

_MISSING_KEY_MSG = (
    "Nenhuma chave de API configurada. "
    "Defina GEMINI_API_KEY ou LLM_API_KEY no arquivo .env."
)


def _resolve_provider() -> str:
    """Escolhe o provedor LLM com base em LLM_PROVIDER ou chaves disponíveis."""
    explicit = os.getenv("LLM_PROVIDER", "").strip().lower()
    if explicit in {"openai", "gemini"}:
        return explicit

    has_gemini = bool(os.getenv("GEMINI_API_KEY", "").strip())
    has_openai = bool(os.getenv("LLM_API_KEY", "").strip())

    if has_gemini and not has_openai:
        return "gemini"
    if has_openai and not has_gemini:
        return "openai"
    if has_gemini:
        return "gemini"
    if has_openai:
        return "openai"

    raise ValueError(_MISSING_KEY_MSG)


def get_client() -> OpenAI:
    """Inicializa o cliente OpenAI usando a variável LLM_API_KEY do ambiente."""
    api_key = os.getenv("LLM_API_KEY")
    if not api_key or not api_key.strip():
        raise ValueError(_MISSING_KEY_MSG)
    return OpenAI(api_key=api_key.strip(), timeout=30.0)


def map_openai_error(exc: BaseException) -> RuntimeError:
    """Map typed OpenAI errors to plain-PT RuntimeError; log [API:openai] detail."""
    print(f"[API:openai] {type(exc).__name__}: {exc}", file=sys.stderr)

    if isinstance(exc, APITimeoutError):
        return RuntimeError("Tempo esgotado ao chamar a API da OpenAI.")
    if isinstance(exc, RateLimitError):
        return RuntimeError(
            "Limite de requisições da API da OpenAI atingido. Tente novamente mais tarde."
        )
    if isinstance(exc, APIConnectionError):
        return RuntimeError("Erro de conexão com a API da OpenAI. Verifique a rede.")
    if isinstance(exc, AuthenticationError):
        return RuntimeError(
            "Falha de autenticação na API da OpenAI. Verifique LLM_API_KEY."
        )
    return RuntimeError(f"Erro na chamada à API da OpenAI: {exc}")


def _generate_with_openai(
    request: GenerationRequest,
    model: str = "gpt-4o-mini",
) -> ExerciseBatch:
    """Gera exercícios usando OpenAI Structured Outputs."""
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
            print(
                f"[API:openai] refusal: {message.refusal}",
                file=sys.stderr,
            )
            raise RuntimeError(f"O modelo recusou a geração: {message.refusal}")

        if message.parsed is None:
            print(
                "[API:openai] parsed is None — estrutura ausente na resposta",
                file=sys.stderr,
            )
            raise RuntimeError(
                "Não foi possível obter a estrutura de exercícios da resposta do modelo."
            )

        return message.parsed

    except OpenAIError as exc:
        raise map_openai_error(exc) from exc


def generate_exercises(
    request: GenerationRequest,
    model: str | None = None,
) -> ExerciseBatch:
    """Gera exercícios matemáticos estruturados via OpenAI ou Gemini."""
    provider = _resolve_provider()

    if provider == "gemini":
        from generator_gemini import DEFAULT_GEMINI_MODEL, generate_exercises as generate_gemini

        return generate_gemini(request, model=model or DEFAULT_GEMINI_MODEL)

    return _generate_with_openai(request, model=model or "gpt-4o-mini")
