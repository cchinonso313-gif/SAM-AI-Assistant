"""Built-in tool modules for the NOVA agent.

Each submodule exposes a ``register(registry)`` function so capabilities are
self-contained and easy to add or improve. ``build_default_registry`` wires
them all together.
"""

from backend.agent.tool_registry import ToolRegistry
from backend.agent.tools import (
    file_tools,
    project_tools,
    shell_tools,
    system_tools,
    web_tools,
)

_MODULES = [file_tools, project_tools, shell_tools, system_tools, web_tools]


def build_default_registry() -> ToolRegistry:
    """Return a registry populated with all built-in tools."""
    registry = ToolRegistry()
    for module in _MODULES:
        module.register(registry)
    return registry


__all__ = ["build_default_registry"]
