"""Fail-closed content assertions for demo anti-accretion docs (Plan 12-02 Task 2)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEMO_README = REPO_ROOT / "demo" / "README.md"
ROOT_README = REPO_ROOT / "README.md"


def test_demo_readme_anti_accretion_pack() -> None:
    text = DEMO_README.read_text(encoding="utf-8")
    for needle in (
        "delete",
        "[::1]:8642",
        "netstat",
        "CI",
    ):
        assert needle in text, f"missing marker in demo/README.md: {needle!r}"
    assert "http://[::1]:8642/" in text
    assert "python demo/serve.py" in text


def test_root_readme_embed_pointer() -> None:
    text = ROOT_README.read_text(encoding="utf-8")
    assert "demo/" in text, "root README missing demo/ pointer"
    assert "[::1]:8642" in text, "root README missing loopback URL"
    lowered = text.lower()
    assert "delete" in lowered, "root README missing delete/expiry note"
