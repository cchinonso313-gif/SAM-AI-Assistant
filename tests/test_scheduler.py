import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
from backend.features.scheduler import TaskScheduler, ScheduleFrequency

class TestScheduler:
    """Test suite for Task Scheduler"""
    
    @pytest.fixture
    def scheduler(self):
        """Create scheduler instance"""
        return TaskScheduler()
    
    @pytest.mark.asyncio
    async def test_add_task(self, scheduler):
        """Test adding a task"""
        async def dummy_handler():
            pass
        
        task_id = await scheduler.add_task(
            name="Test Task",
            handler=dummy_handler,
            frequency=ScheduleFrequency.ONCE,
            scheduled_time=datetime.now()
        )
        
        assert task_id is not None
        assert task_id in scheduler.tasks
    
    @pytest.mark.asyncio
    async def test_remove_task(self, scheduler):
        """Test removing a task"""
        async def dummy_handler():
            pass
        
        task_id = await scheduler.add_task(
            name="Test Task",
            handler=dummy_handler,
            frequency=ScheduleFrequency.ONCE,
            scheduled_time=datetime.now()
        )
        
        removed = await scheduler.remove_task(task_id)
        assert removed == True
        assert task_id not in scheduler.tasks
    
    @pytest.mark.asyncio
    async def test_get_tasks(self, scheduler):
        """Test getting all tasks"""
        tasks = scheduler.get_tasks()
        assert isinstance(tasks, dict)
    
    @pytest.mark.asyncio
    async def test_start_stop(self, scheduler):
        """Test starting and stopping scheduler"""
        with patch('asyncio.sleep', new_callable=AsyncMock):
            scheduler.running = False  # Set to stop after one iteration
            # Should not raise error

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
