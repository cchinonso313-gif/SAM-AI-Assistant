import asyncio
import logging
import speech_recognition as sr
import pyttsx3
from typing import Optional
from backend.config import VOICE_ENABLED, MIC_INDEX, VOICE_RATE, VOICE_VOLUME, TTS_ENGINE

logger = logging.getLogger(__name__)

class VoiceProcessor:
    """Handles voice input and output processing"""
    
    def __init__(self):
        logger.info("🎤 Initializing Voice Processor...")
        
        self.recognizer = sr.Recognizer()

        # Initialize the TTS engine defensively. An unavailable or misconfigured
        # driver must not crash the whole assistant.
        self.engine = self._init_tts_engine()
        if self.engine is not None:
            self.engine.setProperty('rate', VOICE_RATE)
            self.engine.setProperty('volume', VOICE_VOLUME)

        # Microphone access can also fail on headless machines.
        try:
            self.mic = sr.Microphone(device_index=MIC_INDEX)
        except Exception as e:  # noqa: BLE001 - degrade gracefully
            logger.warning(f"⚠️ Microphone unavailable: {e}")
            self.mic = None
        
        logger.info("✅ Voice Processor initialized")

    @staticmethod
    def _init_tts_engine():
        """Create a pyttsx3 engine, falling back to the default driver."""
        driver = TTS_ENGINE or None
        try:
            return pyttsx3.init(driver)
        except Exception as e:  # noqa: BLE001 - retry with platform default
            logger.warning(f"⚠️ TTS driver '{driver}' failed ({e}); using default")
            try:
                return pyttsx3.init()
            except Exception as e2:  # noqa: BLE001 - voice output disabled
                logger.error(f"❌ TTS engine unavailable: {e2}")
                return None

    def set_voice_properties(self, rate: int = None, volume: float = None):
        """Update TTS rate and/or volume at runtime."""
        if self.engine is None:
            logger.warning("TTS engine unavailable; cannot set properties")
            return
        if rate is not None:
            self.engine.setProperty('rate', rate)
        if volume is not None:
            self.engine.setProperty('volume', volume)
    
    async def speech_to_text(self, timeout: int = 10, phrase_time_limit: int = 15) -> Optional[str]:
        """Convert speech to text asynchronously"""
        if not VOICE_ENABLED:
            logger.warning("Voice input disabled")
            return None
        
        try:
            logger.info("👂 Listening for speech...")
            
            loop = asyncio.get_event_loop()
            
            # Run in executor to avoid blocking
            def _listen():
                with self.mic as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(
                        source,
                        timeout=timeout,
                        phrase_time_limit=phrase_time_limit
                    )
                
                try:
                    # Use Google Speech Recognition (free)
                    text = self.recognizer.recognize_google(audio)
                    logger.info(f"🎤 Recognized: {text}")
                    return text
                except sr.UnknownValueError:
                    logger.warning("Could not understand audio")
                    return None
                except sr.RequestError as e:
                    logger.error(f"Speech recognition error: {e}")
                    return None
            
            text = await loop.run_in_executor(None, _listen)
            return text
            
        except Exception as e:
            logger.error(f"❌ Speech-to-text error: {e}")
            return None
    
    async def text_to_speech(self, text: str) -> bool:
        """Convert text to speech asynchronously"""
        if not VOICE_ENABLED:
            logger.warning("Voice output disabled")
            return False
        
        try:
            logger.info(f"🔊 Speaking: {text[:50]}...")
            
            loop = asyncio.get_event_loop()
            
            def _speak():
                self.engine.say(text)
                self.engine.runAndWait()
            
            # Run in executor to avoid blocking
            await loop.run_in_executor(None, _speak)
            
            logger.info("✅ Speech complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Text-to-speech error: {e}")
            return False
    
    def list_microphones(self):
        """List available microphones"""
        logger.info("🎙️ Available Microphones:")
        for i, mic_name in enumerate(sr.Microphone.list_microphone_names()):
            logger.info(f"  {i}: {mic_name}")
