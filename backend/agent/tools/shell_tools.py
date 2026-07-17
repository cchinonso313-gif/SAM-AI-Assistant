import logging
import subprocess

from backend.agent.safety import is_command_safe
from backend.agent.tool_registry import ToolRegistry, ToolResult

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60


def run_shell(command: str, timeout: int = DEFAULT_TIMEOUT) -> ToolResult:
    """Run a shell command after safety screening.

    Destructive or blocked commands are refused. Output is captured and
    truncated. This is intended for legitimate local automation only.
    """
    safe, reason = is_command_safe(command)
    if not safe:
        logger.warning(f"🚫 Refused command ({reason}): {command}")
        return ToolResult(success=False, output="", error=f"Refused for safety ({reason})")

    try:
        completed = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return ToolResult(success=False, output="", error=f"Timed out after {timeout}s")

    output = (completed.stdout or "") + (completed.stderr or "")
    output = output[-10_000:]
    if completed.returncode != 0:
        return ToolResult(
            success=False,
            output=output,
            error=f"exit code {completed.returncode}",
        )
    return ToolResult(success=True, output=output or "(no output)")


def register(registry: ToolRegistry) -> None:
    registry.register(
        "run_shell",
        "Run a safe local shell command and capture its output",
        run_shell,
        {"command": "shell command", "timeout": "seconds (optional)"},
    )
