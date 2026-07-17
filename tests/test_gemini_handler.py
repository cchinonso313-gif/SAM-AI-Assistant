import pytest
from unittest.mock import MagicMock, patch

import backend.apis.gemini_handler as gemini_module
from backend.apis.gemini_handler import GeminiHandler


class TestGeminiHandler:
    """Test suite for the Gemini API handler"""

    @pytest.fixture
    def handler(self):
        return GeminiHandler()

    def test_initialization(self, handler):
        """Handler should start not ready with no model"""
        assert handler.model is None
        assert handler.is_ready is False
        assert handler.config is gemini_module.GEMINI_CONFIG

    @pytest.mark.asyncio
    async def test_initialize_without_library(self, handler, monkeypatch):
        """Initialization should fail gracefully when genai is unavailable"""
        monkeypatch.setattr(gemini_module, "GENAI_AVAILABLE", False)

        result = await handler.initialize()

        assert result is False
        assert handler.is_ready is False

    @pytest.mark.asyncio
    async def test_initialize_without_api_key(self, handler, monkeypatch):
        """Initialization should fail when no API key is configured"""
        monkeypatch.setattr(gemini_module, "GENAI_AVAILABLE", True)
        handler.config = dict(handler.config, api_key=None)

        result = await handler.initialize()

        assert result is False
        assert handler.is_ready is False

    @pytest.mark.asyncio
    async def test_initialize_success(self, handler, monkeypatch):
        """A valid configuration should initialize the model"""
        monkeypatch.setattr(gemini_module, "GENAI_AVAILABLE", True)
        handler.config = dict(handler.config, api_key="test-key")

        fake_genai = MagicMock()
        fake_genai.GenerativeModel.return_value = MagicMock()
        monkeypatch.setattr(gemini_module, "genai", fake_genai)

        result = await handler.initialize()

        assert result is True
        assert handler.is_ready is True
        fake_genai.configure.assert_called_once_with(api_key="test-key")

    @pytest.mark.asyncio
    async def test_generate_when_not_ready(self, handler):
        """Generation should return None when the handler is not ready"""
        assert handler.is_ready is False
        assert await handler.generate("hello") is None

    @pytest.mark.asyncio
    async def test_generate_success(self, handler, monkeypatch):
        """Generation should return the model's text response"""
        monkeypatch.setattr(gemini_module, "genai", MagicMock())
        handler.is_ready = True

        mock_response = MagicMock()
        mock_response.text = "generated text"
        handler.model = MagicMock()
        handler.model.generate_content.return_value = mock_response

        result = await handler.generate("prompt")

        assert result == "generated text"
        handler.model.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_handles_errors(self, handler, monkeypatch):
        """Generation errors should be caught and return None"""
        monkeypatch.setattr(gemini_module, "genai", MagicMock())
        handler.is_ready = True
        handler.model = MagicMock()
        handler.model.generate_content.side_effect = RuntimeError("api down")

        assert await handler.generate("prompt") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
