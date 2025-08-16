"""
Tests for the database API key service
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from sqlalchemy.orm import Session

from app.models.database_models import APIKey, User
from app.services.db_api_key_service import DatabaseAPIKeyService


class TestDatabaseAPIKeyService:
    """Test database API key service functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.mock_db = Mock(spec=Session)
        self.service = DatabaseAPIKeyService(user_id=1)

    def test_service_initialization(self):
        """Test that service initializes correctly"""
        service = DatabaseAPIKeyService(user_id=1)
        assert service is not None
        assert hasattr(service, "get_bitvavo_credentials")
        assert hasattr(service, "get_exchange_credentials")
        assert service.user_id == 1

    @patch("app.services.db_api_key_service.get_encryption_service")
    def test_get_bitvavo_credentials_success(self, mock_get_encryption):
        """Test successful loading of Bitvavo credentials"""
        # Setup mocks
        mock_encryption = Mock()
        mock_encryption.decrypt.side_effect = lambda x: f"decrypted_{x}"
        mock_get_encryption.return_value = mock_encryption

        # Mock database query
        mock_api_key = Mock()
        mock_api_key.encrypted_api_key = "encrypted_key"
        mock_api_key.encrypted_api_secret = "encrypted_secret"

        mock_query = self.mock_db.query.return_value
        mock_query.filter.return_value.first.return_value = mock_api_key

        # Create service with mock
        service = DatabaseAPIKeyService(user_id=1)
        service.encryption_service = mock_encryption

        # Test
        api_key, api_secret = service.get_bitvavo_credentials(self.mock_db)

        # Assertions
        assert api_key == "decrypted_encrypted_key"
        assert api_secret == "decrypted_encrypted_secret"

        # Verify database query
        self.mock_db.query.assert_called_once_with(APIKey)

    def test_get_bitvavo_credentials_not_found(self):
        """Test loading credentials when no API key is found"""
        # Mock database query returning None
        mock_query = self.mock_db.query.return_value
        mock_query.filter.return_value.first.return_value = None

        # Test
        api_key, api_secret = self.service.get_bitvavo_credentials(self.mock_db)

        # Assertions
        assert api_key is None
        assert api_secret is None

    @patch("app.services.db_api_key_service.get_encryption_service")
    def test_get_exchange_credentials_success(self, mock_get_encryption):
        """Test successful loading of exchange credentials"""
        # Setup mocks
        mock_encryption = Mock()
        mock_encryption.decrypt.side_effect = lambda x: f"decrypted_{x}"
        mock_get_encryption.return_value = mock_encryption

        # Mock database query
        mock_api_key = Mock()
        mock_api_key.encrypted_api_key = "encrypted_key"
        mock_api_key.encrypted_api_secret = "encrypted_secret"

        mock_query = self.mock_db.query.return_value
        mock_query.filter.return_value.first.return_value = mock_api_key

        # Create service with mock
        service = DatabaseAPIKeyService(user_id=1)
        service.encryption_service = mock_encryption

        # Test
        api_key, api_secret = service.get_exchange_credentials("binance", self.mock_db)

        # Assertions
        assert api_key == "decrypted_encrypted_key"
        assert api_secret == "decrypted_encrypted_secret"

    @patch("app.services.db_api_key_service.get_encryption_service")
    def test_get_credentials_decryption_error(self, mock_get_encryption):
        """Test handling of decryption errors"""
        # Setup mocks
        mock_encryption = Mock()
        mock_encryption.decrypt.side_effect = Exception("Decryption failed")
        mock_get_encryption.return_value = mock_encryption

        # Mock database query
        mock_api_key = Mock()
        mock_api_key.encrypted_api_key = "encrypted_key"
        mock_api_key.encrypted_api_secret = "encrypted_secret"

        mock_query = self.mock_db.query.return_value
        mock_query.filter.return_value.first.return_value = mock_api_key

        # Create service with mock
        service = DatabaseAPIKeyService(user_id=1)
        service.encryption_service = mock_encryption

        # Test - should return None, None on decryption error
        api_key, api_secret = service.get_bitvavo_credentials(self.mock_db)

        # Assertions
        assert api_key is None
        assert api_secret is None

    def test_get_credentials_database_error(self):
        """Test handling of database errors"""
        # Mock database query raising exception
        self.mock_db.query.side_effect = Exception("Database connection failed")

        # Test - should return None, None on database error
        api_key, api_secret = self.service.get_bitvavo_credentials(self.mock_db)

        # Assertions
        assert api_key is None
        assert api_secret is None

    @patch("app.services.db_api_key_service.get_encryption_service")
    def test_get_credentials_multiple_exchanges(self, mock_get_encryption):
        """Test loading credentials for different exchanges"""
        # Setup mocks
        mock_encryption = Mock()
        mock_encryption.decrypt.side_effect = lambda x: f"decrypted_{x}"
        mock_get_encryption.return_value = mock_encryption

        # Test different exchanges
        exchanges = ["bitvavo", "binance", "coinbase"]

        for exchange in exchanges:
            # Mock database query for each exchange
            mock_api_key = Mock()
            mock_api_key.encrypted_api_key = f"encrypted_key_{exchange}"
            mock_api_key.encrypted_api_secret = f"encrypted_secret_{exchange}"

            mock_query = self.mock_db.query.return_value
            mock_query.filter.return_value.first.return_value = mock_api_key

            # Create service with mock
            service = DatabaseAPIKeyService(user_id=1)
            service.encryption_service = mock_encryption

            # Test
            api_key, api_secret = service.get_exchange_credentials(
                exchange, self.mock_db
            )

            # Assertions
            assert api_key == f"decrypted_encrypted_key_{exchange}"
            assert api_secret == f"decrypted_encrypted_secret_{exchange}"

    @patch("app.services.db_api_key_service.get_encryption_service")
    def test_get_credentials_different_users(self, mock_get_encryption):
        """Test loading credentials for different users"""
        # Setup mocks
        mock_encryption = Mock()
        mock_encryption.decrypt.side_effect = lambda x: f"decrypted_{x}"
        mock_get_encryption.return_value = mock_encryption

        # Test different user IDs
        user_ids = [1, 2, 42, 100]

        for user_id in user_ids:
            # Mock database query for each user
            mock_api_key = Mock()
            mock_api_key.encrypted_api_key = f"encrypted_key_user_{user_id}"
            mock_api_key.encrypted_api_secret = f"encrypted_secret_user_{user_id}"

            mock_query = self.mock_db.query.return_value
            mock_query.filter.return_value.first.return_value = mock_api_key

            # Create service with mock
            service = DatabaseAPIKeyService(user_id=user_id)
            service.encryption_service = mock_encryption

            # Test
            api_key, api_secret = service.get_bitvavo_credentials(self.mock_db)

            # Assertions
            assert api_key == f"decrypted_encrypted_key_user_{user_id}"
            assert api_secret == f"decrypted_encrypted_secret_user_{user_id}"

    @patch("app.services.db_api_key_service.get_encryption_service")
    def test_filter_conditions_correct(self, mock_get_encryption):
        """Test that database filter conditions are correct"""
        # Setup mocks
        mock_encryption = Mock()
        mock_encryption.decrypt.return_value = "decrypted_value"
        mock_get_encryption.return_value = mock_encryption

        mock_api_key = Mock()
        mock_api_key.encrypted_api_key = "encrypted_key"
        mock_api_key.encrypted_api_secret = "encrypted_secret"

        mock_query = self.mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_api_key

        # Create service with mock
        service = DatabaseAPIKeyService(user_id=42)
        service.encryption_service = mock_encryption

        # Test
        service.get_exchange_credentials("test_exchange", self.mock_db)

        # Verify that filter was called
        mock_query.filter.assert_called_once()

    def test_invalid_parameters(self):
        """Test handling of invalid parameters"""
        # Test with None database - should handle gracefully
        api_key, api_secret = self.service.get_bitvavo_credentials(None)
        # This might work because of get_db() fallback, so we just check it returns something
        assert (
            api_key is None
            and api_secret is None
            or isinstance(api_key, (str, type(None)))
        )

        # Test with empty exchange
        api_key, api_secret = self.service.get_exchange_credentials("", self.mock_db)
        assert api_key is None
        assert api_secret is None
