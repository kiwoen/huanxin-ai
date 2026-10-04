"""Obsidian-friendly rendering for GitHub analysis results."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from huanxin.tools.github_readonly import github_list_repository, github_read_file


def render_github_analysis_note(
    *,
    owner: str,
    repo: str,
    summary: str,
    files: list[str] | None = None,
    output_dir: str | Path = "docs/obsidian/github",
) -> Path:
    """Write a deterministic Markdown note and return its path."""
    safe_owner = "".join(c for c in owner if c.isalnum() or c in "-_ ").strip().replace(" ", "-")
    safe_repo = "".join(c for c in repo if c.isalnum() or c in "-_ ").strip().replace(" ", "-")
    if not safe_owner or not safe_repo:
        raise ValueError("owner and repo must contain a valid name")

    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{safe_owner}--{safe_repo}.md"
    source = f"https://github.com/{owner}/{repo}"
    checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    file_lines = "\n".join(f"- `{item}`" for item in (files or [])) or "- 未记录"
    content = (
        f"---\nowner: {owner}\nrepo: {repo}\nsource: {source}\nchecked_at: {checked_at}\ntags: [github, huanxin-ai]\n---\n\n"
        f"# {owner}/{repo}\n\n"
        f"## 摘要\n\n{summary.strip()}\n\n"
        f"## 关键文件\n\n{file_lines}\n\n"
        f"## 来源\n\n[{source}]({source})\n"
    )
    target.write_text(content, encoding="utf-8")
    return target


def analyze_public_repository(
    *,
    owner: str,
    repo: str,
    ref: str = "",
    output_dir: str | Path = "docs/obsidian/github",
) -> dict[str, Any]:
    """Collect a small, deterministic snapshot of a public GitHub repository.

    This is deliberately a read-only ingestion skill.  GPT or another model
    can consume the returned files later to produce a deeper analysis.
    """
    listing = github_list_repository(owner, repo, ref=ref)
    if not listing.success:
        return {"success": False, "error": listing.error, "owner": owner, "repo": repo}

    entries = listing.data or []
    names = [item.get("name", "") for item in entries if isinstance(item, dict)]
    candidate_names = [
        name
        for name in ("README.md", "README中国.md", "pyproject.toml", "requirements.txt", "package.json")
        if name in names
    ]
    files: dict[str, Any] = {}
    for path in candidate_names:
        result = github_read_file(owner, repo, path, ref=ref)
        if result.success:
            files[path] = result.data

    summary = (
        f"已读取公开仓库 `{owner}/{repo}` 的根目录。\n\n"
        f"根目录条目数：{len(entries)}。\n"
        f"已读取关键文件：{', '.join(candidate_names) if candidate_names else '无'}。"
    )
    note = render_github_analysis_note(
        owner=owner,
        repo=repo,
        summary=summary,
        files=[item.get("path", "") for item in entries if isinstance(item, dict)],
        output_dir=output_dir,
    )
    return {
        "success": True,
        "owner": owner,
        "repo": repo,
        "entries": entries,
        "files": files,
        "note": str(note),
    }
