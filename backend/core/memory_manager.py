import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from backend.config import DATA_DIR, MAX_HISTORY_DAYS, ENCRYPTION_ENABLED

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages conversation history and learning"""
    
    def __init__(self):
        logger.info("🧠 Initializing Memory Manager...")
        
        self.history_file = DATA_DIR / 'conversation_history.json'
        self.context_file = DATA_DIR / 'context.json'
        self.learning_file = DATA_DIR / 'learning.json'
        
        self.history = []
        self.context = {}
        self.learning_data = {}
        
        logger.info("✅ Memory Manager initialized")
    
    async def load_history(self) -> List[Dict]:
        """Load conversation history from disk"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                
                self.history = data
                logger.info(f"✅ Loaded {len(self.history)} interactions from history")
            else:
                logger.info("📝 No existing history found")
                self.history = []
        
        except Exception as e:
            logger.error(f"❌ Error loading history: {e}")
            self.history = []
        
        return self.history
    
    async def save_history(self) -> bool:
        """Save conversation history to disk"""
        try:
            # Clean old entries
            await self._cleanup_old_history()
            
            data = self.history
            
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"✅ Saved {len(self.history)} interactions to history")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error saving history: {e}")
            return False
    
    async def store_interaction(
        self,
        user_input: str,
        response: str = None,
        interaction_id: str = None,
        mood: str = None,
        is_voice: bool = False
    ) -> str:
        """Store a user-AI interaction"""
        try:
            # Generate ID if not provided
            if not interaction_id:
                interaction_id = f"int_{datetime.now().timestamp()}"
            
            interaction = {
                'id': interaction_id,
                'timestamp': datetime.now().isoformat(),
                'user_input': user_input,
                'response': response,
                'mood': mood,
                'is_voice': is_voice
            }
            
            self.history.append(interaction)
            logger.info(f"💾 Stored interaction: {interaction_id}")
            
            # Auto-save periodically
            if len(self.history) % 10 == 0:
                await self.save_history()
            
            return interaction_id
        
        except Exception as e:
            logger.error(f"❌ Error storing interaction: {e}")
            return None
    
    async def get_context(self, limit: int = 5) -> Dict:
        """Get recent context for AI processing"""
        try:
            recent = self.history[-limit:] if self.history else []
            
            context = {
                'recent_interactions': recent,
                'total_interactions': len(self.history),
                'mood_history': self._get_mood_history(limit),
                'timestamp': datetime.now().isoformat()
            }
            
            return context
        
        except Exception as e:
            logger.error(f"❌ Error getting context: {e}")
            return {}
    
    def _get_mood_history(self, limit: int = 5) -> List[str]:
        """Get recent mood history"""
        moods = []
        for interaction in self.history[-limit:]:
            if interaction.get('mood'):
                moods.append(interaction['mood'])
        return moods
    
    async def _cleanup_old_history(self) -> int:
        """Remove entries older than MAX_HISTORY_DAYS"""
        try:
            cutoff_date = datetime.now() - timedelta(days=MAX_HISTORY_DAYS)
            original_len = len(self.history)
            
            self.history = [
                entry for entry in self.history
                if datetime.fromisoformat(entry['timestamp']) > cutoff_date
            ]
            
            removed = original_len - len(self.history)
            if removed > 0:
                logger.info(f"🗑️ Cleaned up {removed} old interactions")
            
            return removed
        
        except Exception as e:
            logger.error(f"❌ Error cleaning history: {e}")
            return 0
    
    def get_statistics(self) -> Dict:
        """Get memory usage statistics"""
        total_interactions = len(self.history)
        voice_interactions = sum(1 for i in self.history if i.get('is_voice'))
        
        return {
            'total_interactions': total_interactions,
            'voice_interactions': voice_interactions,
            'text_interactions': total_interactions - voice_interactions,
            'history_file_size': self.history_file.stat().st_size if self.history_file.exists() else 0
        }
