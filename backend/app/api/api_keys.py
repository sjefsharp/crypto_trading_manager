"""
API endpoints for managing user API keys
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel

from app.core.database import get_db
from app.models.database_models import APIKey, User
from app.services.encryption_service import EncryptionService

router = APIRouter()

class APIKeyRequest(BaseModel):
    api_key: str
    api_secret: str

class APIKeyResponse(BaseModel):
    exchange: str
    is_configured: bool
    created_at: str = None
    last_used: str = None

class APIKeyStatus(BaseModel):
    bitvavo: bool = False
    binance: bool = False
    coinbase: bool = False

# For now, we'll use a simple user ID. In a real app, this would come from authentication
CURRENT_USER_ID = 1

def get_current_user_id() -> int:
    """Get current user ID. In a real app, this would come from JWT token"""
    return CURRENT_USER_ID

@router.post("/api-keys/{exchange}", response_model=Dict[str, Any])
async def store_api_key(
    exchange: str,
    request: APIKeyRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Store encrypted API key for a specific exchange"""
    try:
        # Validate exchange
        supported_exchanges = ["bitvavo", "binance", "coinbase"]
        if exchange.lower() not in supported_exchanges:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported exchange. Supported: {supported_exchanges}"
            )
        
        # Validate API credentials format (basic validation)
        if not request.api_key or not request.api_secret:
            raise HTTPException(
                status_code=400,
                detail="Both API key and secret are required"
            )
        
        if len(request.api_key) < 10 or len(request.api_secret) < 10:
            raise HTTPException(
                status_code=400,
                detail="API key and secret seem too short"
            )
        
        # Ensure user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            # Create default user for demo
            user = User(
                username=f"user_{user_id}",
                email=f"user_{user_id}@example.com",
                hashed_password="demo_password"  # In real app, this would be properly hashed
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Initialize encryption service
        encryption_service = EncryptionService()
        
        # Check if API key already exists for this user and exchange
        existing_key = db.query(APIKey).filter(
            APIKey.user_id == user_id,
            APIKey.exchange == exchange.lower()
        ).first()
        
        if existing_key:
            # Update existing key
            existing_key.encrypted_api_key = encryption_service.encrypt(request.api_key)
            existing_key.encrypted_api_secret = encryption_service.encrypt(request.api_secret)
            existing_key.is_active = True
        else:
            # Create new API key entry
            new_api_key = APIKey(
                user_id=user_id,
                exchange=exchange.lower(),
                encrypted_api_key=encryption_service.encrypt(request.api_key),
                encrypted_api_secret=encryption_service.encrypt(request.api_secret),
                is_active=True
            )
            db.add(new_api_key)
        
        db.commit()
        
        return {
            "message": f"API key for {exchange} stored successfully",
            "exchange": exchange.lower(),
            "status": "configured"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error storing API key: {str(e)}"
        )

@router.get("/api-keys/status", response_model=APIKeyStatus)
async def get_api_keys_status(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get status of configured API keys for current user"""
    try:
        api_keys = db.query(APIKey).filter(
            APIKey.user_id == user_id,
            APIKey.is_active == True
        ).all()
        
        status = APIKeyStatus()
        for key in api_keys:
            if key.exchange == "bitvavo":
                status.bitvavo = True
            elif key.exchange == "binance":
                status.binance = True
            elif key.exchange == "coinbase":
                status.coinbase = True
        
        return status
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving API key status: {str(e)}"
        )

@router.delete("/api-keys/{exchange}")
async def delete_api_key(
    exchange: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Delete API key for a specific exchange"""
    try:
        api_key = db.query(APIKey).filter(
            APIKey.user_id == user_id,
            APIKey.exchange == exchange.lower(),
            APIKey.is_active == True
        ).first()
        
        if not api_key:
            raise HTTPException(
                status_code=404,
                detail=f"No active API key found for {exchange}"
            )
        
        # Soft delete - just mark as inactive
        api_key.is_active = False
        db.commit()
        
        return {
            "message": f"API key for {exchange} deleted successfully",
            "exchange": exchange.lower(),
            "status": "deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting API key: {str(e)}"
        )

@router.get("/api-keys/{exchange}/test")
async def test_api_key(
    exchange: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Test if stored API key works for a specific exchange"""
    try:
        # Get the API key
        api_key_record = db.query(APIKey).filter(
            APIKey.user_id == user_id,
            APIKey.exchange == exchange.lower(),
            APIKey.is_active == True
        ).first()
        
        if not api_key_record:
            raise HTTPException(
                status_code=404,
                detail=f"No API key configured for {exchange}"
            )
        
        # Decrypt the credentials
        encryption_service = EncryptionService()
        api_key = encryption_service.decrypt(api_key_record.encrypted_api_key)
        api_secret = encryption_service.decrypt(api_key_record.encrypted_api_secret)
        
        # Test the connection based on exchange
        if exchange.lower() == "bitvavo":
            from app.services.bitvavo_api_secure import BitvavoAPI
            
            # Test connection
            async with BitvavoAPI(api_key=api_key, api_secret=api_secret) as api:
                # Try to get account info (lightweight test)
                time_response = await api._make_request("GET", "/time")
                
                if "error" in time_response:
                    return {
                        "exchange": exchange,
                        "status": "error",
                        "message": f"API test failed: {time_response['error']}"
                    }
                
                return {
                    "exchange": exchange,
                    "status": "success", 
                    "message": "API key is working correctly",
                    "server_time": time_response.get("time")
                }
        else:
            return {
                "exchange": exchange,
                "status": "not_implemented",
                "message": f"Testing for {exchange} not yet implemented"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        return {
            "exchange": exchange,
            "status": "error",
            "message": f"API test failed: {str(e)}"
        }
