"""Local throwaway demo server: POST /gerar → generate_batch on [::1]:8642."""

from __future__ import annotations

import functools
import json
import os
import socket
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from pydantic import ValidationError

DEMO_DIR = Path(__file__).resolve().parent
REPO_ROOT = DEMO_DIR.parent
EXERCISE_AI = REPO_ROOT / "exercise-ai"

_ea = str(EXERCISE_AI)
if _ea not in sys.path:
    sys.path.insert(0, _ea)

_demo = str(DEMO_DIR)
if _demo not in sys.path:
    sys.path.insert(0, _demo)

from error_map import error_payload  # noqa: E402
from guards import assert_loopback, check_post_headers, lock_busy_response  # noqa: E402
from models import GenerationRequest  # noqa: E402
from service import (  # noqa: E402
    ConfigError,
    GenerationFailedError,
    InvalidRequestError,
    generate_batch,
)

HOST = "::1"
PORT = 8642

_VALID_PROVIDER = frozenset({"openai", "gemini", "grok"})
_VALID_REASONING = frozenset({"none", "low", "medium", "high"})
_SCOPED_ENV_KEYS = ("LLM_PROVIDER", "LLM_REASONING_EFFORT", "LLM_MODEL")

_GEN_LOCK = threading.Lock()


class DemoServer(ThreadingHTTPServer):
    """IPv6 loopback ThreadingHTTPServer (AF_INET6 required for ::1)."""

    address_family = socket.AF_INET6


def _apply_env(
    provider: str | None,
    reasoning: str | None,
    model: str | None = None,
) -> dict[str, Any]:
    """Snapshot env, apply provider/reasoning/model; caller must restore."""
    snapshot: dict[str, Any] = {
        key: os.environ.get(key) for key in _SCOPED_ENV_KEYS
    }
    snapshot["_present"] = {key: key in os.environ for key in _SCOPED_ENV_KEYS}

    prov = (provider or "").strip().lower()
    if prov in _VALID_PROVIDER:
        os.environ["LLM_PROVIDER"] = prov
    else:
        os.environ.pop("LLM_PROVIDER", None)

    reason = (reasoning or "").strip().lower()
    if reason in _VALID_REASONING:
        os.environ["LLM_REASONING_EFFORT"] = reason
    else:
        os.environ["LLM_REASONING_EFFORT"] = "medium"

    model_id = (model or "").strip()
    if model_id:
        os.environ["LLM_MODEL"] = model_id
    else:
        os.environ.pop("LLM_MODEL", None)

    return snapshot


def _restore_scoped_env(snapshot: dict[str, Any]) -> None:
    present: dict[str, bool] = snapshot.get("_present", {})
    for key in _SCOPED_ENV_KEYS:
        if present.get(key):
            value = snapshot.get(key)
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        else:
            os.environ.pop(key, None)


def _models_payload() -> dict[str, Any]:
    """Generation fallback lists for the demo model picker."""
    from model_catalog import (
        DEFAULT_GEMINI_MODEL,
        DEFAULT_GROK_MODEL,
        DEFAULT_OPENAI_MODEL,
        GEMINI_MODEL_FALLBACKS,
        GROK_MODEL_FALLBACKS,
        OPENAI_MODEL_FALLBACKS,
    )

    return {
        "openai": list(OPENAI_MODEL_FALLBACKS),
        "gemini": list(GEMINI_MODEL_FALLBACKS),
        "grok": list(GROK_MODEL_FALLBACKS),
        "defaults": {
            "openai": DEFAULT_OPENAI_MODEL,
            "gemini": DEFAULT_GEMINI_MODEL,
            "grok": DEFAULT_GROK_MODEL,
        },
    }


class DemoHandler(SimpleHTTPRequestHandler):
    """Static files from demo/ plus POST /gerar → generate_batch under Lock."""

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/models":
            self._send_json(200, _models_payload())
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        if self.path.split("?", 1)[0] != "/gerar":
            self.send_error(404, "Not Found")
            return

        header_status = check_post_headers(
            self.headers.get("Host"),
            self.headers.get("Origin"),
            self.headers.get("Content-Type"),
        )
        if header_status is not None:
            self._send_json(
                header_status,
                {
                    "ok": False,
                    "error": {
                        "class": "HeaderError",
                        "message": f"Rejected headers (HTTP {header_status})",
                    },
                },
            )
            return

        if not _GEN_LOCK.acquire(blocking=False):
            status, payload = lock_busy_response()
            self._send_json(status, payload)
            return

        try:
            length = int(self.headers.get("Content-Length") or "0")
            raw = self.rfile.read(length) if length > 0 else b"{}"
            try:
                body = json.loads(raw.decode("utf-8") or "{}")
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                self._send_json(
                    400,
                    {
                        "ok": False,
                        "error": {
                            "class": "InvalidRequestError",
                            "message": f"JSON inválido: {exc}",
                            "kind": "invalid_json",
                        },
                    },
                )
                return

            if not isinstance(body, dict):
                self._send_json(
                    400,
                    {
                        "ok": False,
                        "error": {
                            "class": "InvalidRequestError",
                            "message": "Body JSON deve ser um objeto",
                            "kind": "invalid_json",
                        },
                    },
                )
                return

            provider = body.get("provider")
            reasoning = body.get("reasoning")
            model = body.get("model")
            snapshot = _apply_env(
                provider if isinstance(provider, str) else None,
                reasoning if isinstance(reasoning, str) else None,
                model if isinstance(model, str) else None,
            )
            try:
                try:
                    request = GenerationRequest(
                        materia=body.get("materia", "Matemática"),
                        topico=body.get("topico", ""),
                        dificuldade=body.get("dificuldade", "medio"),
                        quantidade=body.get("quantidade", 1),
                    )
                except ValidationError as exc:
                    self._send_json(
                        400,
                        {
                            "ok": False,
                            "error": {
                                "class": "InvalidRequestError",
                                "message": str(exc),
                                "kind": "validation",
                            },
                        },
                    )
                    return

                try:
                    batch = generate_batch(request)
                except (ConfigError, InvalidRequestError, GenerationFailedError) as exc:
                    self._send_json(200, {"ok": False, "error": error_payload(exc)})
                    return

                self._send_json(200, {"ok": True, "batch": batch.model_dump()})
            finally:
                _restore_scoped_env(snapshot)
        finally:
            _GEN_LOCK.release()

    def _send_json(self, status: int, obj: dict[str, Any]) -> None:
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        # Keep terminal quiet during tests; __main__ still gets default via subclass? 
        # Use stderr lightly without secrets.
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))


def make_handler() -> type[DemoHandler]:
    """Bind handler to demo/ directory without os.chdir."""
    return functools.partial(DemoHandler, directory=str(DEMO_DIR))  # type: ignore[return-value]


def create_server(
    host: str = HOST,
    port: int = PORT,
) -> DemoServer:
    handler = make_handler()
    return DemoServer((host, port), handler)


if __name__ == "__main__":
    from dotenv import load_dotenv

    # Multi-path .env: repo root then exercise-ai/
    load_dotenv(REPO_ROOT / ".env")
    load_dotenv(EXERCISE_AI / ".env")

    assert_loopback(HOST)
    with create_server(HOST, PORT) as httpd:
        print(f"Demo em http://[{HOST}]:{PORT}/  (Ctrl+C para parar)")
        httpd.serve_forever()
