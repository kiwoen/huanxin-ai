"""Safe, explicit registration of tools used by the local harness."""

from __future__ import annotations

from huanxin.tools.registry import ToolRegistry, get_registry


def register_default_harness_tools(registry: ToolRegistry | None = None) -> ToolRegistry:
    """Register built-in and read-only GitHub tools.

    Registration is explicit so importing Huanxin never silently enables new
    network or filesystem capabilities.
    """
    target = registry or get_registry()

    # Importing builtin registers its decorated tools for the process registry.
    if target is get_registry():
        import huanxin.tools.builtin  # noqa: F401

    from huanxin.tools.github_readonly import register_github_tools
    from huanxin.tools.file_readonly import register_file_tools

    register_github_tools(target)
    register_file_tools(target)
    return target
