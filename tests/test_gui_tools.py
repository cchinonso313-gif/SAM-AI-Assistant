import sys
from unittest.mock import MagicMock

import pytest

from backend.agent.tools import gui_tools


@pytest.fixture
def fake_pyautogui(monkeypatch):
    fake = MagicMock()
    fake.size.return_value = (1920, 1080)
    monkeypatch.setitem(sys.modules, "pyautogui", fake)
    return fake


@pytest.fixture
def fake_pygetwindow(monkeypatch):
    fake = MagicMock()
    monkeypatch.setitem(sys.modules, "pygetwindow", fake)
    return fake


class TestGuiTools:
    def test_screen_size(self, fake_pyautogui):
        result = gui_tools.screen_size()
        assert result.success and result.output == "1920x1080"

    def test_screen_size_unavailable(self, monkeypatch):
        def boom():
            raise RuntimeError("no display")

        monkeypatch.setattr(gui_tools, "_pyautogui", boom)
        result = gui_tools.screen_size()
        assert result.success is False

    def test_move_mouse(self, fake_pyautogui):
        result = gui_tools.move_mouse(10, 20)
        fake_pyautogui.moveTo.assert_called_once()
        assert result.success

    def test_click(self, fake_pyautogui):
        result = gui_tools.click(5, 5, button="right", clicks=2)
        fake_pyautogui.click.assert_called_once()
        assert result.success

    def test_type_text(self, fake_pyautogui):
        result = gui_tools.type_text("hello")
        fake_pyautogui.typewrite.assert_called_once()
        assert "5 chars" in result.output

    def test_type_text_too_long(self, fake_pyautogui):
        result = gui_tools.type_text("x" * (gui_tools.MAX_TYPE_LEN + 1))
        assert result.success is False

    def test_press_hotkey(self, fake_pyautogui):
        gui_tools.press_key("ctrl+c")
        fake_pyautogui.hotkey.assert_called_once_with("ctrl", "c")

    def test_press_single_key(self, fake_pyautogui):
        gui_tools.press_key("enter")
        fake_pyautogui.press.assert_called_once_with("enter")

    def test_screenshot(self, fake_pyautogui, tmp_path):
        target = tmp_path / "shot.png"
        result = gui_tools.screenshot(str(target))
        fake_pyautogui.screenshot.return_value.save.assert_called_once()
        assert result.output == str(target)

    def test_list_windows(self, fake_pygetwindow):
        fake_pygetwindow.getAllTitles.return_value = ["Editor", "", "Browser"]
        result = gui_tools.list_windows()
        assert "Editor" in result.output and "Browser" in result.output

    def test_focus_window_found(self, fake_pygetwindow):
        win = MagicMock()
        fake_pygetwindow.getWindowsWithTitle.return_value = [win]
        result = gui_tools.focus_window("Editor")
        win.activate.assert_called_once()
        assert result.success

    def test_focus_window_missing(self, fake_pygetwindow):
        fake_pygetwindow.getWindowsWithTitle.return_value = []
        result = gui_tools.focus_window("Nope")
        assert result.success is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
