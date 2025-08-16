import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_keys, market_data, portfolio, trading, trading_mode
from app.core.config import settings
from app.core.database import Base, engine
from app.services.trading_mode import trading_mode_service

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Enterprise-grade Crypto Trading Manager API with comprehensive trading, portfolio management, and market data capabilities.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    contact={
        "name": "Crypto Trading Manager Team",
        "email": "support@crypto-trading-manager.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "trading",
            "description": "Trading operations including order placement, cancellation, and management",
        },
        {
            "name": "market-data",
            "description": "Market data endpoints for prices, tickers, and historical data",
        },
        {
            "name": "portfolio",
            "description": "Portfolio management and position tracking",
        },
        {
            "name": "trading-mode",
            "description": "Trading mode configuration (dry-run, live trading)",
        },
        {
            "name": "health",
            "description": "Application health and status monitoring",
        },
    ],
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
        "mode_warning": mode_warning,
    }


# Include API routers
app.include_router(
    trading.router, prefix=f"{settings.API_V1_STR}/trading", tags=["trading"]
)
app.include_router(
    market_data.router, prefix=f"{settings.API_V1_STR}/market", tags=["market"]
)
app.include_router(
    portfolio.router, prefix=f"{settings.API_V1_STR}/portfolio", tags=["portfolio"]
)
app.include_router(
    trading_mode.router, prefix=f"{settings.API_V1_STR}", tags=["trading-mode"]
)

app.include_router(api_keys.router, prefix=f"{settings.API_V1_STR}", tags=["api-keys"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
