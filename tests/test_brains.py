import pytest

from backend.brains.base import Brain
from backend.brains.router import BrainRouter


class FakeBrain(Brain):
    def __init__(self, name, priority=100, available=True, response="ok", raises=False):
        super().__init__(name=name, priority=priority)
        self._available = available
        self._response = response
        self._raises = raises

    async def initialize(self) -> bool:
        self.is_ready = self._available
        return self.is_ready

    async def generate(self, prompt: str):
        if self._raises:
            raise RuntimeError("boom")
        return self._response

    @property
    def is_available(self) -> bool:
        return self._available


class TestBrainRouter:
    def test_register_and_list_orders_by_priority(self):
        router = BrainRouter()
        router.register(FakeBrain("b", priority=20)).register(FakeBrain("a", priority=10))
        assert router.list_brains() == ["a", "b"]

    def test_get_and_unregister(self):
        router = BrainRouter()
        router.register(FakeBrain("x"))
        assert router.get("x") is not None
        router.unregister("x")
        assert router.get("x") is None

    @pytest.mark.asyncio
    async def test_initialize_reports_readiness(self):
        router = BrainRouter()
        router.register(FakeBrain("up", available=True))
        router.register(FakeBrain("down", available=False))

        results = await router.initialize()

        assert results == {"up": True, "down": False}

    @pytest.mark.asyncio
    async def test_generate_uses_preferred_first(self):
        router = BrainRouter()
        router.register(FakeBrain("primary", priority=10, response="primary"))
        router.register(FakeBrain("secondary", priority=20, response="secondary"))

        assert await router.generate("hi", preferred="secondary") == "secondary"

    @pytest.mark.asyncio
    async def test_generate_fails_over(self):
        router = BrainRouter()
        router.register(FakeBrain("bad", priority=10, raises=True))
        router.register(FakeBrain("good", priority=20, response="recovered"))

        result = await router.generate("hi")

        assert result == "recovered"
        assert router.get_stats()["bad"]["errors"] == 1
        assert router.get_stats()["good"]["calls"] == 1

    @pytest.mark.asyncio
    async def test_generate_skips_unavailable(self):
        router = BrainRouter()
        router.register(FakeBrain("offline", priority=10, available=False))
        router.register(FakeBrain("online", priority=20, response="online"))

        assert await router.generate("hi") == "online"

    @pytest.mark.asyncio
    async def test_generate_returns_none_when_all_fail(self):
        router = BrainRouter()
        router.register(FakeBrain("a", raises=True))

        assert await router.generate("hi") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
