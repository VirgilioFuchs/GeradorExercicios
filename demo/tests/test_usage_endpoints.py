"""Offline tests for GET /usage/sessions and /usage/session (tmp fixtures only)."""

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


@pytest.fixture()
def demo_server():
    """Start DemoServer on [::1] ephemeral port."""
    httpd = serve.create_server("::1", 0)
    _host, port, *_ = httpd.server_address
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.05)
    yield httpd, port
    httpd.shutdown()
    httpd.server_close()


def _get_json(port: int, path: str) -> tuple[int, dict]:
    conn = HTTPConnection("::1", port, timeout=5)
    try:
        conn.request("GET", path, headers={"Host": "[::1]:8642"})
        resp = conn.getresponse()
        data = json.loads(resp.read().decode("utf-8"))
        return resp.status, data
    finally:
        conn.close()


def _write_fixture(tmp_path: Path) -> None:
    day = tmp_path / "2026-01-01"
    day.mkdir(parents=True)
    lines = [
        {
            "ts": "2026-01-01T10:00:00",
            "provider": "openai",
            "model": "gpt-4o-mini",
            "status": "attempt",
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
            "duration_ms": 100,
            "usd": "indisponível",
            "usd_source": "indisponivel",
            "run_id": "run-aaa",
        },
        {
            "ts": "2026-01-01T10:00:01",
            "provider": "openai",
            "model": "gpt-4o-mini",
            "status": "success",
            "prompt_tokens": 20,
            "completion_tokens": 10,
            "total_tokens": 30,
            "duration_ms": 200,
            "usd": 0.001,
            "usd_source": "rate_table",
            "run_id": "run-aaa",
        },
        {
            "ts": "2026-01-01T11:00:00",
            "provider": "openai",
            "model": "gpt-4o-mini",
            "status": "error",
            "prompt_tokens": "indisponível",
            "completion_tokens": "indisponível",
            "total_tokens": "indisponível",
            "duration_ms": 50,
            "usd": "indisponível",
            "usd_source": "indisponivel",
            "run_id": "run-bbb",
            "error_kind": "timeout",
        },
    ]
    (day / "openai.ndjson").write_text(
        "\n".join(json.dumps(obj, ensure_ascii=False) for obj in lines) + "\n",
        encoding="utf-8",
    )


def test_usage_sessions_lists_run_ids(demo_server, tmp_path: Path) -> None:
    _write_fixture(tmp_path)
    _httpd, port = demo_server
    with patch.object(serve, "_USAGE_DIR", tmp_path):
        status, data = _get_json(port, "/usage/sessions")
    assert status == 200
    assert data["ok"] is True
    run_ids = {s["run_id"] for s in data["sessions"]}
    assert run_ids == {"run-aaa", "run-bbb"}
    assert data["sessions"][0]["last_ts"] >= data["sessions"][1]["last_ts"]
    aaa = next(s for s in data["sessions"] if s["run_id"] == "run-aaa")
    assert aaa["event_count"] == 2
    assert aaa["providers"] == ["openai"]


def test_usage_session_aggregates(demo_server, tmp_path: Path) -> None:
    _write_fixture(tmp_path)
    _httpd, port = demo_server
    with patch.object(serve, "_USAGE_DIR", tmp_path):
        status, data = _get_json(port, "/usage/session?run_id=run-aaa")
    assert status == 200
    assert data["ok"] is True
    assert data["run_id"] == "run-aaa"
    assert len(data["events"]) == 2
    summary = data["summary"]
    assert summary["prompt_tokens"] == 30
    assert summary["completion_tokens"] == 15
    assert summary["total_tokens"] == 45
    assert summary["duration_ms"] == 300
    assert summary["usd"] == pytest.approx(0.001)
    assert summary["tentativas"] == 1
    assert summary["sucessos"] == 1
    assert summary["erros"] == 0
    assert summary["event_count"] == 2


def test_usage_session_error_run(demo_server, tmp_path: Path) -> None:
    _write_fixture(tmp_path)
    _httpd, port = demo_server
    with patch.object(serve, "_USAGE_DIR", tmp_path):
        status, data = _get_json(port, "/usage/session?run_id=run-bbb")
    assert status == 200
    summary = data["summary"]
    assert summary["tentativas"] == 0
    assert summary["sucessos"] == 0
    assert summary["erros"] == 1
    assert summary["prompt_tokens"] == "indisponível"
    assert summary["usd"] == "indisponível"
    assert summary["duration_ms"] == 50


def test_usage_sessions_empty_dir(demo_server, tmp_path: Path) -> None:
    empty = tmp_path / "empty-usage"
    empty.mkdir()
    _httpd, port = demo_server
    with patch.object(serve, "_USAGE_DIR", empty):
        status, data = _get_json(port, "/usage/sessions")
    assert status == 200
    assert data == {"ok": True, "sessions": []}


def test_usage_session_unknown_run_empty(demo_server, tmp_path: Path) -> None:
    _write_fixture(tmp_path)
    _httpd, port = demo_server
    with patch.object(serve, "_USAGE_DIR", tmp_path):
        status, data = _get_json(port, "/usage/session?run_id=missing")
    assert status == 200
    assert data["ok"] is True
    assert data["events"] == []
    assert data["summary"]["event_count"] == 0
    assert data["summary"]["usd"] == "indisponível"


def test_usage_session_rejects_bad_run_id(demo_server, tmp_path: Path) -> None:
    _httpd, port = demo_server
    with patch.object(serve, "_USAGE_DIR", tmp_path):
        status, data = _get_json(port, "/usage/session?run_id=../evil")
    assert status == 400
    assert data["ok"] is False


def test_usage_ignores_corrupt_json_lines(demo_server, tmp_path: Path) -> None:
    day = tmp_path / "2026-01-02"
    day.mkdir()
    (day / "openai.ndjson").write_text(
        "not-json\n"
        + json.dumps(
            {
                "ts": "2026-01-02T12:00:00",
                "provider": "openai",
                "model": "m",
                "status": "success",
                "prompt_tokens": 1,
                "completion_tokens": 1,
                "total_tokens": 2,
                "duration_ms": 10,
                "usd": 0.0,
                "usd_source": "api",
                "run_id": "run-ok",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    _httpd, port = demo_server
    with patch.object(serve, "_USAGE_DIR", tmp_path):
        status, data = _get_json(port, "/usage/sessions")
    assert status == 200
    assert len(data["sessions"]) == 1
    assert data["sessions"][0]["run_id"] == "run-ok"
