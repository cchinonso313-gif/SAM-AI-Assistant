"""Autonomous agent core for NOVA.

The agent runs a plan -> act -> observe -> reflect loop, choosing from a
registry of modular tools. Tools live in ``backend.agent.tools`` and each is a
small, self-contained module so capabilities can be added or improved
independently.
"""

from backend.agent.tool_registry import Tool, ToolRegistry, ToolResult
from backend.agent.agent import Agent, AgentStep

__all__ = ["Tool", "ToolRegistry", "ToolResult", "Agent", "AgentStep"]
