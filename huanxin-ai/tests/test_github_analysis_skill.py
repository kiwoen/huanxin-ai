from __future__ import annotations

from pathlib import Path

from huanxin.skills.github_analysis import analyze_public_repository
from huanxin.tools.base import ToolResult
from huanxin.tools.github_readonly import github_list_repository, github_read_file


def test_analyze_public_repository_creates_obsidian_snapshot(monkeypatch, tmp_path: Path) -> None:
    def fake_list(owner, repo, path="", ref=""):
        return ToolResult(
            success=True,
            data=[
                {"name": "README.md", "path": "README.md", "type": "file"},
                {"name": "pyproject.toml", "path": "pyproject.toml", "type": "file"},
                {"name": "huanxin", "path": "huanxin", "type": "dir"},
            ],
        )

    def fake_read(owner, repo, path, ref=""):
        return ToolResult(success=True, data={"path": path, "content": f"content:{path}"})

    monkeypatch.setattr("huanxin.skills.github_analysis.github_list_repository", fake_list)
    monkeypatch.setattr("huanxin.skills.github_analysis.github_read_file", fake_read)

    result = analyze_public_repository(
        owner="kiwoen",
        repo="huanxin-ai",
        output_dir=tmp_path,
    )

    assert result["success"] is True
    assert set(result["files"]) == {"README.md", "pyproject.toml"}
    note = Path(result["note"])
    assert note.exists()
    assert "根目录条目数：3" in note.read_text(encoding="utf-8")
