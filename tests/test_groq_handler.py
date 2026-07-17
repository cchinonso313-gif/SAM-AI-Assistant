import pytest
from unittest.mock import MagicMock, patch

import backend.apis.groq_handler as groq_module
from backend.apis.groq_handler import GroqHandler


class TestGroqHandler:
    """Test suite for the Groq API handler"""

    @pytest.fixture
    def handler(self):
        return GroqHandler()

    def test_initialization(self, handler):
        """Handler should start not ready with no client"""
        assert handler.client is None
        assert handler.is_ready is False
        assert handler.config is groq_module.GROQ_CONFIG

    @pytest.mark.asyncio
    async def test_initialize_without_library(self, handler, monkeypatch):
        """Initialization should fail gracefully when groq is unavailable"""
        monkeypatch.setattr(groq_module, "GROQ_AVAILABLE", False)

        result = await handler.initialize()

        assert result is False
        assert handler.is_ready is False

    @pytest.mark.asyncio
    async def test_initialize_without_api_key(self, handler, monkeypatch):
        """Initialization should fail when no API key is configured"""
        monkeypatch.setattr(groq_module, "GROQ_AVAILABLE", True)
        handler.config = dict(handler.config, api_key=None)

        result = await handler.initialize()

        assert result is False
        assert handler.is_ready is False

    @pytest.mark.asyncio
    async def test_initialize_success(self, handler, monkeypatch):
        """A valid configuration should create the Groq client"""
        monkeypatch.setattr(groq_module, "GROQ_AVAILABLE", True)
        handler.config = dict(handler.config, api_key="test-key")

        fake_groq = MagicMock(return_value=MagicMock())
        monkeypatch.setattr(groq_module, "Groq", fake_groq)

        result = await handler.initialize()

        assert result is True
        assert handler.is_ready is True
        fake_groq.assert_called_once_with(api_key="test-key")

    @pytest.mark.asyncio
    async def test_generate_when_not_ready(self, handler):
        """Generation should return None when the handler is not ready"""
        assert handler.is_ready is False
        assert await handler.generate("hello") is None

    @pytest.mark.asyncio
    async def test_generate_success(self, handler):
        """Generation should return the completion content"""
        handler.is_ready = True

        message = MagicMock()
        message.message.content = "groq reply"
        completion = MagicMock()
        completion.choices = [message]

        handler.client = MagicMock()
        handler.client.chat.completions.create.return_value = completion

        result = await handler.generate("prompt")

        assert result == "groq reply"
        handler.client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_handles_errors(self, handler):
        """Generation errors should be caught and return None"""
        handler.is_ready = True
        handler.client = MagicMock()
        handler.client.chat.completions.create.side_effect = RuntimeError("api down")

        assert await handler.generate("prompt") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
