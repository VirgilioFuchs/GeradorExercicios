"""Pure demo guards: loopback bind, POST header allowlist, busy lock payload."""

from __future__ import annotations

import ipaddress
from typing import Any

ALLOWED_HOST = "[::1]:8642"
ALLOWED_ORIGIN = "http://[::1]:8642"

_BUSY_MESSAGE = (
    "Geração já em andamento — contrato sequencial (HTTP 409). "
    "Aguarde a resposta atual antes de enviar outro POST /gerar."
)


def assert_loopback(host: str) -> None:
    """Refuse non-loopback bind hosts (T-12-01). Raises SystemExit on failure."""
    try:
        addr = ipaddress.ip_address(host)
    except ValueError as exc:
        raise SystemExit(f"Recusa bind inválido: {host!r}") from exc
    if not addr.is_loopback:
        raise SystemExit(f"Recusa bind não-loopback: {host!r}")


def check_post_headers(
    host: str | None,
    origin: str | None,
    content_type: str | None,
) -> int | None:
    """Return 403/415 on allowlist mismatch, else None when headers are OK.

    Host must equal ``[::1]:8642``. Origin, when present, must equal
    ``http://[::1]:8642``. Content-Type type/subtype must be application/json
    (parameters ignored). Missing Origin is allowed.
    """
    if (host or "") != ALLOWED_HOST:
        return 403
    if origin is not None and origin != ALLOWED_ORIGIN:
        return 403
    ctype = (content_type or "").split(";", 1)[0].strip().lower()
    if ctype != "application/json":
        return 415
    return None


def lock_busy_response() -> tuple[int, dict[str, Any]]:
    """Build HTTP 409 payload with literal ``HTTP 409`` in the message (D-11)."""
    return 409, {
        "ok": False,
        "error": {
            "class": "ConflictError",
            "message": _BUSY_MESSAGE,
        },
    }
