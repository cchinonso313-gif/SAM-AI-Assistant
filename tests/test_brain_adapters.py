import pytest
from unittest.mock import AsyncMock, MagicMock

from backend.brains.adapters import GeminiBrain, GroqBrain


class TestBrainAdapters:
    @pytest.mark.asyncio
    async def test_gemini_brain_delegates(self):
        handler = MagicMock()
        handler.initialize = AsyncMock(return_value=True)
        handler.generate = AsyncMock(return_value="gemini text")
        handler.is_ready = True

        brain = GeminiBrain(handler=handler)
        assert brain.name == "gemini"
        assert await brain.initialize() is True
        assert brain.is_ready is True
        assert brain.is_available is True
        assert await brain.generate("p") == "gemini text"

    @pytest.mark.asyncio
    async def test_groq_brain_delegates(self):
        handler = MagicMock()
        handler.initialize = AsyncMock(return_value=False)
        handler.generate = AsyncMock(return_value="groq text")
        handler.is_ready = False

        brain = GroqBrain(handler=handler)
        assert brain.name == "groq"
        assert await brain.initialize() is False
        assert brain.is_available is False
        assert await brain.generate("p") == "groq text"

    def test_priority_override(self):
        brain = GeminiBrain(handler=MagicMock(), priority=1)
        assert brain.priority == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
