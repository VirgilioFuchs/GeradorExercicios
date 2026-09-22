"""Fail-closed content assertions for demo UI markers (Plan 12-02 / 14-02)."""

from __future__ import annotations

from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parents[1]
INDEX = DEMO_DIR / "index.html"
APP_JS = DEMO_DIR / "app.js"


def test_index_html_has_form_and_tab_markers() -> None:
    text = INDEX.read_text(encoding="utf-8")
    for needle in (
        "Contrato",
        "Ambiente",
        "Exercícios",
        "JSON",
        "GenerationRequest",
        "model-select",
    ):
        assert needle in text, f"missing marker in index.html: {needle!r}"


def test_index_html_band_counts_and_soft_warn() -> None:
    """DEMO-01 / D-09..D-11: three band inputs + soft-warn; no dificuldade select."""
    text = INDEX.read_text(encoding="utf-8")
    for needle in (
        'name="facil"',
        'name="medio"',
        'name="dificil"',
        'name="quantidade"',
        'id="band-soft-warn"',
        "soft-warn",
        'role="status"',
    ):
        assert needle in text, f"missing band/soft-warn marker: {needle!r}"
    assert 'name="dificuldade"' not in text
    assert "<select name=\"dificuldade\">" not in text
    assert 'value="0"' in text  # facil/dificil defaults
    assert 'value="2"' in text  # medio + quantidade defaults


def test_app_js_has_client_behavior_markers() -> None:
    text = APP_JS.read_text(encoding="utf-8")
    for needle in (
        "/gerar",
        "/models",
        "Gerando",
        "HTTP 409",
        "lastSuccessBatch",
        "sessionStorage",  # D-16 banner dismiss
        "fillModelOptions",
        "plano",
        "soft-warn",
        "band-soft-warn",
        "buildGerarPayload",
        "updateSoftWarn",
        "Aviso: a soma das dificuldades é 0",
        "Aviso: a soma das dificuldades é maior que 40",
        "é diferente da soma das bandas",
    ):
        assert needle in text, f"missing marker in app.js: {needle!r}"


def test_app_js_payload_rules_uniform_vs_mixed() -> None:
    """D-12..D-14: mixed→plano; uniform→dificuldade + band quantidade."""
    text = APP_JS.read_text(encoding="utf-8")
    assert "payload.plano" in text
    assert "payload.dificuldade" in text
    assert "active.length >= 2" in text
    assert "active.length === 1" in text
    assert "active[0].count" in text
    # Soft-warn must not gate submit
    assert "preventDefault" in text  # only form submit handler
    assert "soft-warn" in text.lower() or "updateSoftWarn" in text


def test_ui_markers_present_across_html_and_js() -> None:
    combined = INDEX.read_text(encoding="utf-8") + "\n" + APP_JS.read_text(encoding="utf-8")
    for needle in (
        "Contrato",
        "Ambiente",
        "Exercícios",
        "Gerando",
        "GenerationRequest",
        "/gerar",
        "facil",
        "plano",
        "band-soft-warn",
    ):
        assert needle in combined, f"missing UI marker: {needle!r}"
