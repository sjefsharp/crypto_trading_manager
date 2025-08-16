from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn

from app.core.config import settings
from app.core.database import get_db, engine, Base
from app.api import trading, market_data, portfolio, trading_mode
from app.services.trading_mode import trading_mode_service

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Crypto Trading Manager API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Crypto Trading Manager API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check with trading mode status"""
    mode_warning = trading_mode_service.get_mode_warning()
    return {
        "status": "healthy", 
        "timestamp": "2025-08-15",
        "trading_mode": trading_mode_service.get_current_mode().value,
        "mode_warning": mode_warning
    }

# Include API routers
app.include_router(trading.router, prefix=f"{settings.API_V1_STR}/trading", tags=["trading"])
app.include_router(market_data.router, prefix=f"{settings.API_V1_STR}/market", tags=["market"])
app.include_router(portfolio.router, prefix=f"{settings.API_V1_STR}/portfolio", tags=["portfolio"])
app.include_router(trading_mode.router, prefix=f"{settings.API_V1_STR}", tags=["trading-mode"])

# Import and include API keys router
from app.api import api_keys
app.include_router(api_keys.router, prefix=f"{settings.API_V1_STR}", tags=["api-keys"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
