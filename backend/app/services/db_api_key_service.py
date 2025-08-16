"""
Service for loading API keys from database for trading operations
"""

from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database_models import APIKey
from app.services.encryption_service import get_encryption_service


class DatabaseAPIKeyService:
    """Service for loading API keys from database"""

    def __init__(self, user_id: int = 1):
        """Initialize with user ID"""
        self.user_id = user_id
        self.encryption_service = get_encryption_service()

    def get_bitvavo_credentials(
        self, db: Session = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """Get Bitvavo API credentials from database"""
        if db is None:
            db = next(get_db())

        try:
            api_key_record = (
                db.query(APIKey)
                .filter(
                    APIKey.user_id == self.user_id,
                    APIKey.exchange == "bitvavo",
                    APIKey.is_active.is_(True),
                )
                .first()
            )

            if not api_key_record:
                return None, None

            # Decrypt the credentials
            api_key = self.encryption_service.decrypt(api_key_record.encrypted_api_key)
            api_secret = self.encryption_service.decrypt(
                api_key_record.encrypted_api_secret
            )

            return api_key, api_secret

        except Exception as e:
            print(f"Error loading Bitvavo credentials from database: {e}")
            return None, None
        finally:
            if db:
                db.close()

    def get_exchange_credentials(
        self, exchange: str, db: Session = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """Get API credentials for any exchange from database"""
        if db is None:
            db = next(get_db())

        try:
            api_key_record = (
                db.query(APIKey)
                .filter(
                    APIKey.user_id == self.user_id,
                    APIKey.exchange == exchange.lower(),
                    APIKey.is_active.is_(True),
                )
                .first()
            )

            if not api_key_record:
                return None, None

            # Decrypt the credentials
            api_key = self.encryption_service.decrypt(api_key_record.encrypted_api_key)
            api_secret = self.encryption_service.decrypt(
                api_key_record.encrypted_api_secret
            )

            return api_key, api_secret

        except Exception as e:
            print(f"Error loading {exchange} credentials from database: {e}")
            return None, None
        finally:
            if db:
                db.close()

    def has_credentials(self, exchange: str, db: Session = None) -> bool:
        """Check if user has credentials configured for an exchange"""
        api_key, api_secret = self.get_exchange_credentials(exchange, db)
        return bool(api_key and api_secret)


# Global service instance
_db_api_key_service = None


def get_db_api_key_service(user_id: int = 1) -> DatabaseAPIKeyService:
    """Get database API key service instance"""
    global _db_api_key_service
    if _db_api_key_service is None or _db_api_key_service.user_id != user_id:
        _db_api_key_service = DatabaseAPIKeyService(user_id)
    return _db_api_key_service
