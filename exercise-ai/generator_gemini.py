"""LLM Generator using Google Gemini structured JSON output.

GEMINI_ERROR_CLASSIFICATION:
priority-1 N/A on this SDK — use status_code table only
Categories (status codes):
- auth: 401/403 → Falha de autenticação na API do Gemini. Verifique GEMINI_API_KEY.
- rate limit: 429 → Limite de requisições da API do Gemini atingido. Tente novamente mais tarde.
- timeout: 408/504 → Tempo esgotado ao chamar a API do Gemini.
- connection/network (message heuristics) → Erro de conexão com a API do Gemini. Verifique a rede.
- generic fallback → Erro na chamada à API do Gemini.
"""

from __future__ import annotations

import json
import os
import sys

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from models import ExerciseBatch, GenerationRequest
import prompts

DEFAULT_GEMINI_MODEL = "gemini-2.5-pro"

_MISSING_KEY_MSG = (
    "Nenhuma chave de API configurada. "
    "Defina GEMINI_API_KEY ou LLM_API_KEY no arquivo .env."
)

_MSG_AUTH = "Falha de autenticação na API do Gemini. Verifique GEMINI_API_KEY."
_MSG_RATE = "Limite de requisições da API do Gemini atingido. Tente novamente mais tarde."
_MSG_TIMEOUT = "Tempo esgotado ao chamar a API do Gemini."
_MSG_CONN = "Erro de conexão com a API do Gemini. Verifique a rede."
_MSG_GENERIC = "Erro na chamada à API do Gemini."

_NETWORK_HINTS = (
    "connection",
    "connect",
    "network",
    "conexão",
    "rede",
    "unreachable",
    "dns",
)


def get_client() -> genai.Client:
    """Inicializa o cliente Gemini usando GEMINI_API_KEY do ambiente."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        raise ValueError(_MISSING_KEY_MSG)
    return genai.Client(api_key=api_key.strip())


def _coerce_status_code(exc: BaseException) -> int | None:
    raw = getattr(exc, "status_code", None)
    if raw is None:
        raw = getattr(exc, "code", None)
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def map_gemini_error(exc: BaseException) -> RuntimeError:
    """Map Gemini API errors via status_code table; log [API:gemini] detail."""
    print(f"[API:gemini] {type(exc).__name__}: {exc}", file=sys.stderr)

    code = _coerce_status_code(exc)
    body = f"{getattr(exc, 'message', '')} {exc}".lower()

    if code in {401, 403}:
        return RuntimeError(_MSG_AUTH)
    if code == 429:
        return RuntimeError(_MSG_RATE)
    if code in {408, 504}:
        return RuntimeError(_MSG_TIMEOUT)
    if any(hint in body for hint in _NETWORK_HINTS):
        return RuntimeError(_MSG_CONN)
    return RuntimeError(_MSG_GENERIC)


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
        raise map_gemini_error(exc) from exc

    if not response.text:
        print("[API:gemini] empty response.text", file=sys.stderr)
        raise RuntimeError("A API do Gemini retornou uma resposta vazia.")

    try:
        return ExerciseBatch.model_validate(json.loads(response.text))
    except (json.JSONDecodeError, ValueError) as exc:
        print(
            f"[API:gemini] unparseable response: {response.text!r}",
            file=sys.stderr,
        )
        raise RuntimeError(
            "Não foi possível interpretar a estrutura de exercícios retornada pelo Gemini."
        ) from exc
