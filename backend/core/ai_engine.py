import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List
from backend.apis.api_manager import APIManager
from backend.core.voice_processor import VoiceProcessor
from backend.core.task_executor import TaskExecutor
from backend.core.memory_manager import MemoryManager
from backend.core.semantic_memory import SemanticMemory
from backend.brains import BrainRouter, GeminiBrain, GroqBrain
from backend.agent import Agent
from backend.agent.tools import build_default_registry
from backend.config import SAM_NAME, DEBUG_MODE, LOG_LEVEL, WAKE_WORD, AGENT_MAX_STEPS, DATA_DIR

# Configure logging
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

class SAMEngine:
    """Main AI Engine orchestrating all SAM components"""
    
    def __init__(self):
        logger.info(f"🤖 Initializing {SAM_NAME} AI Engine...")
        
        self.name = SAM_NAME
        self.api_manager = APIManager()
        self.voice_processor = VoiceProcessor()
        self.task_executor = TaskExecutor()
        self.memory_manager = MemoryManager()

        # Semantic long-term memory for cross-session vector recall.
        self.semantic_memory = SemanticMemory(path=DATA_DIR / "semantic_memory.json")

        # Multi-brain router (reuses the API manager's handlers) so more
        # providers can be registered later without touching the engine.
        self.brain_router = BrainRouter()
        self.brain_router.register(GeminiBrain(handler=self.api_manager.gemini))
        self.brain_router.register(GroqBrain(handler=self.api_manager.groq))

        # Autonomous agent with a modular tool registry.
        self.tool_registry = build_default_registry()
        self.agent = Agent(
            router=self.brain_router,
            registry=self.tool_registry,
            name=SAM_NAME,
            max_steps=AGENT_MAX_STEPS,
        )

        # Optional visual indicator; wired by the app layer to avoid Qt in
        # headless contexts.
        self.indicator = None

        self.is_active = False
        self.is_listening = False
        self.mood = "neutral"
        
        logger.info(f"✅ {SAM_NAME} Engine initialized successfully")

    def _set_indicator(self, state: str):
        """Update the desktop indicator state if one is attached."""
        if self.indicator is not None:
            try:
                self.indicator.set_state(state)
            except Exception as e:  # noqa: BLE001 - UI must never break logic
                logger.debug(f"Indicator update failed: {e}")

    async def run_task(self, goal: str, context: Optional[str] = None):
        """Run an autonomous multi-step task via the agent loop."""
        self._set_indicator("thinking")
        try:
            return await self.agent.run(goal, context=context)
        finally:
            self._set_indicator("active" if self.is_active else "idle")
    
    async def initialize(self):
        """Initialize all components asynchronously"""
        logger.info("Initializing SAM components...")
        await self.api_manager.initialize()
        await self.brain_router.initialize()
        await self.memory_manager.load_history()
        logger.info("✅ All components initialized")
    
    async def listen(self):
        """Listen for voice activation with wake word"""
        logger.info(f"👂 Listening for wake word: '{WAKE_WORD}'...")
        self.is_listening = True
        
        while self.is_listening:
            try:
                audio_text = await self.voice_processor.speech_to_text()
                if audio_text and WAKE_WORD.lower() in audio_text.lower():
                    logger.info(f"🎤 Wake word detected: {audio_text}")
                    # Remove wake word from text
                    command = audio_text.lower().replace(WAKE_WORD.lower(), '').strip()
                    await self.process(command, is_voice=True)
            except Exception as e:
                logger.error(f"❌ Voice listening error: {e}")
                await asyncio.sleep(1)
    
    async def process(self, user_input: str, is_voice: bool = False) -> str:
        """Process user input and generate response"""
        logger.info(f"🔄 Processing: {user_input[:100]}...")
        self._set_indicator("thinking")
        
        try:
            # Store in memory
            interaction_id = await self.memory_manager.store_interaction(
                user_input=user_input,
                is_voice=is_voice
            )
            
            # Get relevant context from memory
            context = await self.memory_manager.get_context()

            # Enrich with semantically-recalled long-term memories.
            recalled = self.semantic_memory.search(user_input, top_k=3)
            if recalled and isinstance(context, dict):
                context = dict(context)
                context["recalled_memories"] = [r["text"] for r in recalled]
            
            # Check if task requires execution
            if self._is_task_command(user_input):
                response = await self.task_executor.execute(
                    command=user_input,
                    context=context
                )
            else:
                # Use AI to generate response
                response = await self.api_manager.generate_response(
                    prompt=user_input,
                    context=context,
                    model_preference=self._select_model(user_input)
                )
            
            # Persist the exchange to semantic long-term memory.
            self.semantic_memory.add(
                f"User: {user_input}\n{self.name}: {response}",
                metadata={"is_voice": is_voice},
            )

            # Update mood based on interaction
            self.mood = await self._analyze_mood(user_input, response)
            
            # Store response in memory
            await self.memory_manager.store_interaction(
                user_input=user_input,
                response=response,
                interaction_id=interaction_id,
                mood=self.mood
            )
            
            # Output response
            if is_voice:
                self._set_indicator("speaking")
                await self.voice_processor.text_to_speech(response)
            
            logger.info(f"✅ Response generated (Mood: {self.mood})")
            return response
            
        except Exception as e:
            logger.error(f"❌ Processing error: {e}")
            error_response = f"I encountered an error: {str(e)}. Please try again."
            if is_voice:
                await self.voice_processor.text_to_speech(error_response)
            return error_response
        finally:
            self._set_indicator("active" if self.is_active else "idle")
    
    def _is_task_command(self, user_input: str) -> bool:
        """Determine if input requires task execution"""
        task_keywords = [
            'write', 'create', 'generate', 'code', 'execute',
            'run', 'file', 'open', 'search', 'download',
            'convert', 'analyze', 'process', 'calculate'
        ]
        return any(keyword in user_input.lower() for keyword in task_keywords)
    
    def _select_model(self, user_input: str) -> str:
        """Select optimal model based on input type"""
        code_keywords = ['code', 'function', 'script', 'program', 'write']
        if any(keyword in user_input.lower() for keyword in code_keywords):
            return 'gemini'  # Gemini better for code
        return 'groq'  # Groq better for general tasks
    
    async def _analyze_mood(self, user_input: str, response: str) -> str:
        """Analyze and update mood based on interaction"""
        mood_keywords = {
            'happy': ['great', 'awesome', 'love', 'perfect', '😊'],
            'curious': ['why', 'how', 'explain', 'tell me', 'what'],
            'urgent': ['fast', 'quickly', 'asap', 'emergency', 'critical'],
            'frustrated': ['error', 'not working', 'bug', 'fail', 'problem'],
            'neutral': []
        }
        
        combined_text = (user_input + ' ' + response).lower()
        
        for mood, keywords in mood_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                return mood
        
        return 'neutral'
    
    def stop_listening(self):
        """Stop voice listening"""
        logger.info("⏹️ Stopping voice listener")
        self.is_listening = False
    
    def activate(self):
        """Activate SAM"""
        logger.info(f"🟢 Activating {self.name}")
        self.is_active = True
        self._set_indicator("active")
    
    def deactivate(self):
        """Deactivate SAM"""
        logger.info(f"🔴 Deactivating {self.name}")
        self.is_active = False
        self.stop_listening()
        self._set_indicator("idle")
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info(f"🛑 Shutting down {self.name}...")
        self.deactivate()
        await self.memory_manager.save_history()
        logger.info("✅ Shutdown complete")
