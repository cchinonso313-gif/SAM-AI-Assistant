import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.apis.api_manager import APIManager

class TestAPIManager:
    """Test suite for API Manager"""
    
    @pytest.fixture
    def manager(self):
        """Create API manager instance"""
        return APIManager()
    
    def test_api_manager_initialization(self, manager):
        """Test API manager initializes"""
        assert manager.gemini is not None
        assert manager.groq is not None
        assert manager.default_model == 'gemini'
        assert manager.fallback_model == 'groq'
    
    @pytest.mark.asyncio
    async def test_initialize(self, manager):
        """Test API initialization"""
        with patch.object(manager.gemini, 'initialize', new_callable=AsyncMock) as mock_g:
            with patch.object(manager.groq, 'initialize', new_callable=AsyncMock) as mock_gr:
                mock_g.return_value = True
                mock_gr.return_value = True
                
                await manager.initialize()
                mock_g.assert_called_once()
                mock_gr.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_response(self, manager):
        """Test response generation"""
        with patch.object(manager, '_call_model', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "Test response"
            
            response = await manager.generate_response("Test prompt")
            assert response == "Test response"
    
    @pytest.mark.asyncio
    async def test_failover_mechanism(self, manager):
        """Test API failover"""
        # First model fails, second succeeds
        with patch.object(manager, '_call_model', new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = [None, "Fallback response"]
            
            response = await manager.generate_response("Test")
            assert response == "Fallback response"
    
    def test_get_stats(self, manager):
        """Test getting statistics"""
        manager.model_stats['gemini']['calls'] = 5
        manager.model_stats['groq']['calls'] = 3
        
        stats = manager.get_stats()
        assert stats['gemini']['calls'] == 5
        assert stats['groq']['calls'] == 3
    
    def test_reset_stats(self, manager):
        """Test resetting statistics"""
        manager.model_stats['gemini']['calls'] = 10
        manager.reset_stats()
        assert manager.model_stats['gemini']['calls'] == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
