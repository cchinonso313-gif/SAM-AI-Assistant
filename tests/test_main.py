import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import backend.main as main_module
from backend.main import SAMApplication


@pytest.fixture
def mock_engine():
    """Replace SAMEngine with a fully mocked async engine"""
    engine = MagicMock()
    engine.initialize = AsyncMock()
    engine.shutdown = AsyncMock()
    engine.process = AsyncMock(return_value="response")
    engine.listen = AsyncMock()
    engine.activate = MagicMock()
    # Disable the optional Qt desktop indicator during tests.
    with patch.object(main_module, "SAMEngine", return_value=engine), patch.object(
        main_module, "INDICATOR_ENABLED", False
    ):
        yield engine


class TestSAMApplication:
    """Test suite for the SAM application entry point"""

    def test_initialization(self, mock_engine):
        app = SAMApplication()
        assert app.engine is mock_engine
        assert app.is_running is False

    @pytest.mark.asyncio
    async def test_start_activates_engine(self, mock_engine):
        """start() should initialize and activate the engine"""
        app = SAMApplication()

        with patch.object(app, "_run_interactive_mode", new_callable=AsyncMock):
            await app.start()

        mock_engine.initialize.assert_awaited_once()
        mock_engine.activate.assert_called_once()
        assert app.is_running is True

    @pytest.mark.asyncio
    async def test_start_handles_failure(self, mock_engine):
        """start() should shut down when initialization fails"""
        mock_engine.initialize.side_effect = RuntimeError("boom")
        app = SAMApplication()

        await app.start()

        mock_engine.shutdown.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_shutdown(self, mock_engine):
        """shutdown() should stop running and shut the engine down"""
        app = SAMApplication()
        app.is_running = True

        await app.shutdown()

        assert app.is_running is False
        mock_engine.shutdown.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_shutdown_handles_errors(self, mock_engine):
        """shutdown() should swallow engine errors"""
        mock_engine.shutdown.side_effect = RuntimeError("fail")
        app = SAMApplication()

        await app.shutdown()  # should not raise

        assert app.is_running is False

    @pytest.mark.asyncio
    async def test_interactive_mode_exits_on_quit(self, mock_engine):
        """Interactive mode should exit when the user types a quit word"""
        app = SAMApplication()
        app.is_running = True

        async def fake_run_in_executor(_executor, _func, *args):
            return "exit"

        loop = MagicMock()
        loop.run_in_executor = fake_run_in_executor

        with patch("asyncio.get_event_loop", return_value=loop):
            await app._run_interactive_mode()

        assert app.is_running is False
        mock_engine.process.assert_not_called()

    @pytest.mark.asyncio
    async def test_interactive_mode_processes_input(self, mock_engine):
        """Interactive mode should process a command then exit"""
        app = SAMApplication()
        app.is_running = True

        inputs = iter(["hello there", "quit"])

        async def fake_run_in_executor(_executor, _func, *args):
            return next(inputs)

        loop = MagicMock()
        loop.run_in_executor = fake_run_in_executor

        with patch("asyncio.get_event_loop", return_value=loop):
            await app._run_interactive_mode()

        mock_engine.process.assert_awaited_once_with("hello there", is_voice=False)
        assert app.is_running is False


@pytest.mark.asyncio
async def test_main_runs_and_shuts_down(mock_engine):
    """The main() coroutine should start and shut down the application"""
    with patch.object(main_module.SAMApplication, "start", new_callable=AsyncMock) as mock_start:
        with patch.object(main_module.SAMApplication, "shutdown", new_callable=AsyncMock) as mock_shutdown:
            await main_module.main()

    mock_start.assert_awaited_once()
    mock_shutdown.assert_awaited_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
