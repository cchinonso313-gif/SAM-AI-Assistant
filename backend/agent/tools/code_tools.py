"""Sandboxed Python code execution tool.

Runs model-authored Python in a fresh subprocess with a timeout, captured
output, and the same safety screening used for shell commands. This is for
running the user's own scripts/snippets, not for bypassing any protections.
"""

import logging
import subprocess
import sys
import tempfile
from pathlib import Path

from backend.agent.safety import is_command_safe
from backend.agent.tool_registry import ToolRegistry, ToolResult

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30
MAX_OUTPUT = 10_000


def run_python(code: str, timeout: int = DEFAULT_TIMEOUT) -> ToolResult:
    """Execute a Python snippet in an isolated subprocess and return output."""
    safe, reason = is_command_safe(code)
    if not safe:
        return ToolResult(success=False, output="", error=f"Refused: {reason}")

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".py", delete=False, encoding="utf-8"
        ) as fh:
            fh.write(code)
            tmp_path = fh.name

        proc = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return ToolResult(success=False, output="", error=f"Timed out after {timeout}s")
    except Exception as e:  # noqa: BLE001
        return ToolResult(success=False, output="", error=str(e))
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)

    output = (proc.stdout or "")[:MAX_OUTPUT]
    if proc.returncode != 0:
        err = (proc.stderr or "").strip()[:MAX_OUTPUT] or f"exit code {proc.returncode}"
        return ToolResult(success=False, output=output, error=err)
    return ToolResult(success=True, output=output or "(no output)")


def register(registry: ToolRegistry) -> None:
    registry.register(
        "run_python",
        "Execute a Python snippet in a sandboxed subprocess and return its output",
        run_python,
        {"code": "python source", "timeout": "seconds (optional)"},
    )
