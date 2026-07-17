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
from backend.config import LOG_LEVEL, SAM_NAME, LOG_FILE, INDICATOR_ENABLED

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
        self.indicator = None
        self.is_running = False

    def _setup_indicator(self):
        """Attach the glowing desktop indicator if enabled and available."""
        if not INDICATOR_ENABLED:
            return
        try:
            from desktop.ui_indicator import DesktopIndicator

            self.indicator = DesktopIndicator()
            self.engine.indicator = self.indicator
            self.indicator.show()
            self.indicator.set_state("active")
        except Exception as e:  # noqa: BLE001 - UI is optional
            logger.warning(f"⚠️ Desktop indicator unavailable: {e}")

    async def _pump_indicator(self):
        """Keep the Qt indicator animating alongside the asyncio loop."""
        if self.indicator is None:
            return
        while self.is_running:
            self.indicator.process_events()
            await asyncio.sleep(0.05)
    
    async def start(self):
        """Start SAM application"""
        logger.info(f"⏰ {SAM_NAME} Starting...")
        
        try:
            # Initialize components
            await self.engine.initialize()

            # Set up the visual indicator
            self._setup_indicator()
            
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
        pump_task = asyncio.create_task(self._pump_indicator())
        
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
            pump_task.cancel()
    
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
