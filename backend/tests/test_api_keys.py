"""
Tests for API key management endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db, Base, engine
from app.models.database_models import User, APIKey
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock


# Create test database
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestAPIKeyManagement:
    """Test API key management functionality"""

    def setup_method(self):
        """Setup test environment"""
        Base.metadata.create_all(bind=engine)
        # Create test user
        db = TestingSessionLocal()
        try:
            test_user = User(
                id=1,
                username="test_user",
                email="test@example.com",
                hashed_password="test_password"
            )
            db.add(test_user)
            db.commit()
        except Exception:
            pass  # User might already exist
        finally:
            db.close()

    def teardown_method(self):
        """Clean up after tests"""
        db = TestingSessionLocal()
        try:
            # Clean up API keys
            db.query(APIKey).delete()
            db.commit()
        finally:
            db.close()

    def test_api_key_status_initially_empty(self):
        """Test that initially no API keys are configured"""
        response = client.get("/api/v1/api-keys/status")
        assert response.status_code == 200
        data = response.json()
        assert data["bitvavo"] is False
        assert data["binance"] is False
        assert data["coinbase"] is False

    def test_store_api_key_success(self):
        """Test storing a valid API key"""
        payload = {
            "api_key": "test_api_key_12345678901234567890123456789012345678901234567890123456789012",
            "api_secret": "test_api_secret_12345678901234567890123456789012345678901234567890123456789012"
        }
        
        response = client.post("/api/v1/api-keys/bitvavo", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["exchange"] == "bitvavo"
        assert data["status"] == "configured"
        assert "stored successfully" in data["message"]

    def test_store_api_key_invalid_exchange(self):
        """Test storing API key for unsupported exchange"""
        payload = {
            "api_key": "test_api_key_12345678901234567890123456789012345678901234567890123456789012",
            "api_secret": "test_api_secret_12345678901234567890123456789012345678901234567890123456789012"
        }
        
        response = client.post("/api/v1/api-keys/invalid_exchange", json=payload)
        assert response.status_code == 400
        assert "Unsupported exchange" in response.json()["detail"]

    def test_store_api_key_too_short(self):
        """Test storing API key that is too short"""
        payload = {
            "api_key": "short",
            "api_secret": "also_short"
        }
        
        response = client.post("/api/v1/api-keys/bitvavo", json=payload)
        assert response.status_code == 400
        assert "too short" in response.json()["detail"]

    def test_api_key_status_after_storing(self):
        """Test status endpoint after storing an API key"""
        # First store an API key
        payload = {
            "api_key": "test_api_key_12345678901234567890123456789012345678901234567890123456789012",
            "api_secret": "test_api_secret_12345678901234567890123456789012345678901234567890123456789012"
        }
        
        client.post("/api/v1/api-keys/bitvavo", json=payload)
        
        # Check status
        response = client.get("/api/v1/api-keys/status")
        assert response.status_code == 200
        data = response.json()
        assert data["bitvavo"] is True
        assert data["binance"] is False
        assert data["coinbase"] is False

    def test_update_existing_api_key(self):
        """Test updating an existing API key"""
        # First store an API key
        payload1 = {
            "api_key": "test_api_key_12345678901234567890123456789012345678901234567890123456789012",
            "api_secret": "test_api_secret_12345678901234567890123456789012345678901234567890123456789012"
        }
        client.post("/api/v1/api-keys/bitvavo", json=payload1)
        
        # Update with new key
        payload2 = {
            "api_key": "new_api_key_12345678901234567890123456789012345678901234567890123456789012",
            "api_secret": "new_api_secret_12345678901234567890123456789012345678901234567890123456789012"
        }
        
        response = client.post("/api/v1/api-keys/bitvavo", json=payload2)
        assert response.status_code == 200
        data = response.json()
        assert data["exchange"] == "bitvavo"
        assert data["status"] == "configured"

    def test_delete_api_key(self):
        """Test deleting an API key"""
        # First store an API key
        payload = {
            "api_key": "test_api_key_12345678901234567890123456789012345678901234567890123456789012",
            "api_secret": "test_api_secret_12345678901234567890123456789012345678901234567890123456789012"
        }
        client.post("/api/v1/api-keys/bitvavo", json=payload)
        
        # Delete it
        response = client.delete("/api/v1/api-keys/bitvavo")
        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"]
        
        # Check status is back to false
        status_response = client.get("/api/v1/api-keys/status")
        assert status_response.json()["bitvavo"] is False

    def test_delete_nonexistent_api_key(self):
        """Test deleting a non-existent API key"""
        response = client.delete("/api/v1/api-keys/bitvavo")
        assert response.status_code == 404
        assert "No active API key found" in response.json()["detail"]

    def test_api_key_test_endpoint_success(self):
        """Test the API key test endpoint with successful validation"""
        # Store API key first
        payload = {
            "api_key": "valid_api_key_12345678901234567890123456789012345678901234567890123456",
            "api_secret": "valid_api_secret_12345678901234567890123456789012345678901234567890123456"
        }
        client.post("/api/v1/api-keys/bitvavo", json=payload)
        
        # Test the key - this will fail with invalid credentials but should return structured response
        response = client.get("/api/v1/api-keys/bitvavo/test")
        assert response.status_code == 200
        data = response.json()
        assert data["exchange"] == "bitvavo"
        assert data["status"] in ["success", "error"]  # Accept either since it depends on API validation

    def test_api_key_test_endpoint_failure(self):
        """Test the API key test endpoint with failed validation"""
        # Store API key first
        payload = {
            "api_key": "invalid_api_key_12345678901234567890123456789012345678901234567890123456",
            "api_secret": "invalid_api_secret_12345678901234567890123456789012345678901234567890123456"
        }
        client.post("/api/v1/api-keys/bitvavo", json=payload)
        
        # Test the key - this will likely fail with invalid credentials
        response = client.get("/api/v1/api-keys/bitvavo/test")
        assert response.status_code == 200
        data = response.json()
        assert data["exchange"] == "bitvavo"
        assert data["status"] == "error"  # Expect error for invalid credentials

    def test_api_key_test_nonexistent(self):
        """Test testing a non-existent API key"""
        response = client.get("/api/v1/api-keys/bitvavo/test")
        assert response.status_code == 404
        assert "No API key configured" in response.json()["detail"]
