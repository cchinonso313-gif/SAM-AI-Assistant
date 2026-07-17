"""Clipboard read/write tools (optional ``pyperclip`` dependency)."""

import logging

from backend.agent.tool_registry import ToolRegistry, ToolResult

logger = logging.getLogger(__name__)


def copy_to_clipboard(text: str) -> ToolResult:
    """Place text on the system clipboard."""
    try:
        import pyperclip  # noqa: WPS433 - optional dependency

        pyperclip.copy(text)
    except Exception as e:  # noqa: BLE001
        return ToolResult(success=False, output="", error=f"clipboard unavailable: {e}")
    return ToolResult(success=True, output=f"Copied {len(text)} chars")


def paste_from_clipboard() -> ToolResult:
    """Read the current clipboard contents."""
    try:
        import pyperclip  # noqa: WPS433 - optional dependency

        return ToolResult(success=True, output=pyperclip.paste())
    except Exception as e:  # noqa: BLE001
        return ToolResult(success=False, output="", error=f"clipboard unavailable: {e}")


def register(registry: ToolRegistry) -> None:
    registry.register(
        "copy_to_clipboard", "Copy text to the clipboard", copy_to_clipboard, {"text": "text"},
    )
    registry.register(
        "paste_from_clipboard", "Read text from the clipboard", paste_from_clipboard, {},
    )
