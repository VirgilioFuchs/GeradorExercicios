"""Offline unit tests for demo loopback/header/lock guards (DEMO-02)."""

from __future__ import annotations

import sys
import threading
from pathlib import Path

import pytest

DEMO_DIR = Path(__file__).resolve().parents[1]
if str(DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(DEMO_DIR))

from guards import (  # noqa: E402
    ALLOWED_HOST,
    ALLOWED_ORIGIN,
    assert_loopback,
    check_post_headers,
    lock_busy_response,
)


def test_refuse_non_loopback() -> None:
    assert_loopback("::1")  # must not raise
    with pytest.raises(SystemExit):
        assert_loopback("0.0.0.0")
    with pytest.raises(SystemExit):
        assert_loopback("::")


def test_headers() -> None:
    assert check_post_headers(ALLOWED_HOST, None, "application/json") is None
    assert check_post_headers(ALLOWED_HOST, None, "application/json; charset=utf-8") is None
    assert check_post_headers(ALLOWED_HOST, ALLOWED_ORIGIN, "application/json") is None

    assert check_post_headers("evil.example:8642", None, "application/json") == 403
    assert check_post_headers(ALLOWED_HOST, "http://evil.example", "application/json") == 403
    assert check_post_headers(ALLOWED_HOST, None, "text/plain") == 415
    assert check_post_headers(ALLOWED_HOST, None, "") == 415


def test_lock_409() -> None:
    lock = threading.Lock()
    assert lock.acquire(blocking=False) is True
    try:
        status, payload = lock_busy_response()
        assert status == 409
        assert "HTTP 409" in payload["error"]["message"]
        assert payload["ok"] is False
    finally:
        lock.release()
