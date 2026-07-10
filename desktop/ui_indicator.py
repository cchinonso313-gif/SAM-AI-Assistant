import logging
import sys
from pathlib import Path

try:
    from PyQt6.QtWidgets import QApplication, QWidget
    from PyQt6.QtCore import Qt, QTimer, QPoint
    from PyQt6.QtGui import QPainter, QColor, QBrush, QPen
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from backend.config import INDICATOR_COLOR, INDICATOR_SIZE, INDICATOR_BLINK_RATE

logger = logging.getLogger(__name__)

class DesktopIndicator:
    """Glowing desktop indicator showing SAM is active"""
    
    def __init__(self):
        logger.info("🎨 Initializing Desktop Indicator...")
        
        if not PYQT_AVAILABLE:
            logger.warning("⚠️ PyQt6 not available - visual indicator disabled")
            self.window = None
            return
        
        try:
            self.app = QApplication.instance()
            if self.app is None:
                self.app = QApplication(sys.argv)
            
            self.window = GlowingCircle()
            self.is_visible = False
            logger.info("✅ Desktop Indicator initialized")
        
        except Exception as e:
            logger.error(f"❌ Indicator initialization failed: {e}")
            self.window = None
    
    def show(self):
        """Show the indicator"""
        if self.window is None:
            logger.warning("Indicator not available")
            return
        
        try:
            self.window.show()
            self.is_visible = True
            logger.info("✅ Indicator shown")
        except Exception as e:
            logger.error(f"Error showing indicator: {e}")
    
    def hide(self):
        """Hide the indicator"""
        if self.window is None:
            return
        
        try:
            self.window.hide()
            self.is_visible = False
            logger.info("✅ Indicator hidden")
        except Exception as e:
            logger.error(f"Error hiding indicator: {e}")
    
    def set_active(self, active: bool):
        """Set indicator active/inactive state"""
        if self.window:
            self.window.set_active(active)


class GlowingCircle(QWidget):
    """Glowing circle widget"""
    
    def __init__(self):
        super().__init__()
        self.is_active = True
        self.blink_state = True
        
        # Get screen dimensions
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        
        # Position at top center
        x = (screen_geometry.width() - INDICATOR_SIZE) // 2
        y = 10
        
        self.setGeometry(x, y, INDICATOR_SIZE, INDICATOR_SIZE)
        self.setWindowTitle("SAM - Active Indicator")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Blinking timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._blink)
        self.timer.start(INDICATOR_BLINK_RATE)
    
    def set_active(self, active: bool):
        """Set active state"""
        self.is_active = active
        self.update()
    
    def _blink(self):
        """Blink effect"""
        self.blink_state = not self.blink_state
        self.update()
    
    def paintEvent(self, event):
        """Paint the glowing circle"""
        if not self.is_active:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Parse color
        color = QColor(INDICATOR_COLOR)
        
        # Draw glow effect
        if self.blink_state:
            glow_color = QColor(color)
            glow_color.setAlpha(100)
            painter.setBrush(glow_color)
            painter.setPen(QPen(glow_color))
            painter.drawEllipse(2, 2, INDICATOR_SIZE - 4, INDICATOR_SIZE - 4)
        
        # Draw main circle
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color))
        painter.drawEllipse(5, 5, INDICATOR_SIZE - 10, INDICATOR_SIZE - 10)
