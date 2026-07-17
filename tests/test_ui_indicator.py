import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from desktop import ui_indicator
from desktop.ui_indicator import DesktopIndicator

pytestmark = pytest.mark.skipif(
    not ui_indicator.PYQT_AVAILABLE, reason="PyQt6 not installed"
)


@pytest.fixture(scope="module")
def indicator():
    return DesktopIndicator()


def test_indicator_creates_window(indicator):
    assert indicator.window is not None


def test_show_hide(indicator):
    indicator.show()
    assert indicator.is_visible is True
    indicator.hide()
    assert indicator.is_visible is False


def test_set_state_valid(indicator):
    indicator.set_state("thinking")
    assert indicator.window.state == "thinking"


def test_set_state_invalid_ignored(indicator):
    indicator.set_state("thinking")
    indicator.set_state("not-a-state")
    assert indicator.window.state == "thinking"


def test_set_active_maps_to_state(indicator):
    indicator.set_active(True)
    assert indicator.window.state == "active"
    indicator.set_active(False)
    assert indicator.window.state == "idle"


def test_process_events_runs(indicator):
    indicator.process_events()  # should not raise


def test_paint_tick(indicator):
    # Advance the animation phase and repaint to exercise paintEvent.
    indicator.window._tick()
    indicator.process_events()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
