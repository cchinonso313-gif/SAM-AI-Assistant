import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Callable, Optional
from enum import Enum

from backend.utils import generate_id

logger = logging.getLogger(__name__)

class ScheduleFrequency(Enum):
    """Schedule frequency options"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class Task:
    """Scheduled task"""
    
    def __init__(
        self,
        task_id: str,
        name: str,
        handler: Callable,
        frequency: ScheduleFrequency,
        scheduled_time: datetime,
        arguments: Dict = None
    ):
        self.task_id = task_id
        self.name = name
        self.handler = handler
        self.frequency = frequency
        self.scheduled_time = scheduled_time
        self.arguments = arguments or {}
        self.last_executed = None
        self.next_execution = scheduled_time
        self.is_active = True
    
    async def execute(self) -> bool:
        """Execute the task"""
        try:
            logger.info(f"⏱️ Executing task: {self.name}")
            await self.handler(**self.arguments)
            self.last_executed = datetime.now()
            self._calculate_next_execution()
            logger.info(f"✅ Task completed: {self.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Task failed: {self.name} - {e}")
            return False
    
    def _calculate_next_execution(self):
        """Calculate next execution time"""
        if self.frequency == ScheduleFrequency.ONCE:
            self.is_active = False
        elif self.frequency == ScheduleFrequency.DAILY:
            self.next_execution = self.next_execution + timedelta(days=1)
        elif self.frequency == ScheduleFrequency.WEEKLY:
            self.next_execution = self.next_execution + timedelta(weeks=1)
        elif self.frequency == ScheduleFrequency.MONTHLY:
            self.next_execution = self.next_execution + timedelta(days=30)

class TaskScheduler:
    """Manages scheduled tasks"""
    
    def __init__(self):
        logger.info("📅 Initializing Task Scheduler...")
        self.tasks: Dict[str, Task] = {}
        self.running = False
        logger.info("✅ Task Scheduler initialized")
    
    async def add_task(
        self,
        name: str,
        handler: Callable,
        frequency: ScheduleFrequency,
        scheduled_time: datetime,
        arguments: Dict = None
    ) -> str:
        """Add a new scheduled task"""
        task_id = generate_id("task")
        task = Task(
            task_id=task_id,
            name=name,
            handler=handler,
            frequency=frequency,
            scheduled_time=scheduled_time,
            arguments=arguments
        )
        self.tasks[task_id] = task
        logger.info(f"📌 Task scheduled: {name} (ID: {task_id})")
        return task_id
    
    async def remove_task(self, task_id: str) -> bool:
        """Remove a scheduled task"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.info(f"🗑️ Task removed: {task_id}")
            return True
        return False
    
    async def start(self):
        """Start the scheduler"""
        logger.info("▶️ Starting Task Scheduler")
        self.running = True
        
        while self.running:
            try:
                now = datetime.now()
                for task in self.tasks.values():
                    if task.is_active and task.next_execution <= now:
                        await task.execute()
                
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                await asyncio.sleep(60)
    
    async def stop(self):
        """Stop the scheduler"""
        logger.info("⏹️ Stopping Task Scheduler")
        self.running = False
    
    def get_tasks(self) -> Dict:
        """Get all tasks"""
        return {
            task_id: {
                'name': task.name,
                'frequency': task.frequency.value,
                'next_execution': task.next_execution.isoformat(),
                'last_executed': task.last_executed.isoformat() if task.last_executed else None,
                'is_active': task.is_active
            }
            for task_id, task in self.tasks.items()
        }

if __name__ == "__main__":
    scheduler = TaskScheduler()
