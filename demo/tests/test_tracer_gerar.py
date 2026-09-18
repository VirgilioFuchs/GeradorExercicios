"""End-to-end tracer tests for POST /gerar with mocked generate_batch."""

from __future__ import annotations

import json
import sys
import threading
import time
from http.client import HTTPConnection
from pathlib import Path
from unittest.mock import patch

import pytest

DEMO_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = DEMO_DIR.parent
EXERCISE_AI = REPO_ROOT / "exercise-ai"
for path in (DEMO_DIR, EXERCISE_AI):
    s = str(path)
    if s not in sys.path:
        sys.path.insert(0, s)

import serve  # noqa: E402
from models import Exercise, ExerciseBatch  # noqa: E402
from service import ConfigError  # noqa: E402


@pytest.fixture()
def demo_server():
    """Start DemoServer on [::1] ephemeral port; Host header still [::1]:8642."""
    httpd = serve.create_server("::1", 0)
    host, port, *_ = httpd.server_address
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    # Brief wait for listen
    time.sleep(0.05)
    yield httpd, port
    httpd.shutdown()
    httpd.server_close()


def _post_gerar(port: int, body: dict, extra_headers: dict | None = None) -> tuple[int, dict]:
    headers = {
        "Host": "[::1]:8642",
        "Content-Type": "application/json",
        "Origin": "http://[::1]:8642",
    }
    if extra_headers:
        headers.update(extra_headers)
    raw = json.dumps(body).encode("utf-8")
    headers["Content-Length"] = str(len(raw))
    conn = HTTPConnection("::1", port, timeout=5)
    try:
        conn.request("POST", "/gerar", body=raw, headers=headers)
        resp = conn.getresponse()
        data = json.loads(resp.read().decode("utf-8"))
        return resp.status, data
    finally:
        conn.close()


def test_gerar_success_mocked(demo_server) -> None:
    _httpd, port = demo_server
    batch = ExerciseBatch(
        exercicios=[
            Exercise(
                enunciado="2x=4",
                resposta="x=2",
                explicacao="dividir por 2",
            )
        ]
    )
    with patch.object(serve, "generate_batch", return_value=batch) as mock_gen:
        status, data = _post_gerar(
            port,
            {
                "materia": "Matemática",
                "topico": "equação do 1º grau",
                "dificuldade": "medio",
                "quantidade": 1,
                "provider": "",
                "reasoning": "medium",
            },
        )
        assert status == 200
        assert data["ok"] is True
        assert data["batch"]["exercicios"][0]["resposta"] == "x=2"
        mock_gen.assert_called_once()
        req = mock_gen.call_args[0][0]
        assert req.materia == "Matemática"
        assert req.topico == "equação do 1º grau"
        assert req.quantidade == 1


def test_gerar_config_error_mocked(demo_server) -> None:
    _httpd, port = demo_server
    with patch.object(
        serve,
        "generate_batch",
        side_effect=ConfigError("chave ausente", kind="missing_key"),
    ):
        status, data = _post_gerar(
            port,
            {
                "materia": "Matemática",
                "topico": "soma",
                "dificuldade": "facil",
                "quantidade": 1,
            },
        )
        assert status == 200
        assert data["ok"] is False
        assert data["error"]["class"] == "ConfigError"
        assert data["error"]["kind"] == "missing_key"
        assert "chave ausente" in data["error"]["message"]


def test_gerar_busy_lock_409(demo_server) -> None:
    _httpd, port = demo_server
    assert serve._GEN_LOCK.acquire(blocking=False) is True
    try:
        status, data = _post_gerar(
            port,
            {
                "materia": "Matemática",
                "topico": "soma",
                "dificuldade": "facil",
                "quantidade": 1,
            },
        )
        assert status == 409
        assert data["ok"] is False
        assert "HTTP 409" in data["error"]["message"]
    finally:
        serve._GEN_LOCK.release()


def test_gerar_bad_content_type_415(demo_server) -> None:
    _httpd, port = demo_server
    status, data = _post_gerar(
        port,
        {"materia": "Matemática", "topico": "soma", "dificuldade": "facil", "quantidade": 1},
        extra_headers={"Content-Type": "text/plain"},
    )
    assert status == 415
    assert data["ok"] is False


def test_static_get_does_not_take_lock(demo_server) -> None:
    _httpd, port = demo_server
    assert serve._GEN_LOCK.acquire(blocking=False) is True
    try:
        conn = HTTPConnection("::1", port, timeout=5)
        try:
            conn.request("GET", "/", headers={"Host": "[::1]:8642"})
            resp = conn.getresponse()
            body = resp.read()
            assert resp.status == 200
            assert b"/gerar" in body or b"GenerationRequest" in body
        finally:
            conn.close()
    finally:
        serve._GEN_LOCK.release()
