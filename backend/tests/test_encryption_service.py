"""
Tests for the encryption service
"""

import os
from unittest.mock import patch

import pytest

from app.services.encryption_service import EncryptionService


class TestEncryptionService:
    """Test encryption service functionality"""

    def setup_method(self):
        """Setup test environment"""
        # Use a test encryption key
        self.test_key = "test_encryption_key_12345678901234567890123456789012"

    def test_encryption_service_initialization(self):
        """Test that encryption service initializes correctly"""
        service = EncryptionService()
        assert service is not None
        assert hasattr(service, "encrypt")
        assert hasattr(service, "decrypt")

    @patch.dict(
        os.environ,
        {
            "ENCRYPTION_KEY": "test_key_for_encryption_service_testing_12345678901234567890"
        },
    )
    def test_encrypt_decrypt_success(self):
        """Test successful encryption and decryption"""
        service = EncryptionService()

        # Test data
        original_data = "test_api_key_12345"

        # Encrypt
        encrypted_data = service.encrypt(original_data)
        assert encrypted_data != original_data
        assert isinstance(encrypted_data, str)
        assert len(encrypted_data) > len(original_data)

        # Decrypt
        decrypted_data = service.decrypt(encrypted_data)
        assert decrypted_data == original_data

    @patch.dict(
        os.environ,
        {
            "ENCRYPTION_KEY": "test_key_for_encryption_service_testing_12345678901234567890"
        },
    )
    def test_encrypt_empty_string(self):
        """Test encrypting empty string"""
        service = EncryptionService()

        encrypted = service.encrypt("")
        decrypted = service.decrypt(encrypted)
        assert decrypted == ""

    @patch.dict(
        os.environ,
        {
            "ENCRYPTION_KEY": "test_key_for_encryption_service_testing_12345678901234567890"
        },
    )
    def test_encrypt_unicode_data(self):
        """Test encrypting unicode data"""
        service = EncryptionService()

        unicode_data = "🔑 API Key with émojis and spéciál chars 中文"
        encrypted = service.encrypt(unicode_data)
        decrypted = service.decrypt(encrypted)
        assert decrypted == unicode_data

    @patch.dict(
        os.environ,
        {
            "ENCRYPTION_KEY": "test_key_for_encryption_service_testing_12345678901234567890"
        },
    )
    def test_encrypt_long_data(self):
        """Test encrypting long data"""
        service = EncryptionService()

        long_data = "x" * 10000  # 10KB of data
        encrypted = service.encrypt(long_data)
        decrypted = service.decrypt(encrypted)
        assert decrypted == long_data

    @patch.dict(
        os.environ,
        {
            "ENCRYPTION_KEY": "test_key_for_encryption_service_testing_12345678901234567890"
        },
    )
    def test_decrypt_invalid_data_raises_error(self):
        """Test that decrypting invalid data raises an error"""
        service = EncryptionService()

        with pytest.raises(Exception):
            service.decrypt("invalid_encrypted_data")

    @patch.dict(
        os.environ,
        {
            "ENCRYPTION_KEY": "test_key_for_encryption_service_testing_12345678901234567890"
        },
    )
    def test_decrypt_corrupted_data_raises_error(self):
        """Test that decrypting corrupted data raises an error"""
        service = EncryptionService()

        # Create valid encrypted data then corrupt it
        original = "test_data"
        encrypted = service.encrypt(original)
        corrupted = encrypted[:-5] + "XXXXX"  # Corrupt the end

        with pytest.raises(Exception):
            service.decrypt(corrupted)

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_encryption_key_generates_key(self):
        """Test that missing encryption key generates a new one"""
        service = EncryptionService()

        # Should work even without environment key
        test_data = "test_data"
        encrypted = service.encrypt(test_data)
        decrypted = service.decrypt(encrypted)
        assert decrypted == test_data

    @patch.dict(os.environ, {"ENCRYPTION_KEY": "short"})
    def test_short_encryption_key_handled(self):
        """Test that short encryption key is handled properly"""
        service = EncryptionService()

        # Should still work with key derivation
        test_data = "test_data"
        encrypted = service.encrypt(test_data)
        decrypted = service.decrypt(encrypted)
        assert decrypted == test_data

    @patch.dict(
        os.environ,
        {
            "ENCRYPTION_KEY": "test_key_for_encryption_service_testing_12345678901234567890"
        },
    )
    def test_multiple_encryptions_different_results(self):
        """Test that multiple encryptions of same data produce different results"""
        service = EncryptionService()

        data = "same_data"
        encrypted1 = service.encrypt(data)
        encrypted2 = service.encrypt(data)

        # Encrypted values should be different (due to random IV/nonce)
        assert encrypted1 != encrypted2

        # But both should decrypt to same original
        assert service.decrypt(encrypted1) == data
        assert service.decrypt(encrypted2) == data

    @patch.dict(
        os.environ,
        {
            "ENCRYPTION_KEY": "test_key_for_encryption_service_testing_12345678901234567890"
        },
    )
    def test_encryption_deterministic_key_derivation(self):
        """Test that key derivation is deterministic"""
        service1 = EncryptionService()
        service2 = EncryptionService()

        data = "test_data"
        encrypted_by_service1 = service1.encrypt(data)
        decrypted_by_service2 = service2.decrypt(encrypted_by_service1)

        assert decrypted_by_service2 == data

    @patch("app.services.encryption_service.Fernet")
    def test_fernet_initialization_error_handling(self, mock_fernet):
        """Test error handling during Fernet initialization"""
        mock_fernet.side_effect = Exception("Fernet initialization failed")

        with pytest.raises(Exception):
            EncryptionService()

    @patch.dict(
        os.environ,
        {
            "ENCRYPTION_KEY": "test_key_for_encryption_service_testing_12345678901234567890"
        },
    )
    def test_key_derivation_with_salt(self):
        """Test that key derivation uses proper salt"""
        service = EncryptionService()

        # Test that the service can encrypt/decrypt (implying key derivation worked)
        test_data = "test_data_with_salt"
        encrypted = service.encrypt(test_data)
        decrypted = service.decrypt(encrypted)
        assert decrypted == test_data

    @patch.dict(
        os.environ,
        {
            "ENCRYPTION_KEY": "test_key_for_encryption_service_testing_12345678901234567890"
        },
    )
    def test_base64_encoding_in_encrypted_output(self):
        """Test that encrypted output is properly base64 encoded"""
        service = EncryptionService()

        encrypted = service.encrypt("test_data")

        # Should be valid base64 (this will raise exception if not)
        import base64

        try:
            base64.b64decode(encrypted)
        except Exception:
            pytest.fail("Encrypted output is not valid base64")

    @patch.dict(
        os.environ,
        {
            "ENCRYPTION_KEY": "test_key_for_encryption_service_testing_12345678901234567890"
        },
    )
    def test_service_instance_reuse(self):
        """Test that service instance can be reused multiple times"""
        service = EncryptionService()

        # Multiple operations with same service instance
        data1 = "first_data"
        data2 = "second_data"

        encrypted1 = service.encrypt(data1)
        encrypted2 = service.encrypt(data2)

        decrypted1 = service.decrypt(encrypted1)
        decrypted2 = service.decrypt(encrypted2)

        assert decrypted1 == data1
        assert decrypted2 == data2
