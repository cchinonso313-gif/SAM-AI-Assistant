import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from backend.core.memory_manager import MemoryManager
import tempfile
from pathlib import Path

class TestMemoryManager:
    """Test suite for Memory Manager"""
    
    @pytest.fixture
    def manager(self):
        """Create memory manager instance"""
        return MemoryManager()
    
    def test_memory_manager_initialization(self, manager):
        """Test memory manager initializes"""
        assert manager.history == []
        assert manager.context == {}
        assert manager.learning_data == {}
    
    @pytest.mark.asyncio
    async def test_store_interaction(self, manager):
        """Test storing interaction"""
        interaction_id = await manager.store_interaction(
            user_input="Test input",
            response="Test response"
        )
        assert interaction_id is not None
        assert len(manager.history) == 1
        assert manager.history[0]['user_input'] == "Test input"
    
    @pytest.mark.asyncio
    async def test_get_context(self, manager):
        """Test getting context"""
        await manager.store_interaction(user_input="Test")
        context = await manager.get_context()
        assert 'recent_interactions' in context
        assert 'total_interactions' in context
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, manager):
        """Test getting statistics"""
        await manager.store_interaction(user_input="Test", is_voice=True)
        await manager.store_interaction(user_input="Test2", is_voice=False)
        
        stats = manager.get_statistics()
        assert stats['total_interactions'] == 2
        assert stats['voice_interactions'] == 1
        assert stats['text_interactions'] == 1
    
    @pytest.mark.asyncio
    async def test_cleanup_old_history(self, manager):
        """Test cleaning up old history"""
        await manager.store_interaction(user_input="Test")
        removed = await manager._cleanup_old_history()
        # Should not remove recent entries
        assert len(manager.history) == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
