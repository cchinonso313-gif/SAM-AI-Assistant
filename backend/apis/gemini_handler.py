import asyncio
import logging
from typing import Optional

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from backend.config import GEMINI_CONFIG

logger = logging.getLogger(__name__)

class GeminiHandler:
    """Handles Gemini API calls"""
    
    def __init__(self):
        logger.info("🔧 Initializing Gemini Handler...")
        self.config = GEMINI_CONFIG
        self.model = None
        self.is_ready = False
    
    async def initialize(self) -> bool:
        """Initialize Gemini API"""
        try:
            if not GENAI_AVAILABLE:
                logger.warning("Google Generative AI library not installed")
                return False
            
            if not self.config['api_key']:
                raise ValueError("Gemini API key not configured")
            
            genai.configure(api_key=self.config['api_key'])
            self.model = genai.GenerativeModel(self.config['model'])
            self.is_ready = True
            
            logger.info(f"✅ Gemini Handler ready (Model: {self.config['model']})")
            return True
        
        except Exception as e:
            logger.error(f"❌ Gemini initialization failed: {e}")
            self.is_ready = False
            return False
    
    async def generate(self, prompt: str) -> Optional[str]:
        """Generate response from Gemini"""
        if not self.is_ready:
            logger.warning("Gemini not ready")
            return None
        
        try:
            logger.info("🧠 Querying Gemini...")
            
            loop = asyncio.get_event_loop()
            
            def _generate():
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=self.config['temperature'],
                        max_output_tokens=self.config['max_tokens']
                    )
                )
                return response.text
            
            # Run in executor to avoid blocking
            result = await loop.run_in_executor(None, _generate)
            logger.info(f"✅ Gemini response received ({len(result)} chars)")
            return result
        
        except Exception as e:
            logger.error(f"❌ Gemini generation error: {e}")
            return None
