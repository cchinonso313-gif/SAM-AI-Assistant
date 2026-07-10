import asyncio
import logging
from typing import Optional, Dict, Any
from backend.apis.gemini_handler import GeminiHandler
from backend.apis.groq_handler import GroqHandler
from backend.config import DEFAULT_MODEL, FALLBACK_MODEL, DEBUG_MODE

logger = logging.getLogger(__name__)

class APIManager:
    """Manages API calls with failover and optimization"""
    
    def __init__(self):
        logger.info("🌐 Initializing API Manager...")
        
        self.gemini = GeminiHandler()
        self.groq = GroqHandler()
        self.default_model = DEFAULT_MODEL
        self.fallback_model = FALLBACK_MODEL
        self.model_stats = {'gemini': {'calls': 0, 'errors': 0}, 'groq': {'calls': 0, 'errors': 0}}
        
        logger.info("✅ API Manager initialized")
    
    async def initialize(self):
        """Initialize all API handlers"""
        logger.info("Initializing API handlers...")
        
        try:
            await self.gemini.initialize()
            logger.info("✅ Gemini API ready")
        except Exception as e:
            logger.warning(f"⚠️ Gemini initialization failed: {e}")
        
        try:
            await self.groq.initialize()
            logger.info("✅ Groq API ready")
        except Exception as e:
            logger.warning(f"⚠️ Groq initialization failed: {e}")
    
    async def generate_response(
        self,
        prompt: str,
        context: Dict[str, Any] = None,
        model_preference: str = None
    ) -> str:
        """Generate response with automatic failover"""
        logger.info(f"🔮 Generating response using {model_preference or self.default_model}")
        
        # Select primary model
        primary_model = model_preference or self.default_model
        models = [primary_model] if primary_model != self.fallback_model else [primary_model, self.fallback_model]
        if self.fallback_model not in models:
            models.append(self.fallback_model)
        
        for model in models:
            try:
                response = await self._call_model(
                    model=model,
                    prompt=prompt,
                    context=context
                )
                
                if response:
                    self.model_stats[model]['calls'] += 1
                    logger.info(f"✅ Response generated via {model}")
                    return response
            
            except Exception as e:
                logger.warning(f"⚠️ {model.upper()} failed: {e}")
                self.model_stats[model]['errors'] += 1
                continue
        
        # All models failed
        logger.error("❌ All API models failed")
        return "I apologize, but I'm currently unable to process your request. Please try again later."
    
    async def _call_model(
        self,
        model: str,
        prompt: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Call specific model with context"""
        
        # Build full prompt with context
        full_prompt = self._build_prompt(prompt, context)
        
        if model == 'gemini':
            return await self.gemini.generate(full_prompt)
        elif model == 'groq':
            return await self.groq.generate(full_prompt)
        else:
            raise ValueError(f"Unknown model: {model}")
    
    def _build_prompt(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Build enhanced prompt with context"""
        if not context:
            return prompt
        
        context_str = ""
        
        # Add recent interactions
        if context.get('recent_interactions'):
            context_str += "\nRecent conversation:\n"
            for interaction in context['recent_interactions'][-3:]:
                context_str += f"- User: {interaction['user_input']}\n"
                if interaction.get('response'):
                    context_str += f"  SAM: {interaction['response'][:100]}...\n"
        
        # Add mood context
        if context.get('mood_history'):
            context_str += f"\nRecent mood: {context['mood_history'][-1] if context['mood_history'] else 'neutral'}\n"
        
        full_prompt = f"{context_str}\nCurrent request: {prompt}"
        return full_prompt
    
    def get_stats(self) -> Dict:
        """Get API usage statistics"""
        return self.model_stats
    
    def reset_stats(self):
        """Reset statistics"""
        for model in self.model_stats:
            self.model_stats[model]['calls'] = 0
            self.model_stats[model]['errors'] = 0
        logger.info("📊 Statistics reset")
