"""Base class for external AI API handlers (Gemini, Groq, ...)."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from backend.utils import run_blocking

logger = logging.getLogger(__name__)


class BaseAPIHandler(ABC):
    """Shared lifecycle for API handlers: initialization and async generation.

    Subclasses provide the provider-specific pieces via the abstract methods.
    """

    #: Human-readable provider name, e.g. "Gemini".
    service_name: str = "API"
    #: Name of the client library, used in the "not installed" warning.
    library_name: str = ""
    #: Emoji shown in the "Querying ..." log line.
    query_emoji: str = "🔮"

    def __init__(self, config: Dict[str, Any]):
        logger.info(f"🔧 Initializing {self.service_name} Handler...")
        self.config = config
        self.is_ready = False

    async def initialize(self) -> bool:
        """Initialize the provider client, returning True on success."""
        try:
            if not self.is_available():
                logger.warning(f"{self.library_name} library not installed")
                return False

            if not self.config['api_key']:
                raise ValueError(f"{self.service_name} API key not configured")

            self._setup_client()
            self.is_ready = True

            logger.info(f"✅ {self.service_name} Handler ready (Model: {self.config['model']})")
            return True

        except Exception as e:
            logger.error(f"❌ {self.service_name} initialization failed: {e}")
            self.is_ready = False
            return False

    async def generate(self, prompt: str) -> Optional[str]:
        """Generate a response for the prompt, or None on failure."""
        if not self.is_ready:
            logger.warning(f"{self.service_name} not ready")
            return None

        try:
            logger.info(f"{self.query_emoji} Querying {self.service_name}...")
            result = await run_blocking(self._generate_sync, prompt)
            logger.info(f"✅ {self.service_name} response received ({len(result)} chars)")
            return result

        except Exception as e:
            logger.error(f"❌ {self.service_name} generation error: {e}")
            return None

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the provider's client library is importable."""

    @abstractmethod
    def _setup_client(self) -> None:
        """Configure the provider client using ``self.config``."""

    @abstractmethod
    def _generate_sync(self, prompt: str) -> str:
        """Perform the blocking generation call and return the text result."""
