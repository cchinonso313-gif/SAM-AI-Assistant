import logging

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from backend.apis.base_handler import BaseAPIHandler
from backend.config import GEMINI_CONFIG

logger = logging.getLogger(__name__)

class GeminiHandler(BaseAPIHandler):
    """Handles Gemini API calls"""

    service_name = "Gemini"
    library_name = "Google Generative AI"
    query_emoji = "🧠"

    def __init__(self):
        super().__init__(GEMINI_CONFIG)
        self.model = None

    def is_available(self) -> bool:
        return GENAI_AVAILABLE

    def _setup_client(self) -> None:
        genai.configure(api_key=self.config['api_key'])
        self.model = genai.GenerativeModel(self.config['model'])

    def _generate_sync(self, prompt: str) -> str:
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=self.config['temperature'],
                max_output_tokens=self.config['max_tokens']
            )
        )
        return response.text
