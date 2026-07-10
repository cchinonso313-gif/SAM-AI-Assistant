import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from backend.core.ai_engine import SAMEngine

class TestSAMEngine:
    """Test suite for SAM AI Engine"""
    
    @pytest.fixture
    def engine(self):
        """Create SAM engine instance"""
        return SAMEngine()
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine):
        """Test engine initializes correctly"""
        assert engine.name == "SAM"
        assert engine.is_active == False
        assert engine.is_listening == False
        assert engine.mood == "neutral"
    
    @pytest.mark.asyncio
    async def test_engine_activate(self, engine):
        """Test engine activation"""
        engine.activate()
        assert engine.is_active == True
    
    @pytest.mark.asyncio
    async def test_engine_deactivate(self, engine):
        """Test engine deactivation"""
        engine.activate()
        engine.deactivate()
        assert engine.is_active == False
    
    @pytest.mark.asyncio
    async def test_is_task_command(self, engine):
        """Test task command detection"""
        assert engine._is_task_command("write a python script") == True
        assert engine._is_task_command("generate code") == True
        assert engine._is_task_command("hello there") == False
    
    @pytest.mark.asyncio
    async def test_select_model(self, engine):
        """Test model selection logic"""
        assert engine._select_model("write code in Python") == "gemini"
        assert engine._select_model("what is the weather") == "groq"
    
    @pytest.mark.asyncio
    async def test_mood_analysis(self, engine):
        """Test mood analysis"""
        mood = await engine._analyze_mood("This is great!", "I'm happy to help")
        assert mood in ["happy", "neutral"]
        
        mood = await engine._analyze_mood("There's an error", "Something went wrong")
        assert mood in ["frustrated", "neutral"]
    
    @pytest.mark.asyncio
    async def test_initialize(self, engine):
        """Test engine initialization"""
        with patch.object(engine.api_manager, 'initialize', new_callable=AsyncMock):
            with patch.object(engine.memory_manager, 'load_history', new_callable=AsyncMock):
                await engine.initialize()
                engine.api_manager.initialize.assert_called_once()
                engine.memory_manager.load_history.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_shutdown(self, engine):
        """Test engine shutdown"""
        with patch.object(engine.memory_manager, 'save_history', new_callable=AsyncMock):
            await engine.shutdown()
            assert engine.is_active == False
            engine.memory_manager.save_history.assert_called_once()

class TestSAMProcess:
    """Test SAM process method"""
    
    @pytest.fixture
    def engine(self):
        return SAMEngine()
    
    @pytest.mark.asyncio
    async def test_process_text_input(self, engine):
        """Test processing text input"""
        with patch.object(engine.api_manager, 'generate_response', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Test response"
            with patch.object(engine.memory_manager, 'store_interaction', new_callable=AsyncMock) as mock_store:
                mock_store.return_value = "int_123"
                with patch.object(engine.memory_manager, 'get_context', new_callable=AsyncMock) as mock_context:
                    mock_context.return_value = {}
                    
                    response = await engine.process("Test command")
                    assert response == "Test response"
    
    @pytest.mark.asyncio
    async def test_process_with_task(self, engine):
        """Test processing task command"""
        with patch.object(engine.task_executor, 'execute', new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = "Task executed"
            with patch.object(engine.memory_manager, 'store_interaction', new_callable=AsyncMock):
                with patch.object(engine.memory_manager, 'get_context', new_callable=AsyncMock) as mock_context:
                    mock_context.return_value = {}
                    
                    response = await engine.process("write a python function")
                    mock_exec.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
