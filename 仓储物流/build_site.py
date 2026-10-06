from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
SITE = ROOT / "site"

PAGES = [
    ("project-charter", "项目章程", "目标、范围、干系人和待确认假设"),
    ("requirements", "需求清单", "角色、功能优先级、数据与质量要求"),
    ("workflows", "仓储业务流程", "建档、收货、上架、拣货、移库与盘点"),
    ("architecture", "系统架构与底座", "数据真值、扫码设备、开源方案与集成"),
    ("ai-assistant", "AI 助手边界", "适合交给 AI 的工作及人工确认规则"),
    ("implementation", "实施计划与任务表", "分阶段交付、责任人、产物和关口"),
    ("cost-and-commercial", "成本与商业化", "成本构成、路线对比与收费假设"),
    ("risks-and-compliance", "风险与合规", "库存准确性、数据安全、运行和授权风险"),
    ("acceptance", "试点验收指标", "先取基线，再按试点数据决定是否扩展"),
    ("references", "网络资料与依据", "项目书结构、开源系统和条码标准来源"),
]

PAGE_SLUGS = {slug for slug, _, _ in PAGES}


def split_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def inline_markup(text: str, is_home: bool) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    def replace_link(match: re.Match[str]) -> str:
        label, target = match.group(1), html.unescape(match.group(2))
        target_slug = Path(target.split("#", 1)[0]).stem
        if target.endswith(".md") and target_slug in PAGE_SLUGS | {"index"}:
            if target_slug == "index":
                href = "../index.html" if not is_home else "index.html"
            else:
                href = (
                    f"pages/{target_slug}.html"
                    if is_home
                    else f"{target_slug}.html"
                )
            if "#" in target:
                href += "#" + target.split("#", 1)[1]
            return f'<a href="{html.escape(href, quote=True)}">{label}</a>'
        safe_target = html.escape(target, quote=True)
        external = target.startswith(("https://", "http://", "mailto:"))
        attrs = ' target="_blank" rel="noopener noreferrer"' if external else ""
        return f'<a href="{safe_target}"{attrs}>{label}</a>'

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, text)


def render_markdown(source: str, is_home: bool) -> str:
    lines = source.splitlines()
    if lines and lines[0].strip() == "---":
        try:
            end = lines.index("---", 1)
            lines = lines[end + 1 :]
        except ValueError:
            pass

    out: list[str] = []
    paragraph: list[str] = []
    list_kind: str | None = None
    table_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            joined = " ".join(part.strip() for part in paragraph)
            out.append("<p>" + inline_markup(joined, is_home) + "</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            out.append(f"</{list_kind}>")
            list_kind = None

    def flush_table() -> None:
        if not table_lines:
            return
        rows = [split_cells(line) for line in table_lines]
        header = rows[0]
        body = rows[2:] if len(rows) > 1 and all(
            re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in rows[1]
        ) else rows[1:]
        out.append('<div class="table-wrap"><table><thead><tr>')
        out.extend(
            "<th>" + inline_markup(cell, is_home) + "</th>" for cell in header
        )
        out.append("</tr></thead><tbody>")
        for row in body:
            out.append("<tr>")
            for index in range(len(header)):
                value = row[index] if index < len(row) else ""
                out.append("<td>" + inline_markup(value, is_home) + "</td>")
            out.append("</tr>")
        out.append("</tbody></table></div>")
        table_lines.clear()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph()
            close_list()
            table_lines.append(stripped)
            continue
        flush_table()
        if not stripped:
            flush_paragraph()
            close_list()
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1))
            title = heading.group(2).strip()
            anchor = re.sub(r"[^a-z0-9\u4e00-\u9fff-]+", "-", title.lower()).strip("-")
            out.append(
                f'<h{level} id="{html.escape(anchor, quote=True)}">'
                f'{inline_markup(title, is_home)}</h{level}>'
            )
            continue
        if stripped == "---":
            flush_paragraph()
            close_list()
            out.append("<hr>")
            continue
        if stripped.startswith(">"):
            flush_paragraph()
            close_list()
            quote = stripped[1:].strip()
            out.append(
                '<blockquote><p>'
                + inline_markup(quote, is_home)
                + "</p></blockquote>"
            )
            continue
        unordered = re.match(r"^[-*]\s+(.+)$", stripped)
        ordered = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if unordered or ordered:
            flush_paragraph()
            next_kind = "ul" if unordered else "ol"
            if list_kind != next_kind:
                close_list()
                list_kind = next_kind
                out.append(f"<{list_kind}>")
            item = unordered.group(1) if unordered else ordered.group(1)
            out.append("<li>" + inline_markup(item, is_home) + "</li>")
            continue
        close_list()
        paragraph.append(stripped)

    flush_paragraph()
    close_list()
    flush_table()
    return "\n".join(out)


def navigation(current_slug: str, is_home: bool) -> str:
    home_href = "index.html" if is_home else "../index.html"
    prefix = "pages/" if is_home else ""
    entries = [
        f'<a class="nav-item{" active" if is_home else ""}" href="{home_href}">'
        '<span class="nav-number">00</span><span>总览首页</span></a>'
    ]
    for index, (slug, title, _) in enumerate(PAGES, start=1):
        active = " active" if current_slug == slug else ""
        entries.append(
            f'<a class="nav-item{active}" href="{prefix}{slug}.html">'
            f'<span class="nav-number">{index:02d}</span><span>{html.escape(title)}</span></a>'
        )
    return "\n".join(entries)


def page_template(
    title: str,
    body: str,
    current_slug: str,
    is_home: bool,
    page_description: str = "",
) -> str:
    asset_prefix = "" if is_home else "../"
    active_title = "项目总览" if is_home else title
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{html.escape(page_description or title, quote=True)}">
  <title>{html.escape(title)} · 仓储物流项目书</title>
  <link rel="stylesheet" href="{asset_prefix}assets/style.css">
</head>
<body>
  <header class="topbar">
    <a class="brand" href="{asset_prefix}index.html">
      <span class="brand-mark">仓</span>
      <span><strong>仓储物流</strong><small>半自动化仓储系统 · 项目书</small></span>
    </a>
    <div class="topbar-meta"><span class="status-dot"></span>草案 V0.1</div>
  </header>
  <div class="layout">
    <aside class="sidebar" aria-label="项目书章节">
      <div class="sidebar-caption">项目导航</div>
      {navigation(current_slug, is_home)}
      <div class="sidebar-note">
        <strong>文档状态</strong>
        <span>需求待实地确认</span>
        <small>更新于 2026-10-06</small>
      </div>
    </aside>
    <main class="main">
      <div class="breadcrumb"><a href="{asset_prefix}index.html">项目书</a><span>/</span><span>{html.escape(active_title)}</span></div>
      <article class="article">
        {body}
      </article>
      <footer class="footer">
        <span>仓储物流 · 立项与试点方案</span>
        <span>Markdown 源文件位于 content/，可在 Obsidian 中编辑</span>
      </footer>
    </main>
  </div>
</body>
</html>
"""


def main() -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "pages").mkdir(parents=True, exist_ok=True)
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    css_source = ROOT / "assets" / "style.css"
    (SITE / "assets" / "style.css").write_text(
        css_source.read_text(encoding="utf-8"), encoding="utf-8"
    )

    home_source = (CONTENT / "index.md").read_text(encoding="utf-8")
    home_body = render_markdown(home_source, True)
    cards = []
    for index, (slug, title, description) in enumerate(PAGES, start=1):
        cards.append(
            f'<a class="chapter-card" href="pages/{slug}.html">'
            f'<span class="card-number">{index:02d}</span>'
            f'<span class="card-copy"><strong>{html.escape(title)}</strong>'
            f'<small>{html.escape(description)}</small></span>'
            '<span class="card-arrow">↗</span></a>'
        )
    home_body += (
        '<section class="chapter-section"><div class="section-kicker">PROJECT BOOK</div>'
        '<h2>项目书导航</h2><p>点击章节进入对应子网页；也可用左侧导航在页面间切换。</p>'
        '<div class="chapter-grid">'
        + "\n".join(cards)
        + "</div></section>"
    )
    (SITE / "index.html").write_text(
        page_template(
            "项目总览",
            home_body,
            "index",
            True,
            "仓储半自动化系统项目书总览与子章节导航",
        ),
        encoding="utf-8",
    )

    for slug, title, description in PAGES:
        source = CONTENT / f"{slug}.md"
        if not source.exists():
            raise FileNotFoundError(f"项目书章节不存在：{source}")
        body = render_markdown(source.read_text(encoding="utf-8"), False)
        (SITE / "pages" / f"{slug}.html").write_text(
            page_template(title, body, slug, False, description),
            encoding="utf-8",
        )
    print(f"网站已生成：{SITE / 'index.html'}")
    print(f"子页面数量：{len(PAGES)}")


if __name__ == "__main__":
    main()
