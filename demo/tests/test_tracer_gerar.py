"""End-to-end tracer tests for POST /gerar with mocked generate_batch."""

from __future__ import annotations

import json
import os
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
from models import DificuldadeEnum, Exercise, ExerciseBatch  # noqa: E402
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


def _uniform_batch(band: str = "medio") -> ExerciseBatch:
    return ExerciseBatch(
        exercicios=[
            Exercise(
                enunciado="2x=4",
                resposta="x=2",
                explicacao="dividir por 2",
                dificuldade=band,
            )
        ],
        dificuldades=[band],
    )


def test_gerar_success_mocked(demo_server) -> None:
    _httpd, port = demo_server
    batch = _uniform_batch("medio")
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
        assert req.plano is None


def test_gerar_mixed_plano_passthrough(demo_server) -> None:
    """DEMO-01 / D-15: mixed POST with plano reaches GenerationRequest."""
    _httpd, port = demo_server
    batch = ExerciseBatch(
        exercicios=[
            Exercise(
                enunciado="fácil",
                resposta="1",
                explicacao="ok",
                dificuldade="facil",
            ),
            Exercise(
                enunciado="médio",
                resposta="2",
                explicacao="ok",
                dificuldade="medio",
            ),
        ],
        dificuldades=["facil", "medio"],
    )
    with patch.object(serve, "generate_batch", return_value=batch) as mock_gen:
        status, data = _post_gerar(
            port,
            {
                "materia": "Matemática",
                "topico": "misto",
                "quantidade": 2,
                "plano": {"facil": 1, "medio": 1, "dificil": 0},
                "provider": "",
                "reasoning": "medium",
            },
        )
        assert status == 200
        assert data["ok"] is True
        mock_gen.assert_called_once()
        req = mock_gen.call_args[0][0]
        assert req.plano is not None
        assert req.plano.facil == 1
        assert req.plano.medio == 1
        assert req.plano.dificil == 0
        bands = [s.dificuldade for s in req.itens_ordenados]
        assert bands == [DificuldadeEnum.FACIL, DificuldadeEnum.MEDIO]


def test_gerar_plano_qty_drift_returns_400(demo_server) -> None:
    """Illegal qty↔plano drift rejected by Pydantic → 400."""
    _httpd, port = demo_server
    with patch.object(serve, "generate_batch") as mock_gen:
        status, data = _post_gerar(
            port,
            {
                "materia": "Matemática",
                "topico": "drift",
                "quantidade": 3,
                "plano": {"facil": 1, "medio": 1, "dificil": 0},
            },
        )
        assert status == 400
        assert data["ok"] is False
        assert data["error"]["kind"] == "validation"
        mock_gen.assert_not_called()


def test_models_endpoint(demo_server) -> None:
    _httpd, port = demo_server
    conn = HTTPConnection("::1", port, timeout=5)
    try:
        conn.request("GET", "/models", headers={"Host": "[::1]:8642"})
        resp = conn.getresponse()
        data = json.loads(resp.read().decode("utf-8"))
        assert resp.status == 200
        assert "openai" in data and "gemini" in data and "grok" in data
        assert "defaults" in data
        assert data["defaults"]["openai"]
        assert isinstance(data["openai"], list) and len(data["openai"]) >= 1
    finally:
        conn.close()


def test_gerar_sets_llm_model_env(demo_server) -> None:
    _httpd, port = demo_server
    seen: dict[str, str | None] = {}

    def capture(request):
        seen["LLM_MODEL"] = os.environ.get("LLM_MODEL")
        return ExerciseBatch(
            exercicios=[
                Exercise(
                    enunciado="1+1",
                    resposta="2",
                    explicacao="soma",
                    dificuldade="facil",
                )
            ],
            dificuldades=["facil"],
        )

    with patch.object(serve, "generate_batch", side_effect=capture):
        status, data = _post_gerar(
            port,
            {
                "materia": "Matemática",
                "topico": "soma",
                "dificuldade": "facil",
                "quantidade": 1,
                "provider": "openai",
                "model": "gpt-4o-mini",
                "reasoning": "medium",
            },
        )
        assert status == 200
        assert data["ok"] is True
        assert seen["LLM_MODEL"] == "gpt-4o-mini"
    assert os.environ.get("LLM_MODEL") in (None, "")


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
