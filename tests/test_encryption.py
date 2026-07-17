import builtins

import pytest

import backend.security.encryption as encryption_module
from backend.security.encryption import Encryption


class TestEncryption:
    """Test suite for the Encryption module"""

    @pytest.fixture
    def data_dir(self, tmp_path, monkeypatch):
        """Point the encryption module at a temporary data directory"""
        monkeypatch.setattr(encryption_module, "DATA_DIR", tmp_path)
        return tmp_path

    def test_initialization_creates_cipher(self, data_dir):
        """Encryption should build a cipher when cryptography is available"""
        enc = Encryption()
        assert enc.cipher is not None
        assert enc.key_file == data_dir / ".enc_key"

    def test_key_file_created_when_missing(self, data_dir):
        """A new key file should be generated on first use"""
        key_file = data_dir / ".enc_key"
        assert not key_file.exists()

        Encryption()

        assert key_file.exists()
        assert len(key_file.read_bytes()) > 0

    def test_existing_key_is_reused(self, data_dir):
        """A second instance should load the previously generated key"""
        first = Encryption()
        key_file = data_dir / ".enc_key"
        original_key = key_file.read_bytes()

        second = Encryption()

        assert key_file.read_bytes() == original_key
        assert first.cipher is not None
        assert second.cipher is not None

    def test_roundtrip_encrypt_decrypt(self, data_dir):
        """The generated cipher should encrypt and decrypt data losslessly"""
        enc = Encryption()
        token = enc.cipher.encrypt(b"secret message")

        assert token != b"secret message"
        assert enc.cipher.decrypt(token) == b"secret message"

    def test_cipher_none_when_crypto_unavailable(self, data_dir, monkeypatch):
        """No cipher should be created when the crypto library is missing"""
        monkeypatch.setattr(encryption_module, "CRYPTO_AVAILABLE", False)

        enc = Encryption()

        assert enc.cipher is None

    def test_load_or_create_key_handles_errors(self, data_dir, monkeypatch):
        """Key loading failures should be swallowed and return None"""
        def boom(*args, **kwargs):
            raise OSError("disk failure")

        monkeypatch.setattr(builtins, "open", boom)

        enc = Encryption()

        assert enc.cipher is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
