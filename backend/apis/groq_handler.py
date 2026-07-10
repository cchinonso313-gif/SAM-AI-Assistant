import asyncio
import logging
from typing import Optional

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

from backend.config import GROQ_CONFIG

logger = logging.getLogger(__name__)

class GroqHandler:
    """Handles Groq API calls"""
    
    def __init__(self):
        logger.info("🔧 Initializing Groq Handler...")
        self.config = GROQ_CONFIG
        self.client = None
        self.is_ready = False
    
    async def initialize(self) -> bool:
        """Initialize Groq API"""
        try:
            if not GROQ_AVAILABLE:
                logger.warning("Groq library not installed")
                return False
            
            if not self.config['api_key']:
                raise ValueError("Groq API key not configured")
            
            self.client = Groq(api_key=self.config['api_key'])
            self.is_ready = True
            
            logger.info(f"✅ Groq Handler ready (Model: {self.config['model']})")
            return True
        
        except Exception as e:
            logger.error(f"❌ Groq initialization failed: {e}")
            self.is_ready = False
            return False
    
    async def generate(self, prompt: str) -> Optional[str]:
        """Generate response from Groq"""
        if not self.is_ready:
            logger.warning("Groq not ready")
            return None
        
        try:
            logger.info("⚡ Querying Groq...")
            
            loop = asyncio.get_event_loop()
            
            def _generate():
                response = self.client.chat.completions.create(
                    model=self.config['model'],
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.config['temperature'],
                    max_tokens=self.config['max_tokens']
                )
                return response.choices[0].message.content
            
            # Run in executor to avoid blocking
            result = await loop.run_in_executor(None, _generate)
            logger.info(f"✅ Groq response received ({len(result)} chars)")
            return result
        
        except Exception as e:
            logger.error(f"❌ Groq generation error: {e}")
            return None
