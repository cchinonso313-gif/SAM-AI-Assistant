import pytest
from unittest.mock import patch, AsyncMock
from backend.core.task_executor import TaskExecutor

class TestTaskExecutor:
    """Test suite for Task Executor"""
    
    @pytest.fixture
    def executor(self):
        """Create task executor instance"""
        return TaskExecutor()
    
    def test_executor_initialization(self, executor):
        """Test executor initializes"""
        assert executor.allowed_commands is not None
        assert executor.blocked_keywords is not None
    
    def test_is_safe_blocked_keyword(self, executor):
        """Test safety check for blocked keywords"""
        assert executor._is_safe("write a malware script") == False
        assert executor._is_safe("exploit a vulnerability") == False
    
    def test_is_safe_dangerous_pattern(self, executor):
        """Test safety check for dangerous patterns"""
        assert executor._is_safe("rm -rf /") == False
        assert executor._is_safe("dd if=/dev/zero") == False
    
    def test_is_safe_normal_command(self, executor):
        """Test normal commands pass safety check"""
        assert executor._is_safe("write a python function") == True
        assert executor._is_safe("generate code") == True
    
    @pytest.mark.asyncio
    async def test_execute_blocked_command(self, executor):
        """Test executing blocked command"""
        response = await executor.execute("hack my system")
        assert "security" in response.lower()
    
    @pytest.mark.asyncio
    async def test_execute_code_task(self, executor):
        """Test executing code task"""
        response = await executor.execute("write a python function")
        assert response is not None
    
    @pytest.mark.asyncio
    async def test_execute_file_task(self, executor):
        """Test executing file task"""
        response = await executor.execute("create a new file")
        assert response is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
