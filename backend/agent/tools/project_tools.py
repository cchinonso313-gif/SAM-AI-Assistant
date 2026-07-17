import json
import logging
from pathlib import Path
from typing import Dict, Union

from backend.agent.tool_registry import ToolRegistry, ToolResult

logger = logging.getLogger(__name__)


def scaffold_project(root: str, files: Union[Dict[str, str], str]) -> ToolResult:
    """Create a project tree.

    ``files`` maps relative paths to file contents (or a JSON string of the
    same). Directories are created automatically. Useful for generating
    websites, apps, or scripts in one step.
    """
    if isinstance(files, str):
        try:
            files = json.loads(files)
        except json.JSONDecodeError as e:
            return ToolResult(success=False, output="", error=f"Invalid files JSON: {e}")

    if not isinstance(files, dict) or not files:
        return ToolResult(success=False, output="", error="files must be a non-empty mapping")

    root_path = Path(root).expanduser()
    written = []
    for rel_path, content in files.items():
        target = root_path / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content if isinstance(content, str) else str(content), encoding="utf-8")
        written.append(str(target))

    return ToolResult(
        success=True,
        output=f"Created {len(written)} files under {root_path}:\n" + "\n".join(written),
    )


def register(registry: ToolRegistry) -> None:
    registry.register(
        "scaffold_project",
        "Create a whole project/website/app from a map of path -> file contents",
        scaffold_project,
        {"root": "project root dir", "files": "mapping of relative path -> contents"},
    )
