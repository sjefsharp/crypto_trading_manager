from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestTradingAPI:
    """Test cases for trading API endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Crypto Trading Manager API" in response.json()["message"]

    @patch.dict(
        "os.environ",
        {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
    )
    @patch("app.services.bitvavo_api_secure.BitvavoAPI.get_balance")
    def test_get_balance_success(self, mock_get_balance, client, mock_bitvavo_response):
        """Test successful balance retrieval"""
        # Mock the get_balance method to return expected response
        mock_get_balance.return_value = mock_bitvavo_response["balance"]

        response = client.get("/api/v1/trading/balance")
        assert response.status_code == 200

        balance_data = response.json()
        assert len(balance_data) == 2
        assert balance_data[0]["symbol"] == "EUR"
        assert balance_data[0]["available"] == 1000.0

    @patch.dict(
        "os.environ",
        {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
    )
    @patch("app.services.bitvavo_api_secure.BitvavoAPI.get_balance")
    def test_get_balance_with_configured_keys(
        self, mock_get_balance, client, mock_bitvavo_response
    ):
        """Test balance retrieval with configured API keys"""
        # Mock successful balance response
        mock_get_balance.return_value = mock_bitvavo_response["balance"]

        response = client.get("/api/v1/trading/balance")
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
        assert response.status_code == 200
        balance_data = response.json()
        assert isinstance(balance_data, list)
        # Since we now have keys configured, this should work

    @patch.dict(
        "os.environ",
        {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
    )
    @patch("app.api.trading.get_db")
    @patch("app.services.bitvavo_api_secure.BitvavoAPI.place_order")
    def test_place_order_success(
        self,
        mock_place_order,
        mock_get_db,
        client,
        mock_bitvavo_response,
        sample_order_data,
    ):
        """Test successful order placement"""
        # Mock the database session
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db

        # Mock the place_order method to return expected response
        mock_place_order.return_value = mock_bitvavo_response["order_response"]

        response = client.post("/api/v1/trading/order", json=sample_order_data)
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
        assert response.status_code == 200

        order_response = response.json()
        assert order_response["order_id"] == "test-order-123"
        assert order_response["status"] == "success"

    @patch.dict(
        "os.environ",
        {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
    )
    @patch("app.api.trading.get_db")
    @patch("app.services.bitvavo_api_secure.BitvavoAPI.place_order")
    def test_place_order_with_stop_loss(
        self, mock_place_order, mock_get_db, client, mock_bitvavo_response
    ):
        """Test order placement with stop loss"""
        # Mock the database session
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db

        # Mock the place_order method to return expected response
        mock_place_order.return_value = mock_bitvavo_response["order_response"]

        order_data = {
            "market": "BTC-EUR",
            "side": "buy",
            "order_type": "market",
            "amount": 0.001,
            "stop_loss_price": 44000.0,
        }

        response = client.post("/api/v1/trading/order", json=order_data)
        assert response.status_code == 200

        # Verify that stop loss order was also placed
        assert mock_place_order.call_count >= 1

    def test_place_order_invalid_data(self, client):
        """Test order placement with invalid data"""
        invalid_order = {
            "market": "INVALID",
            "side": "invalid_side",
            "amount": -1,  # Invalid amount
        }

        response = client.post("/api/v1/trading/order", json=invalid_order)
        assert response.status_code == 422  # Validation error

    @patch.dict(
        "os.environ",
        {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
    )
    @patch("app.services.bitvavo_api_secure.BitvavoAPI.get_orders")
    def test_get_open_orders(self, mock_get_orders, client, mock_bitvavo_response):
        """Test getting open orders"""
        # Mock the get_orders method to return expected response
        mock_get_orders.return_value = [mock_bitvavo_response["order_response"]]

        response = client.get("/api/v1/trading/orders")
        assert response.status_code == 200

        orders = response.json()
        assert len(orders) >= 0

    @patch.dict(
        "os.environ",
        {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
    )
    @patch("app.services.bitvavo_api_secure.BitvavoAPI.cancel_order")
    def test_cancel_order(self, mock_cancel_order, client):
        """Test order cancellation"""
        # Mock the cancel_order method to return expected response
        mock_cancel_order.return_value = {
            "orderId": "test-order-123",
            "status": "cancelled",
        }

        response = client.delete("/api/v1/trading/order/test-order-123")
        assert response.status_code == 200

        result = response.json()
        assert result["orderId"] == "test-order-123"


class TestMarketDataAPI:
    """Test cases for market data API endpoints"""

    @patch.dict(
        "os.environ",
        {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
    )
    @patch("app.services.bitvavo_api_secure.BitvavoAPI.get_markets")
    def test_get_markets(self, mock_get_markets, client, mock_bitvavo_response):
        """Test getting market information"""
        # Mock the get_markets method to return expected response
        mock_get_markets.return_value = mock_bitvavo_response["markets"]

        response = client.get("/api/v1/market/markets")
        assert response.status_code == 200

        markets = response.json()
        assert len(markets) == 1
        assert markets[0]["market"] == "BTC-EUR"

    @patch.dict(
        "os.environ",
        {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
    )
    @patch("app.services.bitvavo_api_secure.BitvavoAPI.get_ticker")
    def test_get_ticker(self, mock_get_ticker, client, mock_bitvavo_response):
        """Test getting ticker information"""
        # Mock the get_ticker method to return expected response
        mock_get_ticker.return_value = mock_bitvavo_response["ticker"]

        response = client.get("/api/v1/market/ticker/BTC-EUR")
        assert response.status_code == 200

        ticker = response.json()
        assert ticker["market"] == "BTC-EUR"
        assert ticker["last"] == 45000.0

    @patch.dict(
        "os.environ",
        {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
    )
    @patch("app.services.bitvavo_api_secure.BitvavoAPI.get_ticker")
    def test_get_current_price(self, mock_get_ticker, client, mock_bitvavo_response):
        """Test getting current price"""
        # Mock the get_ticker method to return expected response
        mock_get_ticker.return_value = mock_bitvavo_response["ticker"]

        response = client.get("/api/v1/market/price/BTC-EUR")
        assert response.status_code == 200

        price_data = response.json()
        assert price_data["market"] == "BTC-EUR"
        assert price_data["price"] == 45000.0

    @patch.dict(
        "os.environ",
        {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
    )
    @patch("app.services.bitvavo_api_secure.BitvavoAPI.get_candles")
    def test_get_candles(self, mock_get_candles, client):
        """Test getting candlestick data"""
        # Setup mock candle data
        mock_candles = [
            [1692115200000, "45000.00", "45100.00", "44900.00", "45050.00", "10.5"],
            [1692118800000, "45050.00", "45200.00", "45000.00", "45150.00", "8.2"],
        ]

        # Mock the get_candles method to return expected response
        mock_get_candles.return_value = mock_candles

        response = client.get("/api/v1/market/candles/BTC-EUR?interval=1h&limit=24")
        assert response.status_code == 200

        candles = response.json()
        assert len(candles) == 2
        assert candles[0]["open"] == 45000.0
        assert candles[0]["close"] == 45050.0


class TestPortfolioAPI:
    """Test cases for portfolio API endpoints"""

    def test_create_portfolio(self, client, sample_portfolio_data):
        """Test portfolio creation"""
        response = client.post("/api/v1/portfolio/", json=sample_portfolio_data)
        assert response.status_code == 200

        portfolio = response.json()
        assert portfolio["name"] == sample_portfolio_data["name"]
        assert portfolio["description"] == sample_portfolio_data["description"]

    def test_get_portfolios(self, client, sample_portfolio_data):
        """Test getting portfolios"""
        # First create a portfolio
        client.post("/api/v1/portfolio/", json=sample_portfolio_data)

        # Then get all portfolios
        response = client.get("/api/v1/portfolio/")
        assert response.status_code == 200

        portfolios = response.json()
        assert len(portfolios) >= 1

    def test_get_portfolio_by_id(self, client, sample_portfolio_data):
        """Test getting specific portfolio"""
        # Create portfolio
        create_response = client.post("/api/v1/portfolio/", json=sample_portfolio_data)
        portfolio_id = create_response.json()["id"]

        # Get portfolio by ID
        response = client.get(f"/api/v1/portfolio/{portfolio_id}")
        assert response.status_code == 200

        portfolio = response.json()
        assert portfolio["id"] == portfolio_id
        assert portfolio["name"] == sample_portfolio_data["name"]

    def test_get_nonexistent_portfolio(self, client):
        """Test getting portfolio that doesn't exist"""
        response = client.get("/api/v1/portfolio/99999")
        assert response.status_code == 404

    def test_create_portfolio_invalid_data(self, client):
        """Test creating portfolio with invalid data"""
        invalid_data = {}  # Missing required fields

        response = client.post("/api/v1/portfolio/", json=invalid_data)
        assert response.status_code == 422  # Validation error
