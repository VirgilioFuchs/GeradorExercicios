"""LLM Generator — dispatches to OpenAI, Gemini, or Grok based on environment."""

from __future__ import annotations

import os
import sys
import time

from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    OpenAIError,
    RateLimitError,
)

from model_catalog import (
    DEFAULT_GROK_MODEL,
    DEFAULT_OPENAI_MODEL,
    GROK_MODEL_FALLBACKS,
    OPENAI_MODEL_FALLBACKS,
    model_candidates,
)
from models import ExerciseBatch, GenerationRequest
import prompts
from reasoning import openai_compatible_effort_kwargs
from token_usage import (
    extract_grok_usage,
    extract_openai_usage,
    get_collector,
)

_MISSING_KEY_MSG = (
    "Nenhuma chave de API configurada. "
    "Defina GEMINI_API_KEY, LLM_API_KEY ou GROK_API_KEY no arquivo .env."
)

_GROK_BASE_URL = "https://api.x.ai/v1"

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
    "model_not_found",
)


def _resolve_provider() -> str:
    """Escolhe o provedor LLM com base em LLM_PROVIDER ou chaves disponíveis."""
    explicit = os.getenv("LLM_PROVIDER", "").strip().lower()
    if explicit in {"openai", "gemini", "grok"}:
        return explicit

    # Prefer Gemini, then OpenAI, then Grok when multiple keys exist.
    if os.getenv("GEMINI_API_KEY", "").strip():
        return "gemini"
    if os.getenv("LLM_API_KEY", "").strip():
        return "openai"
    if os.getenv("GROK_API_KEY", "").strip():
        return "grok"

    from service import ConfigError

    raise ConfigError(_MISSING_KEY_MSG, kind="missing_key")


def get_client() -> OpenAI:
    """Inicializa o cliente OpenAI usando a variável LLM_API_KEY do ambiente."""
    from service import ConfigError

    api_key = os.getenv("LLM_API_KEY")
    if not api_key or not api_key.strip():
        raise ConfigError(_MISSING_KEY_MSG, kind="missing_key")
    return OpenAI(api_key=api_key.strip(), timeout=30.0)


def get_grok_client() -> OpenAI:
    """Inicializa cliente OpenAI-compatible apontando para a API xAI (Grok)."""
    from service import ConfigError

    api_key = os.getenv("GROK_API_KEY")
    if not api_key or not api_key.strip():
        raise ConfigError(_MISSING_KEY_MSG, kind="missing_key")
    return OpenAI(
        api_key=api_key.strip(),
        base_url=_GROK_BASE_URL,
        timeout=30.0,
    )


def _redact_env_secrets(text: str) -> str:
    """Replace live env API key values so debug dumps never echo secrets."""
    for name in ("LLM_API_KEY", "GEMINI_API_KEY", "GROK_API_KEY"):
        val = os.getenv(name, "")
        if val and val.strip() and val in text:
            text = text.replace(val, "[REDACTED]")
    return text


def _openai_error_detail(exc: BaseException) -> str:
    """Build sanitized API detail: type + status/code only (no raw str(exc))."""
    parts = [type(exc).__name__]
    status = getattr(exc, "status_code", None)
    if status is None:
        status = getattr(exc, "code", None)
    if status is not None:
        parts.append(f"status={status}")
    return " ".join(parts)


def invalid_llm_response(msg: str) -> GenerationFailedError:
    """Typed invalid-response error — retriable for reliability loop (D-19)."""
    from service import GenerationFailedError

    return GenerationFailedError(msg, retriable=True)


def _permanent_api_error(msg: str, *, api_error_kind: str) -> GenerationFailedError:
    """Auth/timeout/rate-limit/connection/refusal — not retriable (D-06)."""
    from service import GenerationFailedError

    return GenerationFailedError(
        msg, retriable=False, api_error_kind=api_error_kind
    )


def map_openai_compatible_error(
    exc: BaseException,
    *,
    api_tag: str,
    of_label: str,
    auth_key_name: str,
) -> GenerationFailedError:
    """Map typed OpenAI-SDK errors to plain-PT RuntimeError; log [API:{tag}] detail."""
    print(f"[API:{api_tag}] {_openai_error_detail(exc)}", file=sys.stderr)

    if isinstance(exc, APITimeoutError):
        return _permanent_api_error(
            f"Tempo esgotado ao chamar a API {of_label}.",
            api_error_kind="timeout",
        )
    if isinstance(exc, RateLimitError):
        return _permanent_api_error(
            f"Limite de requisições da API {of_label} atingido. Tente novamente mais tarde.",
            api_error_kind="rate_limit",
        )
    if isinstance(exc, APIConnectionError):
        return _permanent_api_error(
            f"Erro de conexão com a API {of_label}. Verifique a rede.",
            api_error_kind="connection",
        )
    if isinstance(exc, AuthenticationError):
        return _permanent_api_error(
            f"Falha de autenticação na API {of_label}. Verifique {auth_key_name}.",
            api_error_kind="auth",
        )
    return _permanent_api_error(
        f"Erro na chamada à API {of_label}.",
        api_error_kind="generic",
    )


def map_openai_error(exc: BaseException) -> GenerationFailedError:
    """Map typed OpenAI errors to GenerationFailedError; log [API:openai] detail."""
    return map_openai_compatible_error(
        exc,
        api_tag="openai",
        of_label="da OpenAI",
        auth_key_name="LLM_API_KEY",
    )


def _record_openai_compatible_usage(
    *,
    completion: object | None,
    provider: str,
    model: str,
    status: str,
    duration_ms: int,
    error_kind: str | None = None,
) -> None:
    """Record one usage event for OpenAI or Grok (D-13); extract per provider."""
    if completion is not None:
        if provider == "grok":
            fields = extract_grok_usage(completion, model=model)
        else:
            fields = extract_openai_usage(completion, model=model)
        get_collector().record(
            provider=provider,
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
            provider=provider,
            model=model,
            status=status,  # type: ignore[arg-type]
            duration_ms=duration_ms,
            error_kind=error_kind,
        )


def _is_openai_usage_capacity_error(exc: BaseException) -> bool:
    """True when another model in the fallback list may still succeed."""
    if isinstance(exc, RateLimitError):
        return True
    status = getattr(exc, "status_code", None)
    if status is None:
        status = getattr(exc, "code", None)
    try:
        code = int(status) if status is not None else None
    except (TypeError, ValueError):
        code = None
    if code in {429, 500, 502, 503, 404}:
        return True
    body = f"{exc}".lower()
    return any(hint in body for hint in _USAGE_BODY_HINTS)


def _generate_with_openai_compatible(
    request: GenerationRequest,
    *,
    client: OpenAI,
    model: str,
    api_tag: str,
    of_label: str,
    auth_key_name: str,
    fallbacks: tuple[str, ...],
) -> ExerciseBatch:
    """Gera exercícios via Structured Outputs; fallback em erros de uso/capacidade."""
    system_prompt, user_prompt = prompts.build_prompts(request)
    candidates = model_candidates(model, fallbacks)
    last_exc: BaseException | None = None

    for idx, candidate in enumerate(candidates):
        t0 = time.perf_counter()
        completion = None
        effort_kwargs = openai_compatible_effort_kwargs(api_tag=api_tag, model=candidate)

        try:
            completion = client.beta.chat.completions.parse(
                model=candidate,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=ExerciseBatch,
                **effort_kwargs,
            )
            duration_ms = int((time.perf_counter() - t0) * 1000)

            if not getattr(completion, "choices", None):
                print(f"[API:{api_tag}] empty choices", file=sys.stderr)
                _record_openai_compatible_usage(
                    completion=completion,
                    provider=api_tag,
                    model=candidate,
                    status="error",
                    duration_ms=duration_ms,
                    error_kind="empty_choices",
                )
                raise invalid_llm_response(
                    "Não foi possível obter a estrutura de exercícios da resposta do modelo."
                )

            message = completion.choices[0].message

            if message.refusal:
                safe_refusal = _redact_env_secrets(str(message.refusal))
                print(
                    f"[API:{api_tag}] refusal: {safe_refusal}",
                    file=sys.stderr,
                )
                _record_openai_compatible_usage(
                    completion=completion,
                    provider=api_tag,
                    model=candidate,
                    status="error",
                    duration_ms=duration_ms,
                    error_kind="refusal",
                )
                raise _permanent_api_error(
                    f"O modelo recusou a geração: {safe_refusal}",
                    api_error_kind="refusal",
                )

            if message.parsed is None:
                print(
                    f"[API:{api_tag}] parsed is None — estrutura ausente na resposta",
                    file=sys.stderr,
                )
                _record_openai_compatible_usage(
                    completion=completion,
                    provider=api_tag,
                    model=candidate,
                    status="error",
                    duration_ms=duration_ms,
                    error_kind="parsed_none",
                )
                raise invalid_llm_response(
                    "Não foi possível obter a estrutura de exercícios da resposta do modelo."
                )

            _record_openai_compatible_usage(
                completion=completion,
                provider=api_tag,
                model=candidate,
                status="success",
                duration_ms=duration_ms,
            )
            return message.parsed

        except OpenAIError as exc:
            duration_ms = int((time.perf_counter() - t0) * 1000)
            last_exc = exc
            if _is_openai_usage_capacity_error(exc) and idx < len(candidates) - 1:
                _record_openai_compatible_usage(
                    completion=completion,
                    provider=api_tag,
                    model=candidate,
                    status="attempt",
                    duration_ms=duration_ms,
                    error_kind=type(exc).__name__,
                )
                print(
                    f"[API:{api_tag}] uso/capacidade em {candidate}; "
                    f"tentando {candidates[idx + 1]}",
                    file=sys.stderr,
                )
                continue
            _record_openai_compatible_usage(
                completion=completion,
                provider=api_tag,
                model=candidate,
                status="error",
                duration_ms=duration_ms,
                error_kind=type(exc).__name__,
            )
            raise map_openai_compatible_error(
                exc,
                api_tag=api_tag,
                of_label=of_label,
                auth_key_name=auth_key_name,
            ) from exc

    assert last_exc is not None
    raise map_openai_compatible_error(
        last_exc,
        api_tag=api_tag,
        of_label=of_label,
        auth_key_name=auth_key_name,
    ) from last_exc


def _generate_with_openai(
    request: GenerationRequest,
    model: str = DEFAULT_OPENAI_MODEL,
) -> ExerciseBatch:
    """Gera exercícios usando OpenAI Structured Outputs."""
    return _generate_with_openai_compatible(
        request,
        client=get_client(),
        model=model,
        api_tag="openai",
        of_label="da OpenAI",
        auth_key_name="LLM_API_KEY",
        fallbacks=OPENAI_MODEL_FALLBACKS,
    )


def _generate_with_grok(
    request: GenerationRequest,
    model: str = DEFAULT_GROK_MODEL,
) -> ExerciseBatch:
    """Gera exercícios usando Grok (xAI) via OpenAI-compatible Structured Outputs."""
    return _generate_with_openai_compatible(
        request,
        client=get_grok_client(),
        model=model,
        api_tag="grok",
        of_label="do Grok",
        auth_key_name="GROK_API_KEY",
        fallbacks=GROK_MODEL_FALLBACKS,
    )


def generate_exercises(
    request: GenerationRequest,
    model: str | None = None,
) -> ExerciseBatch:
    """Gera exercícios matemáticos estruturados via OpenAI, Gemini ou Grok."""
    provider = _resolve_provider()

    if provider == "gemini":
        from generator_gemini import DEFAULT_GEMINI_MODEL, generate_exercises as generate_gemini

        return generate_gemini(request, model=model or DEFAULT_GEMINI_MODEL)

    if provider == "grok":
        return _generate_with_grok(request, model=model or DEFAULT_GROK_MODEL)

    return _generate_with_openai(request, model=model or DEFAULT_OPENAI_MODEL)
