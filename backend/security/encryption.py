import logging

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

from backend.config import DATA_DIR

logger = logging.getLogger(__name__)

class Encryption:
    """Handles data encryption and decryption"""
    
    def __init__(self):
        logger.info("🔐 Initializing Encryption...")
        if not CRYPTO_AVAILABLE:
            logger.warning("Cryptography library not installed")
            self.cipher = None
        else:
            self.key_file = DATA_DIR / '.enc_key'
            self.cipher = self._load_or_create_key()
        logger.info("✅ Encryption ready")
    
    def _load_or_create_key(self):
        """Load or create encryption key"""
        try:
            if self.key_file.exists():
                with open(self.key_file, 'rb') as f:
                    key = f.read()
            else:
                key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(key)
            
            return Fernet(key)
        
        except Exception as e:
            logger.error(f"Encryption key error: {e}")
            return None
