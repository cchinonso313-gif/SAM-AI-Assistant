import logging
import os
import sys

try:
    from PyQt6.QtWidgets import QApplication, QWidget
    from PyQt6.QtCore import Qt, QTimer, QRectF
    from PyQt6.QtGui import QPainter, QColor, QRadialGradient
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from backend.config import (
    INDICATOR_COLOR,
    INDICATOR_SIZE,
    INDICATOR_STATE_COLORS,
    ASSISTANT_NAME,
)

logger = logging.getLogger(__name__)

# Valid indicator states mapped to colors in config.
STATES = tuple(INDICATOR_STATE_COLORS.keys())

# Base class for the widget: the real QWidget when PyQt6 is present, otherwise
# a stand-in so this module still imports on headless systems without PyQt6.
_WidgetBase = QWidget if PYQT_AVAILABLE else object


class DesktopIndicator:
    """Glowing, always-on-top desktop indicator showing assistant state."""

    def __init__(self):
        logger.info("🎨 Initializing Desktop Indicator...")

        if not PYQT_AVAILABLE:
            logger.warning("⚠️ PyQt6 not available - visual indicator disabled")
            self.window = None
            return

        try:
            # On a headless Linux host (no display) fall back to Qt's
            # offscreen platform so construction never aborts the process.
            if (
                sys.platform not in ("win32", "darwin")
                and not os.environ.get("DISPLAY")
                and not os.environ.get("WAYLAND_DISPLAY")
                and not os.environ.get("QT_QPA_PLATFORM")
            ):
                os.environ["QT_QPA_PLATFORM"] = "offscreen"

            self.app = QApplication.instance() or QApplication(sys.argv)
            self.window = GlowingCircle()
            self.is_visible = False
            logger.info("✅ Desktop Indicator initialized")
        except Exception as e:  # noqa: BLE001 - headless envs may lack a display
            logger.error(f"❌ Indicator initialization failed: {e}")
            self.window = None

    def show(self):
        if self.window is None:
            return
        self.window.show()
        self.is_visible = True

    def hide(self):
        if self.window is None:
            return
        self.window.hide()
        self.is_visible = False

    def set_active(self, active: bool):
        """Backward-compatible on/off toggle."""
        self.set_state("active" if active else "idle")

    def set_state(self, state: str):
        """Set the visual state (idle/active/listening/thinking/speaking)."""
        if self.window:
            self.window.set_state(state)

    def process_events(self):
        """Pump the Qt event loop.

        Lets the indicator animate while the app runs its own asyncio loop,
        avoiding a separate GUI thread or extra dependencies.
        """
        if self.window is not None and getattr(self, "app", None) is not None:
            self.app.processEvents()


class GlowingCircle(_WidgetBase):
    """A smoothly pulsing, glowing circle rendered top-center of the screen."""

    #: Animation frame interval in milliseconds.
    FRAME_MS = 40

    def __init__(self):
        super().__init__()
        self.state = "active"
        self._phase = 0.0

        size = max(INDICATOR_SIZE, 24)
        # Reserve extra room around the core for the glow halo.
        self._canvas = int(size * 2.2)
        self._core = size

        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self._canvas) // 2
        y = 12
        self.setGeometry(x, y, self._canvas, self._canvas)

        self.setWindowTitle(f"{ASSISTANT_NAME} - Status")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(self.FRAME_MS)

    def set_state(self, state: str):
        if state in INDICATOR_STATE_COLORS:
            self.state = state
            self.update()

    def _tick(self):
        # Advance the pulse phase; wrap to keep it bounded.
        self._phase = (self._phase + 0.08) % (2 * 3.14159265)
        self.update()

    def _color(self) -> QColor:
        return QColor(INDICATOR_STATE_COLORS.get(self.state, INDICATOR_COLOR))

    def paintEvent(self, event):  # noqa: N802 - Qt signature
        import math

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = self._canvas / 2
        color = self._color()

        # Pulse factor oscillates between ~0.6 and ~1.0.
        pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(self._phase))

        # Outer glow halo via a radial gradient.
        halo_radius = (self._canvas / 2) * pulse
        gradient = QRadialGradient(center, center, halo_radius)
        glow = QColor(color)
        glow.setAlpha(int(150 * pulse))
        gradient.setColorAt(0.0, glow)
        edge = QColor(color)
        edge.setAlpha(0)
        gradient.setColorAt(1.0, edge)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(QRectF(center - halo_radius, center - halo_radius,
                                   halo_radius * 2, halo_radius * 2))

        # Solid core.
        core_r = self._core / 2
        painter.setBrush(color)
        painter.drawEllipse(QRectF(center - core_r, center - core_r,
                                   core_r * 2, core_r * 2))

        # Bright highlight for a glassy look.
        highlight = QColor(255, 255, 255, 90)
        painter.setBrush(highlight)
        hr = core_r * 0.4
        painter.drawEllipse(QRectF(center - hr * 1.2, center - hr * 1.4, hr, hr))
