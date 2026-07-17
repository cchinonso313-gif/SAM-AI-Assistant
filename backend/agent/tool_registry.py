import asyncio
import inspect
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Outcome of a single tool invocation."""

    success: bool
    output: str
    error: Optional[str] = None

    def to_observation(self) -> str:
        if self.success:
            return self.output
        return f"ERROR: {self.error or self.output}"


@dataclass
class Tool:
    """A capability the agent can invoke.

    ``func`` may be sync or async and receives keyword arguments matching
    ``parameters`` (a ``name -> description`` mapping used only to prompt the
    LLM). It should return a str, a ToolResult, or raise on failure.
    """

    name: str
    description: str
    func: Callable[..., Any]
    parameters: Dict[str, str] = field(default_factory=dict)

    async def __call__(self, **kwargs: Any) -> ToolResult:
        try:
            result = self.func(**kwargs)
            if inspect.isawaitable(result):
                result = await result
            if isinstance(result, ToolResult):
                return result
            return ToolResult(success=True, output=str(result))
        except Exception as e:  # noqa: BLE001 - surfaced back to the agent loop
            logger.error(f"❌ Tool '{self.name}' failed: {e}")
            return ToolResult(success=False, output="", error=str(e))


class ToolRegistry:
    """Holds the set of tools available to an agent."""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(
        self,
        name: str,
        description: str,
        func: Callable[..., Any],
        parameters: Optional[Dict[str, str]] = None,
    ) -> Tool:
        tool = Tool(name=name, description=description, func=func, parameters=parameters or {})
        self._tools[name] = tool
        logger.info(f"🛠️ Registered tool: {name}")
        return tool

    def add(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def names(self) -> List[str]:
        return sorted(self._tools)

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def describe(self) -> str:
        """Return a compact, LLM-friendly description of all tools."""
        lines = []
        for name in self.names():
            tool = self._tools[name]
            params = ", ".join(f"{k} ({v})" for k, v in tool.parameters.items()) or "none"
            lines.append(f"- {name}: {tool.description} | args: {params}")
        return "\n".join(lines)

    async def execute(self, name: str, args: Dict[str, Any]) -> ToolResult:
        tool = self.get(name)
        if tool is None:
            return ToolResult(success=False, output="", error=f"Unknown tool: {name}")
        return await tool(**(args or {}))
