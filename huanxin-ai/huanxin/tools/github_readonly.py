"""Read-only GitHub tools for public repositories."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any

from huanxin.tools.base import ToolResult, tool


def _get_json(url: str, timeout: int = 15) -> Any:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "huanxin-ai"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


@tool(name="github_read_file", category="github")
def github_read_file(owner: str, repo: str, path: str, ref: str = "") -> ToolResult:
    """Read a file from a public GitHub repository without modifying it."""
    if not owner or not repo or not path:
        return ToolResult(success=False, error="owner, repo and path are required")

    query = f"?ref={urllib.parse.quote(ref)}" if ref else ""
    url = f"https://api.github.com/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repo)}/contents/{urllib.parse.quote(path, safe='/')}" + query
    try:
        payload = _get_json(url)
    except Exception as exc:
        return ToolResult(success=False, error=f"GitHub read failed: {exc}")

    if not isinstance(payload, dict) or payload.get("type") != "file":
        return ToolResult(success=False, error="GitHub path is not a file")

    return ToolResult(
        success=True,
        data={
            "owner": owner,
            "repo": repo,
            "path": path,
            "sha": payload.get("sha", ""),
            "content": payload.get("content", ""),
            "encoding": payload.get("encoding", ""),
            "html_url": payload.get("html_url", ""),
        },
    )


@tool(name="github_list_repository", category="github")
def github_list_repository(owner: str, repo: str, path: str = "", ref: str = "") -> ToolResult:
    """List files and directories in a public GitHub repository path."""
    query = f"?ref={urllib.parse.quote(ref)}" if ref else ""
    url = f"https://api.github.com/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repo)}/contents/{urllib.parse.quote(path, safe='/')}" + query
    try:
        payload = _get_json(url)
    except Exception as exc:
        return ToolResult(success=False, error=f"GitHub listing failed: {exc}")

    if not isinstance(payload, list):
        return ToolResult(success=False, error="GitHub path is not a directory")

    return ToolResult(
        success=True,
        data=[
            {"name": item.get("name", ""), "type": item.get("type", ""), "path": item.get("path", ""), "sha": item.get("sha", "")}
            for item in payload
            if isinstance(item, dict)
        ],
    )


def register_github_tools(registry: Any | None = None) -> Any:
    """Register the two read-only GitHub tools and return the registry."""
    if registry is None:
        from huanxin.tools.registry import get_registry

        registry = get_registry()
    for function in (github_read_file, github_list_repository):
        if function.tool_def is not None and registry.get_tool(function.tool_def.name) is None:
            registry.register_tool(function.tool_def)
    return registry
