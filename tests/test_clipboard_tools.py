import sys
from unittest.mock import MagicMock

import pytest

from backend.agent.tools import clipboard_tools


@pytest.fixture
def fake_pyperclip(monkeypatch):
    fake = MagicMock()
    monkeypatch.setitem(sys.modules, "pyperclip", fake)
    return fake


def test_copy(fake_pyperclip):
    result = clipboard_tools.copy_to_clipboard("hello")
    fake_pyperclip.copy.assert_called_once_with("hello")
    assert result.success


def test_paste(fake_pyperclip):
    fake_pyperclip.paste.return_value = "clip contents"
    result = clipboard_tools.paste_from_clipboard()
    assert result.output == "clip contents"


def test_copy_unavailable(monkeypatch):
    monkeypatch.setitem(sys.modules, "pyperclip", None)
    result = clipboard_tools.copy_to_clipboard("x")
    assert result.success is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
