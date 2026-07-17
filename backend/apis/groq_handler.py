import logging

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

from backend.apis.base_handler import BaseAPIHandler
from backend.config import GROQ_CONFIG

logger = logging.getLogger(__name__)

class GroqHandler(BaseAPIHandler):
    """Handles Groq API calls"""

    service_name = "Groq"
    library_name = "Groq"
    query_emoji = "⚡"

    def __init__(self):
        super().__init__(GROQ_CONFIG)
        self.client = None

    def is_available(self) -> bool:
        return GROQ_AVAILABLE

    def _setup_client(self) -> None:
        self.client = Groq(api_key=self.config['api_key'])

    def _generate_sync(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.config['model'],
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=self.config['temperature'],
            max_tokens=self.config['max_tokens']
        )
        return response.choices[0].message.content
