"""Fail-closed content assertions for demo UI markers (Plan 12-02 Task 1)."""

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
    ):
        assert needle in text, f"missing marker in app.js: {needle!r}"


def test_ui_markers_present_across_html_and_js() -> None:
    combined = INDEX.read_text(encoding="utf-8") + "\n" + APP_JS.read_text(encoding="utf-8")
    for needle in (
        "Contrato",
        "Ambiente",
        "Exercícios",
        "Gerando",
        "GenerationRequest",
        "/gerar",
    ):
        assert needle in combined, f"missing UI marker: {needle!r}"
