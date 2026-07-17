import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / 'backend'
DESKTOP_DIR = BASE_DIR / 'desktop'
LOGS_DIR = BASE_DIR / 'logs'
DATA_DIR = BASE_DIR / 'data'
CACHE_DIR = DATA_DIR / 'cache'

# Create directories
for directory in [LOGS_DIR, DATA_DIR, CACHE_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

# API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

GEMINI_CONFIG = {
    'api_key': GEMINI_API_KEY,
    'model': 'gemini-2.0-flash',
    'temperature': 0.7,
    'max_tokens': 2048,
    'timeout': 30
}

GROQ_CONFIG = {
    'api_key': GROQ_API_KEY,
    'model': 'mixtral-8x7b-32768',
    'temperature': 0.7,
    'max_tokens': 2048,
    'timeout': 30
}

# System Settings
SAM_NAME = os.getenv('SAM_NAME', 'SAM')
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gemini')
FALLBACK_MODEL = os.getenv('FALLBACK_MODEL', 'groq')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Voice Configuration
VOICE_ENABLED = os.getenv('VOICE_ENABLED', 'True').lower() == 'true'
MIC_INDEX = int(os.getenv('MIC_INDEX', 0))
TTS_ENGINE = os.getenv('TTS_ENGINE', 'pyttsx3')
VOICE_RATE = int(os.getenv('VOICE_RATE', 150))
VOICE_VOLUME = float(os.getenv('VOICE_VOLUME', 0.9))
WAKE_WORD = f'hey {SAM_NAME.lower()}'

# Desktop UI Configuration
INDICATOR_ENABLED = os.getenv('INDICATOR_ENABLED', 'True').lower() == 'true'
INDICATOR_SIZE = int(os.getenv('INDICATOR_SIZE', 50))
INDICATOR_COLOR = os.getenv('INDICATOR_COLOR', '#00FF00')
INDICATOR_BLINK_RATE = 500  # milliseconds

# Security
ENCRYPTION_ENABLED = os.getenv('ENCRYPTION_ENABLED', 'True').lower() == 'true'
MAX_HISTORY_DAYS = int(os.getenv('MAX_HISTORY_DAYS', 30))
AUTO_CLEAR_CACHE = os.getenv('AUTO_CLEAR_CACHE', 'True').lower() == 'true'

# Web Dashboard
DASHBOARD_HOST = os.getenv('DASHBOARD_HOST', '127.0.0.1')
DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', 8000))
# Token required to access the dashboard API/WebSocket. If unset, a random
# token is generated at runtime so the dashboard is never left unauthenticated.
DASHBOARD_TOKEN = os.getenv('DASHBOARD_TOKEN')

# Task Execution
ALLOWED_COMMANDS = [
    'code',
    'execute',
    'file',
    'system',
    'search',
    'analyze',
    'generate',
    'convert',
    'summarize',
    'translate'
]

BLOCKED_KEYWORDS = [
    'hack',
    'crack',
    'exploit',
    'malware',
    'virus',
    'ransomware'
]

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = LOGS_DIR / 'sam.log'

print("✅ Configuration loaded successfully")
