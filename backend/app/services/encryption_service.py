"""
Encryption service for database storage
"""

import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionService:
    """Service for encrypting/decrypting sensitive data in database"""

    def __init__(self):
        """Initialize encryption service"""
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)

    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key for database"""
        # In production, this should be stored securely (environment variable, key management service, etc.)
        key_source = os.getenv(
            "DB_ENCRYPTION_KEY",
            "crypto-trading-manager-default-key-change-in-production",
        )

        # Derive a proper Fernet key from the source
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"crypto_trading_salt",  # In production, use a random salt stored securely
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(key_source.encode()))
        return key

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string and return base64 encoded result"""
        if not plaintext:
            return ""

        encrypted_data = self.cipher.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt a base64 encoded encrypted string"""
        if not encrypted_data:
            return ""

        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {str(e)}")

    def is_encrypted(self, data: str) -> bool:
        """Check if data appears to be encrypted"""
        if not data:
            return False

        try:
            # Try to decode as base64 and decrypt
            decoded_data = base64.urlsafe_b64decode(data.encode())
            self.cipher.decrypt(decoded_data)
            return True
        except Exception:
            return False


# Global encryption service instance
_encryption_service = None


def get_encryption_service() -> EncryptionService:
    """Get global encryption service instance"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service
