import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.core.voice_processor import VoiceProcessor

class TestVoiceProcessor:
    """Test suite for Voice Processor"""
    
    @pytest.fixture
    def processor(self):
        """Create voice processor instance"""
        return VoiceProcessor()
    
    def test_voice_processor_initialization(self, processor):
        """Test voice processor initializes"""
        assert processor.recognizer is not None
        assert processor.engine is not None
        assert processor.mic is not None
    
    @pytest.mark.asyncio
    async def test_speech_to_text_disabled(self, processor):
        """Test speech-to-text when disabled"""
        with patch('backend.core.voice_processor.VOICE_ENABLED', False):
            result = await processor.speech_to_text()
            assert result is None
    
    @pytest.mark.asyncio
    async def test_text_to_speech_disabled(self, processor):
        """Test text-to-speech when disabled"""
        with patch('backend.core.voice_processor.VOICE_ENABLED', False):
            result = await processor.text_to_speech("Test")
            assert result == False
    
    def test_list_microphones(self, processor):
        """Test listing microphones"""
        with patch('speech_recognition.Microphone.list_microphone_names') as mock_list:
            mock_list.return_value = ['Mic 1', 'Mic 2']
            processor.list_microphones()
            # Should not raise an error
    
    def test_set_voice_properties(self, processor):
        """Test setting voice properties"""
        processor.set_voice_properties(rate=200, volume=0.8)
        # Should not raise an error

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
