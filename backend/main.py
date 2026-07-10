#!/usr/bin/env python3
"""
SAM - Agentic AI Assistant
Main entry point for the application
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.ai_engine import SAMEngine
from backend.config import LOG_LEVEL, SAM_NAME, LOG_FILE

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SAMApplication:
    """Main application class"""
    
    def __init__(self):
        logger.info(f"🚀 Starting {SAM_NAME} Application...")
        self.engine = SAMEngine()
        self.is_running = False
    
    async def start(self):
        """Start SAM application"""
        logger.info(f"⏰ {SAM_NAME} Starting...")
        
        try:
            # Initialize components
            await self.engine.initialize()
            
            # Activate engine
            self.engine.activate()
            self.is_running = True
            
            logger.info(f"✅ {SAM_NAME} Started Successfully!")
            logger.info(f"🎤 Listening for voice commands with wake word: 'Hey {SAM_NAME}'")
            logger.info("💬 You can also type commands directly")
            
            # Start listening
            await self._run_interactive_mode()
        
        except Exception as e:
            logger.error(f"❌ Failed to start {SAM_NAME}: {e}")
            await self.shutdown()
    
    async def _run_interactive_mode(self):
        """Run interactive mode with voice and text input"""
        logger.info("📱 Entering interactive mode...")
        
        # Start voice listener in background
        voice_task = asyncio.create_task(self.engine.listen())
        
        try:
            while self.is_running:
                # Get user input from console
                try:
                    user_input = await asyncio.get_event_loop().run_in_executor(
                        None,
                        input,
                        f"\n🎯 {SAM_NAME}> "
                    )
                    
                    if user_input.lower() in ['exit', 'quit', 'bye']:
                        logger.info("👋 Goodbye!")
                        self.is_running = False
                        break
                    
                    if user_input.strip():
                        response = await self.engine.process(user_input, is_voice=False)
                        logger.info(f"\n🤖 {SAM_NAME}: {response}\n")
                
                except EOFError:
                    # Handle non-interactive mode
                    await asyncio.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("\n⏸️ Keyboard interrupt received")
        
        finally:
            self.is_running = False
            voice_task.cancel()
    
    async def shutdown(self):
        """Shutdown SAM application"""
        logger.info(f"🛑 Shutting down {SAM_NAME}...")
        
        try:
            self.is_running = False
            await self.engine.shutdown()
            logger.info(f"✅ {SAM_NAME} shutdown complete")
        
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")


async def main():
    """Main entry point"""
    app = SAMApplication()
    
    try:
        await app.start()
    except KeyboardInterrupt:
        logger.info("\n⏸️ Keyboard interrupt")
    finally:
        await app.shutdown()


if __name__ == "__main__":
    print(f"""
    ╔═══════════════════════════════════════════════╗
    ║   🤖 SAM - Agentic AI Assistant 🤖           ║
    ║   Gemini + Groq Powered                       ║
    ║   Voice | Code | Tasks | Automation           ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())
