import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class Brain(ABC):
    """Common interface for a single LLM backend ("brain").

    Concrete brains wrap a provider SDK. The router only depends on this
    interface, so adding a new provider means adding one subclass and
    registering it — nothing else changes.
    """

    #: Human readable identifier, e.g. ``"gemini"``.
    name: str = "brain"

    #: Lower numbers are preferred when no explicit preference is given.
    priority: int = 100

    def __init__(self, name: Optional[str] = None, priority: Optional[int] = None):
        if name is not None:
            self.name = name
        if priority is not None:
            self.priority = priority
        self.is_ready = False
        self.stats = {"calls": 0, "errors": 0}

    @abstractmethod
    async def initialize(self) -> bool:
        """Prepare the backend. Return True on success."""
        raise NotImplementedError

    @abstractmethod
    async def generate(self, prompt: str) -> Optional[str]:
        """Return a completion for ``prompt`` or ``None`` on failure."""
        raise NotImplementedError

    @property
    def is_available(self) -> bool:
        """Whether this brain can currently serve requests."""
        return self.is_ready

    def record_success(self) -> None:
        self.stats["calls"] += 1

    def record_error(self) -> None:
        self.stats["errors"] += 1

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Brain {self.name} ready={self.is_ready} priority={self.priority}>"
