import logging
import platform
import shutil

from backend.agent.tool_registry import ToolRegistry, ToolResult

logger = logging.getLogger(__name__)


def system_info() -> ToolResult:
    """Report basic host information and resource usage."""
    lines = [
        f"os: {platform.system()} {platform.release()}",
        f"machine: {platform.machine()}",
        f"python: {platform.python_version()}",
    ]

    try:
        import psutil

        lines.append(f"cpu_percent: {psutil.cpu_percent(interval=0.1)}")
        vm = psutil.virtual_memory()
        lines.append(f"memory_percent: {vm.percent}")
    except ImportError:
        lines.append("psutil not installed - limited info")

    total, used, free = shutil.disk_usage("/")
    lines.append(f"disk_free_gb: {free // (1024 ** 3)}")

    return ToolResult(success=True, output="\n".join(lines))


def register(registry: ToolRegistry) -> None:
    registry.register(
        "system_info",
        "Report host OS and resource usage",
        system_info,
        {},
    )
