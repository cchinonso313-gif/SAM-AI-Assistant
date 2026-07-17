import logging

from backend.agent.tool_registry import ToolRegistry, ToolResult

logger = logging.getLogger(__name__)

MAX_BODY = 20_000


def web_fetch(url: str, timeout: int = 20) -> ToolResult:
    """Fetch the text body of a URL (HTTP GET)."""
    try:
        import requests
    except ImportError:
        return ToolResult(success=False, output="", error="requests not installed")

    if not url.lower().startswith(("http://", "https://")):
        return ToolResult(success=False, output="", error="url must start with http:// or https://")

    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "NOVA-Assistant"})
    except Exception as e:  # noqa: BLE001 - network errors surfaced to agent
        return ToolResult(success=False, output="", error=str(e))

    body = resp.text[:MAX_BODY]
    return ToolResult(
        success=resp.ok,
        output=f"HTTP {resp.status_code}\n{body}",
        error=None if resp.ok else f"HTTP {resp.status_code}",
    )


def register(registry: ToolRegistry) -> None:
    registry.register(
        "web_fetch",
        "Fetch the contents of a web page via HTTP GET",
        web_fetch,
        {"url": "http(s) URL", "timeout": "seconds (optional)"},
    )
