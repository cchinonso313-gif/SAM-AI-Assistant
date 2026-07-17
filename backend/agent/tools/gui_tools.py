"""Desktop GUI automation tools (mouse, keyboard, screenshots, windows).

Backed by ``pyautogui``/``pygetwindow``, imported lazily so the rest of NOVA
works on machines without a display or those libraries installed. Designed for
legitimate local automation of the user's own machine.
"""

import logging
from pathlib import Path

from backend.agent.tool_registry import ToolRegistry, ToolResult

logger = logging.getLogger(__name__)

# Cap typed text so a runaway model can't flood the OS with keystrokes.
MAX_TYPE_LEN = 5000


def _pyautogui():
    import pyautogui  # noqa: WPS433 - lazy import; optional dependency

    pyautogui.FAILSAFE = True
    return pyautogui


def screen_size() -> ToolResult:
    """Return the primary screen resolution as ``WIDTHxHEIGHT``."""
    try:
        gui = _pyautogui()
    except Exception as e:  # noqa: BLE001
        return ToolResult(success=False, output="", error=f"GUI unavailable: {e}")
    w, h = gui.size()
    return ToolResult(success=True, output=f"{w}x{h}")


def move_mouse(x: int, y: int, duration: float = 0.2) -> ToolResult:
    """Move the mouse cursor to absolute screen coordinates."""
    try:
        gui = _pyautogui()
        gui.moveTo(int(x), int(y), duration=float(duration))
    except Exception as e:  # noqa: BLE001
        return ToolResult(success=False, output="", error=str(e))
    return ToolResult(success=True, output=f"Moved to ({x}, {y})")


def click(x: int = None, y: int = None, button: str = "left", clicks: int = 1) -> ToolResult:
    """Click at coordinates (or current position if x/y omitted)."""
    try:
        gui = _pyautogui()
        if x is not None and y is not None:
            gui.click(x=int(x), y=int(y), clicks=int(clicks), button=button)
        else:
            gui.click(clicks=int(clicks), button=button)
    except Exception as e:  # noqa: BLE001
        return ToolResult(success=False, output="", error=str(e))
    return ToolResult(success=True, output=f"Clicked {button} x{clicks}")


def type_text(text: str, interval: float = 0.0) -> ToolResult:
    """Type text using the keyboard."""
    if len(text) > MAX_TYPE_LEN:
        return ToolResult(success=False, output="", error="text too long")
    try:
        gui = _pyautogui()
        gui.typewrite(text, interval=float(interval))
    except Exception as e:  # noqa: BLE001
        return ToolResult(success=False, output="", error=str(e))
    return ToolResult(success=True, output=f"Typed {len(text)} chars")


def press_key(keys: str) -> ToolResult:
    """Press a key or hotkey combo, e.g. ``enter`` or ``ctrl+c``."""
    try:
        gui = _pyautogui()
        combo = [k.strip() for k in keys.split("+") if k.strip()]
        if len(combo) > 1:
            gui.hotkey(*combo)
        elif combo:
            gui.press(combo[0])
        else:
            return ToolResult(success=False, output="", error="no keys given")
    except Exception as e:  # noqa: BLE001
        return ToolResult(success=False, output="", error=str(e))
    return ToolResult(success=True, output=f"Pressed {keys}")


def screenshot(path: str = "") -> ToolResult:
    """Capture the screen to a PNG file and return its path."""
    try:
        gui = _pyautogui()
        target = Path(path).expanduser() if path else Path.home() / "nova_screenshot.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        img = gui.screenshot()
        img.save(str(target))
    except Exception as e:  # noqa: BLE001
        return ToolResult(success=False, output="", error=str(e))
    return ToolResult(success=True, output=str(target))


def list_windows() -> ToolResult:
    """List titles of open windows."""
    try:
        import pygetwindow as gw  # noqa: WPS433 - optional dependency

        titles = [t for t in gw.getAllTitles() if t.strip()]
    except Exception as e:  # noqa: BLE001
        return ToolResult(success=False, output="", error=f"window control unavailable: {e}")
    return ToolResult(success=True, output="\n".join(titles) or "(none)")


def focus_window(title: str) -> ToolResult:
    """Bring the first window whose title contains ``title`` to the front."""
    try:
        import pygetwindow as gw  # noqa: WPS433 - optional dependency

        matches = gw.getWindowsWithTitle(title)
        if not matches:
            return ToolResult(success=False, output="", error=f"no window matching '{title}'")
        matches[0].activate()
    except Exception as e:  # noqa: BLE001
        return ToolResult(success=False, output="", error=str(e))
    return ToolResult(success=True, output=f"Focused '{title}'")


def register(registry: ToolRegistry) -> None:
    registry.register("screen_size", "Get screen resolution", screen_size, {})
    registry.register(
        "move_mouse", "Move mouse to coordinates", move_mouse,
        {"x": "x px", "y": "y px", "duration": "seconds (optional)"},
    )
    registry.register(
        "click", "Click the mouse (optionally at x,y)", click,
        {"x": "x px (optional)", "y": "y px (optional)", "button": "left/right/middle", "clicks": "count"},
    )
    registry.register(
        "type_text", "Type text on the keyboard", type_text,
        {"text": "text to type", "interval": "seconds between keys (optional)"},
    )
    registry.register(
        "press_key", "Press a key or hotkey (e.g. ctrl+c)", press_key, {"keys": "key or combo"},
    )
    registry.register(
        "screenshot", "Capture the screen to a PNG", screenshot, {"path": "output path (optional)"},
    )
    registry.register("list_windows", "List open window titles", list_windows, {})
    registry.register(
        "focus_window", "Focus a window by title substring", focus_window, {"title": "window title"},
    )
