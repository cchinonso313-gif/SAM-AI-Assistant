import logging
from pathlib import Path

from backend.agent.tool_registry import ToolRegistry, ToolResult

logger = logging.getLogger(__name__)

MAX_READ_BYTES = 200_000


def read_file(path: str) -> ToolResult:
    """Read a UTF-8 text file."""
    p = Path(path).expanduser()
    if not p.is_file():
        return ToolResult(success=False, output="", error=f"Not a file: {path}")
    data = p.read_text(encoding="utf-8", errors="replace")[:MAX_READ_BYTES]
    return ToolResult(success=True, output=data)


def write_file(path: str, content: str = "") -> ToolResult:
    """Create or overwrite a text file, making parent dirs as needed."""
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return ToolResult(success=True, output=f"Wrote {len(content)} chars to {p}")


def append_file(path: str, content: str = "") -> ToolResult:
    """Append text to a file, creating it if needed."""
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(content)
    return ToolResult(success=True, output=f"Appended {len(content)} chars to {p}")


def list_dir(path: str = ".") -> ToolResult:
    """List the entries of a directory."""
    p = Path(path).expanduser()
    if not p.is_dir():
        return ToolResult(success=False, output="", error=f"Not a directory: {path}")
    entries = sorted(e.name + ("/" if e.is_dir() else "") for e in p.iterdir())
    return ToolResult(success=True, output="\n".join(entries) or "(empty)")


def make_dir(path: str) -> ToolResult:
    """Create a directory (and parents)."""
    p = Path(path).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    return ToolResult(success=True, output=f"Created directory {p}")


def register(registry: ToolRegistry) -> None:
    registry.register("read_file", "Read a text file", read_file, {"path": "file path"})
    registry.register(
        "write_file",
        "Create or overwrite a text file",
        write_file,
        {"path": "file path", "content": "text to write"},
    )
    registry.register(
        "append_file",
        "Append text to a file",
        append_file,
        {"path": "file path", "content": "text to append"},
    )
    registry.register("list_dir", "List a directory", list_dir, {"path": "directory path"})
    registry.register("make_dir", "Create a directory", make_dir, {"path": "directory path"})
