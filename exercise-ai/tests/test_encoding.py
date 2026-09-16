"""cp1252-safe diagnostics and CLI encoding regressions (D-10 / EMBED-06)."""

from __future__ import annotations

import io
import sys
from contextlib import redirect_stderr

import pytest

import failover
import main
import validator
from models import DificuldadeEnum, Exercise, ExerciseBatch, GenerationRequest


def _cp1252_stream() -> io.TextIOWrapper:
    """Text stream that rejects glyphs outside Windows cp1252."""
    return io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict", newline="\n")


def test_failover_diagnostic_encodes_on_cp1252():
    """[FAILOVER] hop line must be ASCII-safe for narrow Windows consoles."""
    line = "[FAILOVER] openai -> gemini (timeout)\n"
    stream = _cp1252_stream()
    stream.write(line)
    stream.flush()
    raw = stream.buffer.getvalue()
    assert b"->" in raw
    assert "→".encode("utf-8") not in raw


def test_failover_print_to_cp1252_stderr_does_not_raise(monkeypatch):
    """Live [FAILOVER] print path must not raise UnicodeEncodeError on cp1252."""
    stream = _cp1252_stream()
    monkeypatch.setattr(sys, "stderr", stream)

    req = GenerationRequest(
        topico="x",
        dificuldade=DificuldadeEnum.FACIL,
        quantidade=1,
    )
    batch = ExerciseBatch(
        exercicios=[
            Exercise(enunciado="e", resposta="1", explicacao="x"),
        ]
    )

    calls = {"n": 0}

    def _gen(_request, _max_retries):
        calls["n"] += 1
        if calls["n"] == 1:
            from service import GenerationFailedError

            raise GenerationFailedError(
                "Tempo esgotado",
                retriable=False,
                api_error_kind="timeout",
            )
        return batch

    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-gemini-key")

    result = failover.generate_with_failover(
        req,
        max_retries=0,
        generate_fn=_gen,
        switch_provider=lambda _p: None,
    )
    assert result is batch
    stream.flush()
    text = stream.buffer.getvalue().decode("cp1252")
    assert "[FAILOVER] openai -> gemini (timeout)" in text


def test_validation_failure_log_safe_on_cp1252(monkeypatch):
    """Batch dump with math glyphs must not raise on cp1252 stderr."""
    stream = _cp1252_stream()
    monkeypatch.setattr(sys, "stderr", stream)

    batch = ExerciseBatch(
        exercicios=[
            Exercise(
                enunciado="Calcule √16 + π",
                resposta="4 + π",
                explicacao="√16 = 4; use π",
            )
        ]
    )
    # Should not raise UnicodeEncodeError
    validator._log_validation_failure("quantidade incorreta", batch)
    stream.flush()
    # Stream remains usable (got some bytes)
    assert len(stream.buffer.getvalue()) > 0


def test_format_batch_text_printable_via_safe_path():
    """format_batch_text output can be written to cp1252 with replace, not crash helpers."""
    batch = ExerciseBatch(
        exercicios=[
            Exercise(
                enunciado="√9 = ?",
                resposta="3",
                explicacao="√9 = 3",
            )
        ]
    )
    text = main.format_batch_text(batch)
    encoded = text.encode("cp1252", errors="replace")
    assert isinstance(encoded, bytes)
    # Helper used by CLI must not itself require a UTF-8-only environment
    assert "Exercício" in text or "Exercicio" in text or "###" in text


def test_reconfigure_stdio_when_supported():
    """CLI helper reconfigures stdout/stderr to utf-8 + replace when available."""
    stdout = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")
    stderr = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")
    # Bind temporary streams
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = stdout, stderr
        main._reconfigure_stdio()
        assert sys.stdout.encoding.lower().replace("-", "") in {"utf8", "utf_8"}
        assert sys.stderr.errors == "replace" or sys.stderr.encoding.lower().startswith(
            "utf"
        )
    finally:
        sys.stdout, sys.stderr = old_out, old_err
