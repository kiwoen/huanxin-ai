from __future__ import annotations

from pathlib import Path

from huanxin.tools.file_readonly import read_file


def test_read_file_stays_inside_allowed_root(tmp_path: Path) -> None:
    source = tmp_path / "note.md"
    source.write_text("hello", encoding="utf-8")

    result = read_file(str(source), str(tmp_path))

    assert result.success is True
    assert result.data["content"] == "hello"


def test_read_file_rejects_path_escape(tmp_path: Path) -> None:
    result = read_file(str(tmp_path.parent / "outside.md"), str(tmp_path))

    assert result.success is False
    assert "outside" in result.error
