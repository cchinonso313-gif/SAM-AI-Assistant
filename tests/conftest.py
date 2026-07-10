import pytest
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv('GEMINI_API_KEY', 'test_key_gemini')
    monkeypatch.setenv('GROQ_API_KEY', 'test_key_groq')
    monkeypatch.setenv('DEBUG_MODE', 'True')
