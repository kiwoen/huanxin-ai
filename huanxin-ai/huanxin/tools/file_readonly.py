"""Sandboxed read-only file tool."""

from __future__ import annotations

import os
from pathlib import Path

from huanxin.tools.base import tool


def _allowed_path(path: str, allowed_root: str | None) -> Path:
    candidate = Path(path).expanduser().resolve()
    root = Path(allowed_root or os.getenv("HUANXIN_READ_ROOT", ".")).expanduser().resolve()
    if candidate != root and root not in candidate.parents:
        raise PermissionError(f"file is outside the read root: {root}")
    return candidate


@tool(name="read_file", category="file")
def read_file(path: str, allowed_root: str = "") -> dict[str, str]:
    """Read a UTF-8 text file under the configured read-only root."""
    target = _allowed_path(path, allowed_root or None)
    if not target.is_file():
        raise FileNotFoundError("path is not a file")
    content = target.read_text(encoding="utf-8")
    return {"path": str(target), "content": content}


def register_file_tools(registry=None):
    """Register the read-only file tool into a supplied or global registry."""
    if registry is None:
        from huanxin.tools.registry import get_registry

        registry = get_registry()
    if read_file.tool_def is not None and registry.get_tool(read_file.tool_def.name) is None:
        registry.register_tool(read_file.tool_def)
    return registry
