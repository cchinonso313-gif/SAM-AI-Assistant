import logging
from typing import Optional

from backend.brains.base import Brain
from backend.apis.gemini_handler import GeminiHandler
from backend.apis.groq_handler import GroqHandler

logger = logging.getLogger(__name__)


class GeminiBrain(Brain):
    """Brain backed by Google Gemini."""

    name = "gemini"
    priority = 10

    def __init__(self, handler: Optional[GeminiHandler] = None, priority: Optional[int] = None):
        super().__init__(priority=priority)
        self.handler = handler or GeminiHandler()

    async def initialize(self) -> bool:
        self.is_ready = await self.handler.initialize()
        return self.is_ready

    async def generate(self, prompt: str) -> Optional[str]:
        return await self.handler.generate(prompt)

    @property
    def is_available(self) -> bool:
        return self.handler.is_ready


class GroqBrain(Brain):
    """Brain backed by Groq."""

    name = "groq"
    priority = 20

    def __init__(self, handler: Optional[GroqHandler] = None, priority: Optional[int] = None):
        super().__init__(priority=priority)
        self.handler = handler or GroqHandler()

    async def initialize(self) -> bool:
        self.is_ready = await self.handler.initialize()
        return self.is_ready

    async def generate(self, prompt: str) -> Optional[str]:
        return await self.handler.generate(prompt)

    @property
    def is_available(self) -> bool:
        return self.handler.is_ready
