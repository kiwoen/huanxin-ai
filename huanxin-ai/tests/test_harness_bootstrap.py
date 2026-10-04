from __future__ import annotations

from pathlib import Path

from huanxin.harness import register_default_harness_tools
from huanxin.skills import render_github_analysis_note
from huanxin.tools.registry import ToolRegistry


def test_bootstrap_registers_read_only_github_tools() -> None:
    registry = register_default_harness_tools(ToolRegistry())

    assert registry.get_tool("github_read_file") is not None
    assert registry.get_tool("github_list_repository") is not None


def test_render_github_analysis_note(tmp_path: Path) -> None:
    note = render_github_analysis_note(
        owner="kiwoen",
        repo="huanxin-ai",
        summary="这是一个测试摘要。",
        files=["README.md", "pyproject.toml"],
        output_dir=tmp_path,
    )

    text = note.read_text(encoding="utf-8")
    assert note.name == "kiwoen--huanxin-ai.md"
    assert "这是一个测试摘要" in text
    assert "README.md" in text
