"""Obsidian-friendly rendering for GitHub analysis results."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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
