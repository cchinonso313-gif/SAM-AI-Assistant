import asyncio
import logging
from typing import Dict

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)

class SystemMonitor:
    """Monitor system resources"""
    
    def __init__(self):
        logger.info("📊 Initializing System Monitor...")
        self.monitoring = False
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not installed - system monitoring disabled")
        logger.info("✅ System Monitor initialized")
    
    async def get_system_stats(self) -> Dict:
        """Get current system statistics"""
        if not PSUTIL_AVAILABLE:
            return {}
        
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'temperature': self._get_temperature(),
                'processes': len(psutil.pids())
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def _get_temperature(self) -> float:
        """Get CPU temperature if available"""
        if not PSUTIL_AVAILABLE:
            return 0.0
        
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                return list(temps.values())[0][0].current
        except:
            pass
        return 0.0
    
    async def monitor_continuously(self, interval: int = 5):
        """Monitor system continuously"""
        self.monitoring = True
        logger.info(f"📊 Starting continuous monitoring (interval: {interval}s)")
        
        while self.monitoring:
            stats = await self.get_system_stats()
            logger.debug(f"System stats: {stats}")
            await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        logger.info("📊 Stopped monitoring")
