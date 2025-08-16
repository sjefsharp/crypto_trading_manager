import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# Import models to register with Base

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def test_db():
    """Create a test database"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestingSessionLocal()
    app.dependency_overrides.clear()


# Mock data fixtures
@pytest.fixture
def mock_bitvavo_response():
    """Mock responses for Bitvavo API"""
    return {
        "balance": [
            {"symbol": "EUR", "available": "1000.0", "inOrder": "0.0"},
            {"symbol": "BTC", "available": "0.1", "inOrder": "0.0"},
        ],
        "markets": [
            {
                "market": "BTC-EUR",
                "status": "trading",
                "base": "BTC",
                "quote": "EUR",
                "pricePrecision": 2,
                "minOrderInBaseAsset": "0.001",
                "minOrderInQuoteAsset": "10",
                "orderTypes": ["market", "limit"],
            }
        ],
        "ticker": {
            "market": "BTC-EUR",
            "price": "45000.0",
            "size": "0.001",
            "bestBid": "44950.0",
            "bestAsk": "45050.0",
            "bestBidSize": "1.0",
            "bestAskSize": "1.0",
        },
        "order_response": {
            "orderId": "test-order-123",
            "market": "BTC-EUR",
            "created": 1692115200000,
            "updated": 1692115200000,
            "status": "filled",
            "side": "buy",
            "orderType": "market",
            "amount": "0.001",
            "amountRemaining": "0.0",
            "price": "45000.0",
            "onHold": "0.0",
            "onHoldCurrency": "EUR",
            "triggerPrice": "",
            "triggerType": "",
            "triggerReference": "",
            "selfTradePrevention": "decrementAndCancel",
            "visible": True,
            "timeInForce": "GTC",
            "postOnly": False,
            "clientOrderId": "",
        },
    }


@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio data for testing"""
    return {"name": "Test Portfolio", "description": "Test portfolio for unit testing"}


@pytest.fixture
def sample_order_data():
    """Sample order data for testing"""
    return {"market": "BTC-EUR", "side": "buy", "order_type": "market", "amount": 0.001}


# API Mocks
@pytest.fixture
def mock_bitvavo_api():
    """Mock Bitvavo API instance"""
    mock_api = AsyncMock()
    mock_api.api_key = "test_key"
    mock_api.api_secret = "test_secret"
    mock_api.base_url = "https://api.bitvavo.com/v2"
    mock_api.rate_limit = 1000

    # Mock API methods
    mock_api.test_connection.return_value = {
        "status": "success",
        "message": "Connection successful",
        "authenticated": True,
    }

    mock_api.get_balance.return_value = [
        {"symbol": "EUR", "available": 1000.0},
        {"symbol": "BTC", "available": 0.1},
    ]

    mock_api.get_markets.return_value = [{"market": "BTC-EUR", "status": "trading"}]

    mock_api.get_ticker.return_value = {"market": "BTC-EUR", "last": 45000.0}

    mock_api.place_order.return_value = {
        "orderId": "test-order-123",
        "status": "filled",
    }

    return mock_api


# Database mocks
@pytest.fixture
def mock_user():
    """Mock user object"""
    user = MagicMock()
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.is_active = True
    return user


@pytest.fixture
def mock_portfolio():
    """Mock portfolio object"""
    portfolio = MagicMock()
    portfolio.id = 1
    portfolio.user_id = 1
    portfolio.name = "Test Portfolio"
    portfolio.description = "Test portfolio"
    portfolio.total_value = 10000.0
    return portfolio


# Async test helper
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
    }


@pytest.fixture
def mock_api_instance():
    """Mock API client fixture"""
    mock_api = AsyncMock()
    return mock_api
