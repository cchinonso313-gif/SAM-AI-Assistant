import logging
from typing import Dict, List, Optional

from backend.brains.base import Brain

logger = logging.getLogger(__name__)


class BrainRouter:
    """Routes generation requests across multiple brains with failover.

    Brains are tried in order of: an explicit ``preferred`` name first, then
    ascending ``priority``. Adding a new provider is a one-liner::

        router.register(MyBrain())
    """

    def __init__(self):
        self._brains: Dict[str, Brain] = {}

    def register(self, brain: Brain) -> "BrainRouter":
        """Register a brain (returns self for chaining)."""
        self._brains[brain.name] = brain
        logger.info(f"🧠 Registered brain: {brain.name} (priority={brain.priority})")
        return self

    def unregister(self, name: str) -> None:
        self._brains.pop(name, None)

    def get(self, name: str) -> Optional[Brain]:
        return self._brains.get(name)

    def list_brains(self) -> List[str]:
        return [b.name for b in self._ordered()]

    def _ordered(self) -> List[Brain]:
        return sorted(self._brains.values(), key=lambda b: b.priority)

    async def initialize(self) -> Dict[str, bool]:
        """Initialize every registered brain, returning per-brain readiness."""
        results: Dict[str, bool] = {}
        for brain in self._ordered():
            try:
                results[brain.name] = await brain.initialize()
            except Exception as e:  # noqa: BLE001 - never let one brain break init
                logger.warning(f"⚠️ Brain {brain.name} failed to initialize: {e}")
                results[brain.name] = False
        return results

    def _selection_order(self, preferred: Optional[str]) -> List[Brain]:
        ordered = self._ordered()
        if preferred and preferred in self._brains:
            pref = self._brains[preferred]
            ordered = [pref] + [b for b in ordered if b.name != preferred]
        return ordered

    async def generate(self, prompt: str, preferred: Optional[str] = None) -> Optional[str]:
        """Generate a response, failing over across available brains."""
        for brain in self._selection_order(preferred):
            if not brain.is_available:
                continue
            try:
                response = await brain.generate(prompt)
                if response:
                    brain.record_success()
                    logger.info(f"✅ Response via brain: {brain.name}")
                    return response
                logger.warning(f"⚠️ Brain {brain.name} returned no content")
            except Exception as e:  # noqa: BLE001 - failover to next brain
                logger.warning(f"⚠️ Brain {brain.name} error: {e}")
                brain.record_error()
                continue

        logger.error("❌ All brains failed or unavailable")
        return None

    def get_stats(self) -> Dict[str, Dict[str, int]]:
        return {name: dict(brain.stats) for name, brain in self._brains.items()}
