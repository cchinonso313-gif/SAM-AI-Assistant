import html
import logging
import re
from urllib.parse import unquote

from backend.agent.tool_registry import ToolRegistry, ToolResult

logger = logging.getLogger(__name__)

MAX_BODY = 20_000

# Matches DuckDuckGo HTML result anchors: href + visible title text.
_RESULT_RE = re.compile(
    r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
    re.DOTALL,
)
_TAG_RE = re.compile(r"<[^>]+>")


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


def _clean(text: str) -> str:
    return html.unescape(_TAG_RE.sub("", text)).strip()


def web_search(query: str, max_results: int = 5) -> ToolResult:
    """Search the web (DuckDuckGo) and return top result titles + URLs."""
    try:
        import requests
    except ImportError:
        return ToolResult(success=False, output="", error="requests not installed")

    try:
        resp = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            timeout=20,
            headers={"User-Agent": "NOVA-Assistant"},
        )
    except Exception as e:  # noqa: BLE001 - network errors surfaced to agent
        return ToolResult(success=False, output="", error=str(e))

    results = []
    for href, title in _RESULT_RE.findall(resp.text):
        # DuckDuckGo wraps external links in a redirect with uddg=<url>.
        m = re.search(r"uddg=([^&]+)", href)
        url = unquote(m.group(1)) if m else href
        results.append(f"{_clean(title)} - {url}")
        if len(results) >= max_results:
            break

    if not results:
        return ToolResult(success=True, output="(no results)")
    return ToolResult(success=True, output="\n".join(results))


def register(registry: ToolRegistry) -> None:
    registry.register(
        "web_fetch",
        "Fetch the contents of a web page via HTTP GET",
        web_fetch,
        {"url": "http(s) URL", "timeout": "seconds (optional)"},
    )
    registry.register(
        "web_search",
        "Search the web and return top result titles and URLs",
        web_search,
        {"query": "search terms", "max_results": "count (optional)"},
    )
