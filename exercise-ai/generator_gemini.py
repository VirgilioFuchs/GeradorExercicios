"""LLM Generator using Google Gemini structured JSON output.

GEMINI_ERROR_CLASSIFICATION:
priority-1 N/A on this SDK — use status_code table only
Categories (status codes):
- auth: 401/403 → Falha de autenticação na API do Gemini. Verifique GEMINI_API_KEY.
- rate limit: 429 → Limite de requisições da API do Gemini atingido. Tente novamente mais tarde.
- timeout: 408/504 → Tempo esgotado ao chamar a API do Gemini.
- connection/network (message heuristics) → Erro de conexão com a API do Gemini. Verifique a rede.
- generic fallback → Erro na chamada à API do Gemini.

On usage/capacity errors (429/503/quota/overload), try the next model in
GEMINI_MODEL_FALLBACKS before surfacing the mapped error.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from models import ExerciseBatch, GenerationRequest
import prompts
from token_usage import extract_gemini_usage, get_collector

# Prefer lite; on usage/capacity errors walk the list.
GEMINI_MODEL_FALLBACKS: tuple[str, ...] = (
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
)
DEFAULT_GEMINI_MODEL = GEMINI_MODEL_FALLBACKS[0]

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

_USAGE_BODY_HINTS = (
    "resource_exhausted",
    "quota",
    "rate limit",
    "rate_limit",
    "too many requests",
    "overloaded",
    "unavailable",
    "no longer available",
    "high demand",
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
    if raw is not None:
        try:
            return int(raw)
        except (TypeError, ValueError):
            pass
    # Some SDK ClientErrors leave status_code unset but embed it in message.
    blob = f"{getattr(exc, 'message', '')} {exc}"
    match = re.search(r"\b([45]\d{2})\b", blob)
    if match:
        return int(match.group(1))
    return None


def _redact_env_secrets(text: str) -> str:
    """Replace live env API key values so debug dumps never echo secrets."""
    for name in ("LLM_API_KEY", "GEMINI_API_KEY"):
        val = os.getenv(name, "")
        if val and val.strip() and val in text:
            text = text.replace(val, "[REDACTED]")
    return text


def _gemini_error_detail(exc: BaseException) -> str:
    """Build sanitized [API:gemini] detail: type + status/code only (no raw str(exc))."""
    parts = [type(exc).__name__]
    code = _coerce_status_code(exc)
    if code is not None:
        parts.append(f"status={code}")
    return " ".join(parts)


def invalid_llm_response(msg: str) -> RuntimeError:
    """Typed invalid-response RuntimeError — retriable for reliability loop (D-19)."""
    err = RuntimeError(msg)
    err.retriable = True
    return err


def _permanent_api_error(msg: str) -> RuntimeError:
    """Auth/timeout/rate-limit/connection/generic mapped — not retriable (D-06)."""
    err = RuntimeError(msg)
    err.retriable = False
    return err


def _is_usage_capacity_error(exc: BaseException) -> bool:
    """True when another model in the fallback list may still succeed."""
    body = f"{getattr(exc, 'message', '')} {exc}".lower()
    # Real network failures won't be fixed by switching model ids.
    if any(hint in body for hint in _NETWORK_HINTS):
        return False
    code = _coerce_status_code(exc)
    if code in {429, 500, 502, 503, 404}:
        return True
    return any(hint in body for hint in _USAGE_BODY_HINTS)


def _model_candidates(preferred: str) -> list[str]:
    """Preferred first, then remaining GEMINI_MODEL_FALLBACKS (deduped)."""
    ordered: list[str] = [preferred]
    for name in GEMINI_MODEL_FALLBACKS:
        if name not in ordered:
            ordered.append(name)
    return ordered


def map_gemini_error(exc: BaseException) -> RuntimeError:
    """Map Gemini API/transport errors via status_code table; log [API:gemini] detail."""
    print(f"[API:gemini] {_gemini_error_detail(exc)}", file=sys.stderr)

    code = _coerce_status_code(exc)
    # Classification may read message/str for network heuristics only — never log it.
    body = f"{getattr(exc, 'message', '')} {exc}".lower()

    if code in {401, 403}:
        return _permanent_api_error(_MSG_AUTH)
    if code == 429:
        return _permanent_api_error(_MSG_RATE)
    if code in {408, 504}:
        return _permanent_api_error(_MSG_TIMEOUT)
    if any(hint in body for hint in _NETWORK_HINTS):
        return _permanent_api_error(_MSG_CONN)
    return _permanent_api_error(_MSG_GENERIC)


def _parse_gemini_response(response: object) -> ExerciseBatch:
    text = getattr(response, "text", None)
    if not text:
        print("[API:gemini] empty response.text", file=sys.stderr)
        raise invalid_llm_response("A API do Gemini retornou uma resposta vazia.")

    try:
        return ExerciseBatch.model_validate(json.loads(text))
    except (json.JSONDecodeError, ValueError) as exc:
        safe_preview = _redact_env_secrets(repr(text))
        print(
            f"[API:gemini] unparseable response: {safe_preview}",
            file=sys.stderr,
        )
        raise invalid_llm_response(
            "Não foi possível interpretar a estrutura de exercícios retornada pelo Gemini."
        ) from exc


def _record_gemini_usage(
    *,
    response: object | None,
    model: str,
    status: str,
    duration_ms: int,
    error_kind: str | None = None,
) -> None:
    if response is not None:
        fields = extract_gemini_usage(response, model=model)
        get_collector().record(
            provider="gemini",
            model=model,
            status=status,  # type: ignore[arg-type]
            prompt_tokens=fields.prompt_tokens,
            completion_tokens=fields.completion_tokens,
            total_tokens=fields.total_tokens,
            duration_ms=duration_ms,
            usd=fields.usd,
            usd_source=fields.usd_source,
            error_kind=error_kind,
        )
    else:
        get_collector().record(
            provider="gemini",
            model=model,
            status=status,  # type: ignore[arg-type]
            duration_ms=duration_ms,
            error_kind=error_kind,
        )


def generate_exercises(
    request: GenerationRequest,
    model: str = DEFAULT_GEMINI_MODEL,
) -> ExerciseBatch:
    """Gera exercícios matemáticos estruturados usando Google Gemini.

    Em erro de uso/capacidade (429/503/quota/etc.), tenta o próximo modelo
    em ``GEMINI_MODEL_FALLBACKS`` antes de falhar.
    """
    client = get_client()
    system_prompt, user_prompt = prompts.build_prompts(request)
    prompt = f"{system_prompt}\n\n{user_prompt}"
    candidates = _model_candidates(model)
    last_exc: BaseException | None = None

    for idx, candidate in enumerate(candidates):
        t0 = time.perf_counter()
        response = None
        try:
            response = client.models.generate_content(
                model=candidate,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=ExerciseBatch.model_json_schema(),
                ),
            )
        except genai_errors.APIError as exc:
            duration_ms = int((time.perf_counter() - t0) * 1000)
            last_exc = exc
            if _is_usage_capacity_error(exc) and idx < len(candidates) - 1:
                _record_gemini_usage(
                    response=None,
                    model=candidate,
                    status="attempt",
                    duration_ms=duration_ms,
                    error_kind=type(exc).__name__,
                )
                print(
                    f"[API:gemini] uso/capacidade em {candidate}; "
                    f"tentando {candidates[idx + 1]}",
                    file=sys.stderr,
                )
                continue
            _record_gemini_usage(
                response=None,
                model=candidate,
                status="error",
                duration_ms=duration_ms,
                error_kind=type(exc).__name__,
            )
            raise map_gemini_error(exc) from exc
        except Exception as exc:
            duration_ms = int((time.perf_counter() - t0) * 1000)
            last_exc = exc
            if _is_usage_capacity_error(exc) and idx < len(candidates) - 1:
                _record_gemini_usage(
                    response=None,
                    model=candidate,
                    status="attempt",
                    duration_ms=duration_ms,
                    error_kind=type(exc).__name__,
                )
                print(
                    f"[API:gemini] uso/capacidade em {candidate}; "
                    f"tentando {candidates[idx + 1]}",
                    file=sys.stderr,
                )
                continue
            _record_gemini_usage(
                response=None,
                model=candidate,
                status="error",
                duration_ms=duration_ms,
                error_kind=type(exc).__name__,
            )
            raise map_gemini_error(exc) from exc

        duration_ms = int((time.perf_counter() - t0) * 1000)
        if candidate != model:
            print(f"[API:gemini] modelo usado: {candidate}", file=sys.stderr)
        try:
            batch = _parse_gemini_response(response)
        except RuntimeError as exc:
            kind = "empty_response" if "vazia" in str(exc) else "unparseable"
            _record_gemini_usage(
                response=response,
                model=candidate,
                status="error",
                duration_ms=duration_ms,
                error_kind=kind,
            )
            raise
        _record_gemini_usage(
            response=response,
            model=candidate,
            status="success",
            duration_ms=duration_ms,
        )
        return batch

    assert last_exc is not None
    raise map_gemini_error(last_exc) from last_exc
