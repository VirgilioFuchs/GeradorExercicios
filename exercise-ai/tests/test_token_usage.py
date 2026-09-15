"""Offline tests for token usage observability (Phase 9) — mocks only, no live LLM."""

from __future__ import annotations

import json
from datetime import datetime
from types import SimpleNamespace

import pytest

import token_usage.collector as collector_mod
from token_usage import (
    INDISPONIVEL,
    begin_run,
    estimate_usd_from_rates,
    extract_gemini_usage,
    extract_grok_usage,
    extract_openai_usage,
    flush_token_usage,
    get_collector,
)


@pytest.fixture
def usage_dir(tmp_path, monkeypatch):
    """Injectable TOKEN_USAGE_DIR under tmp (mirror POSTMORTEM_PATH pattern)."""
    base = tmp_path / "token-usage"
    base.mkdir()
    monkeypatch.setattr(collector_mod, "TOKEN_USAGE_DIR", base)
    collector = get_collector()
    collector.begin_run("testrun01")
    yield base
    collector.events.clear()


def _fake_openai_completion(*, prompt=100, completion=20, total=120, ticks=None):
    usage = SimpleNamespace(
        prompt_tokens=prompt,
        completion_tokens=completion,
        total_tokens=total,
    )
    if ticks is not None:
        usage.cost_in_usd_ticks = ticks
    return SimpleNamespace(usage=usage)


def test_extract_openai_usage_and_missing_indisponivel():
    fields = extract_openai_usage(
        _fake_openai_completion(),
        model="gpt-4o-mini",
    )
    assert fields.prompt_tokens == 100
    assert fields.completion_tokens == 20
    assert fields.total_tokens == 120
    assert isinstance(fields.usd, float)
    assert fields.usd_source == "rate_table"

    empty = extract_openai_usage(SimpleNamespace(usage=None), model="gpt-4o-mini")
    assert empty.prompt_tokens == INDISPONIVEL
    assert empty.completion_tokens == INDISPONIVEL
    assert empty.total_tokens == INDISPONIVEL
    assert empty.usd == INDISPONIVEL
    assert empty.usd_source == "indisponivel"
    assert empty.prompt_tokens != 0


def test_extract_gemini_usage_metadata():
    response = SimpleNamespace(
        usage_metadata=SimpleNamespace(
            prompt_token_count=50,
            candidates_token_count=10,
            total_token_count=60,
        )
    )
    fields = extract_gemini_usage(response, model="gemini-3.1-flash-lite")
    assert fields.prompt_tokens == 50
    assert fields.completion_tokens == 10
    assert fields.total_tokens == 60
    assert isinstance(fields.usd, float)
    assert fields.usd_source == "rate_table"


def test_extract_grok_prefers_cost_in_usd_ticks():
    ticks = 25_000_000  # 0.0025 USD
    fields = extract_grok_usage(
        _fake_openai_completion(ticks=ticks),
        model="grok-4.6",
    )
    assert fields.usd == pytest.approx(ticks / 1e10)
    assert fields.usd_source == "api"

    no_ticks = extract_grok_usage(
        _fake_openai_completion(),
        model="grok-4.6",
    )
    assert isinstance(no_ticks.usd, float)
    assert no_ticks.usd_source == "rate_table"


def test_rate_table_unknown_model_indisponivel():
    usd, src = estimate_usd_from_rates("totally-unknown-model", 100, 20)
    assert usd == INDISPONIVEL
    assert src == "indisponivel"


def test_record_flush_ndjson_append_and_idempotent(usage_dir, capsys):
    c = get_collector()
    fields = extract_openai_usage(
        _fake_openai_completion(),
        model="gpt-4o-mini",
    )
    c.record(
        provider="openai",
        model="gpt-4o-mini",
        status="success",
        prompt_tokens=fields.prompt_tokens,
        completion_tokens=fields.completion_tokens,
        total_tokens=fields.total_tokens,
        duration_ms=42,
        usd=fields.usd,
        usd_source=fields.usd_source,
    )
    err = capsys.readouterr().err
    assert "[USAGE]" in err
    assert "provider=openai" in err
    assert "in=100" in err
    assert "sk-" not in err

    flush_token_usage()
    day = datetime.now().astimezone().date().isoformat()
    path = usage_dir / day / "openai.ndjson"
    assert path.is_file()
    lines1 = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines1) == 1
    row = json.loads(lines1[0])
    assert row["provider"] == "openai"
    assert row["prompt_tokens"] == 100
    assert row["run_id"] == "testrun01"
    assert "sk-" not in lines1[0]

    # Idempotent: second flush without new events adds nothing
    flush_token_usage()
    lines_after = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines_after) == 1

    # Second run appends
    begin_run("testrun02")
    c.record(
        provider="openai",
        model="gpt-4o-mini",
        status="success",
        prompt_tokens=5,
        completion_tokens=1,
        total_tokens=6,
        duration_ms=1,
        usd=INDISPONIVEL,
        usd_source="indisponivel",
    )
    flush_token_usage()
    lines2 = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines2) == 2


def test_missing_usage_never_fabricates_zero(usage_dir, capsys):
    c = get_collector()
    c.record(
        provider="openai",
        model="unknown-x",
        status="error",
        duration_ms=3,
        error_kind="Timeout",
    )
    err = capsys.readouterr().err
    assert INDISPONIVEL in err
    assert "in=0" not in err
    flush_token_usage()
    day = datetime.now().astimezone().date().isoformat()
    row = json.loads(
        (usage_dir / day / "openai.ndjson").read_text(encoding="utf-8").strip()
    )
    assert row["prompt_tokens"] == INDISPONIVEL
    assert row["usd"] == INDISPONIVEL
    assert row["prompt_tokens"] != 0


def test_usage_stderr_redacts_secrets_spirit(usage_dir, monkeypatch, capsys):
    monkeypatch.setenv("LLM_API_KEY", "sk-secret-should-never-appear")
    monkeypatch.setenv("GEMINI_API_KEY", "AIza-secret-never")
    c = get_collector()
    c.record(
        provider="openai",
        model="gpt-4o-mini",
        status="success",
        prompt_tokens=10,
        completion_tokens=2,
        total_tokens=12,
        duration_ms=5,
        usd=0.001,
        usd_source="rate_table",
    )
    err = capsys.readouterr().err
    assert "sk-secret" not in err
    assert "AIza-secret" not in err
    assert "Resolva a equação" not in err  # no prompt bodies
    flush_token_usage()
    day = datetime.now().astimezone().date().isoformat()
    blob = (usage_dir / day / "openai.ndjson").read_text(encoding="utf-8")
    assert "sk-secret" not in blob
    assert "AIza-secret" not in blob


def test_rely_attempt_status_retag(usage_dir, monkeypatch, capsys):
    """RELY validation failure retags last LLM success → attempt (D-12)."""
    from models import DificuldadeEnum, Exercise, ExerciseBatch, GenerationRequest
    import reliability

    request = GenerationRequest(
        materia="Matemática",
        topico="soma",
        dificuldade=DificuldadeEnum.FACIL,
        quantidade=1,
    )
    good = ExerciseBatch(
        exercicios=[
            Exercise(
                enunciado="2+2",
                resposta="4",
                explicacao="dois mais dois",
            )
        ]
    )
    bad = ExerciseBatch(
        exercicios=[
            Exercise(
                enunciado="bad",
                resposta="x",
                explicacao="y",
            )
        ]
    )
    calls = {"n": 0}

    def fake_gen(_req):
        calls["n"] += 1
        batch = bad if calls["n"] == 1 else good
        get_collector().record(
            provider="openai",
            model="gpt-4o-mini",
            status="success",
            prompt_tokens=10,
            completion_tokens=2,
            total_tokens=12,
            duration_ms=1,
            usd=0.01,
            usd_source="rate_table",
        )
        return batch

    def fake_validate(batch, _req):
        if batch.exercicios[0].enunciado == "bad":
            raise ValueError("enunciado inválido")
        return batch

    monkeypatch.setattr(reliability, "generate_exercises", fake_gen)
    monkeypatch.setattr(reliability, "validate_exercise_batch", fake_validate)
    result = reliability.generate_validated_batch(request, max_retries=1)
    assert result.exercicios[0].enunciado == "2+2"

    statuses = [e.status for e in get_collector().events]
    assert "attempt" in statuses
    assert statuses[-1] == "success"
    flush_token_usage()
    err = capsys.readouterr().err
    assert "resumo" in err
    assert "eventos_sem_preco" in err


def test_end_of_run_summary_numeric_vs_indisponivel(usage_dir, capsys):
    c = get_collector()
    c.record(
        provider="openai",
        model="gpt-4o-mini",
        status="success",
        prompt_tokens=100,
        completion_tokens=20,
        total_tokens=120,
        duration_ms=10,
        usd=0.05,
        usd_source="rate_table",
    )
    c.record(
        provider="gemini",
        model="unknown",
        status="success",
        prompt_tokens=50,
        completion_tokens=10,
        total_tokens=60,
        duration_ms=8,
        usd=INDISPONIVEL,
        usd_source="indisponivel",
    )
    flush_token_usage()
    err = capsys.readouterr().err
    assert "[USAGE] resumo provider=openai" in err
    assert "[USAGE] resumo provider=gemini" in err
    assert "eventos_sem_preco=1" in err
    assert "0.05" in err


def test_main_run_flush_in_finally(usage_dir, monkeypatch, tmp_path, capsys):
    """main.run flushes once in finally even on SystemExit."""
    from models import DificuldadeEnum, Exercise, ExerciseBatch, GenerationRequest
    import main as main_mod

    batch = ExerciseBatch(
        exercicios=[
            Exercise(enunciado="1+1", resposta="2", explicacao="soma")
        ]
    )
    request = GenerationRequest(
        materia="Matemática",
        topico="soma",
        dificuldade=DificuldadeEnum.FACIL,
        quantidade=1,
    )

    def fake_validated(req, max_retries):
        get_collector().record(
            provider="openai",
            model="gpt-4o-mini",
            status="success",
            prompt_tokens=1,
            completion_tokens=1,
            total_tokens=2,
            duration_ms=1,
            usd=INDISPONIVEL,
            usd_source="indisponivel",
        )
        return batch

    monkeypatch.setattr(main_mod, "generate_validated_batch", fake_validated)
    monkeypatch.setattr(main_mod, "resolve_max_retries", lambda x: 0)
    out = tmp_path / "out.json"
    main_mod.run(request, out_path=out, max_retries=0)
    day = datetime.now().astimezone().date().isoformat()
    path = usage_dir / day / "openai.ndjson"
    assert path.is_file()
    assert len(path.read_text(encoding="utf-8").strip().splitlines()) == 1
    # Exercise JSON must not contain usage fields
    dumped = json.loads(out.read_text(encoding="utf-8"))
    assert "prompt_tokens" not in dumped
    assert "usd" not in dumped
    assert "exercicios" in dumped
