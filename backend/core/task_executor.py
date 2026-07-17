import asyncio
import logging
import subprocess
import os
from typing import Dict, Any, Optional
from backend.config import ALLOWED_COMMANDS, BLOCKED_KEYWORDS
from backend.utils import contains_any

logger = logging.getLogger(__name__)

class TaskExecutor:
    """Executes system tasks and commands safely"""
    
    def __init__(self):
        logger.info("🔧 Initializing Task Executor...")
        self.allowed_commands = ALLOWED_COMMANDS
        self.blocked_keywords = BLOCKED_KEYWORDS
        logger.info("✅ Task Executor initialized")
    
    async def execute(self, command: str, context: Dict[str, Any] = None) -> str:
        """Execute a task with safety checks"""
        logger.info(f"⚙️ Executing: {command[:100]}")
        
        # Safety checks
        if not self._is_safe(command):
            logger.warning(f"🚫 Blocked unsafe command: {command}")
            return "I cannot execute that command for security reasons."
        
        try:
            # Route to appropriate executor
            if 'code' in command.lower() or 'generate' in command.lower():
                return await self._execute_code_task(command)
            elif 'file' in command.lower():
                return await self._execute_file_task(command)
            elif 'system' in command.lower():
                return await self._execute_system_task(command)
            elif 'search' in command.lower():
                return await self._execute_search_task(command)
            else:
                return await self._execute_general_task(command)
        
        except Exception as e:
            logger.error(f"❌ Task execution error: {e}")
            return f"Error executing task: {str(e)}"
    
    def _is_safe(self, command: str) -> bool:
        """Check if command is safe to execute"""
        # Check for blocked keywords
        if contains_any(command, self.blocked_keywords):
            logger.warning("Blocked keyword detected")
            return False
        
        # Check for dangerous patterns
        dangerous_patterns = ['rm -rf', 'dd if=', 'format', 'fdisk']
        if contains_any(command, dangerous_patterns):
            logger.warning("Dangerous pattern detected")
            return False
        
        return True
    
    async def _execute_code_task(self, command: str) -> str:
        """Execute code generation/writing tasks"""
        logger.info("📝 Executing code task")
        return "Code generation task routed to AI engine."
    
    async def _execute_file_task(self, command: str) -> str:
        """Execute file operations"""
        logger.info("📁 Executing file task")
        return "File operation task - routed to AI engine."
    
    async def _execute_system_task(self, command: str) -> str:
        """Execute system-level tasks"""
        logger.info("🖥️ Executing system task")
        return "System task recognized - routed to AI engine."
    
    async def _execute_search_task(self, command: str) -> str:
        """Execute search operations"""
        logger.info("🔍 Executing search task")
        return "Search task - routed to AI engine."
    
    async def _execute_general_task(self, command: str) -> str:
        """Execute general tasks"""
        logger.info("📋 Executing general task")
        return f"Task recognized: {command}. Routed to AI engine."
