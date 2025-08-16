from unittest.mock import AsyncMock, patch

import pytest

from app.services.bitvavo_api_secure import BitvavoAPI, TradingHelpers


class TestBitvavoAPI:
    """Test cases for Bitvavo API client"""

    @pytest.mark.asyncio
    async def test_api_initialization(self):
        """Test API client initialization"""
        api = BitvavoAPI(api_key="test_key", api_secret="test_secret")
        assert api.api_key == "test_key"
        assert api.api_secret == "test_secret"
        assert api.base_url == "https://api.bitvavo.com/v2"

    def test_signature_generation(self):
        """Test HMAC signature generation"""
        api = BitvavoAPI(api_key="test_key", api_secret="test_secret")
        timestamp = "1692115200000"
        method = "GET"
        path = "/time"

        signature = api._generate_signature(timestamp, method, path)
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex digest length

    @patch.dict("os.environ", {}, clear=True)
    def test_headers_generation_without_auth(self):
        """Test header generation without authentication"""
        api = BitvavoAPI()
        headers = api._get_headers("GET", "/time")

        assert headers["Content-Type"] == "application/json"
        assert headers["User-Agent"] == "Crypto Trading Manager/1.0"
        assert "bitvavo-access-key" not in headers

    def test_headers_generation_with_auth(self):
        """Test header generation with authentication"""
        api = BitvavoAPI(api_key="test_key", api_secret="test_secret")
        headers = api._get_headers("GET", "/time")

        assert headers["Content-Type"] == "application/json"
        assert headers["bitvavo-access-key"] == "test_key"
        assert "bitvavo-access-signature" in headers
        assert "bitvavo-access-timestamp" in headers

    @pytest.mark.asyncio
    @patch("app.services.bitvavo_api_secure.httpx.AsyncClient")
    async def test_get_time(self, mock_client):
        """Test get_time endpoint"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.json.return_value = {"time": 1692115200000}
        mock_response.status_code = 200

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.aclose = AsyncMock()

        mock_client.return_value = mock_client_instance

        async with BitvavoAPI() as api:
            result = await api.get_time()

        assert result["time"] == 1692115200000
        mock_client_instance.get.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.services.bitvavo_api_secure.httpx.AsyncClient")
    async def test_get_markets(self, mock_client, mock_bitvavo_response):
        """Test get_markets endpoint"""
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_bitvavo_response["markets"]
        mock_response.status_code = 200

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.aclose = AsyncMock()
        mock_client.return_value = mock_client_instance

        async with BitvavoAPI() as api:
            result = await api.get_markets()

        assert len(result) == 1
        assert result[0]["market"] == "BTC-EUR"
        assert result[0]["status"] == "trading"

    @pytest.mark.asyncio
    @patch("app.services.bitvavo_api_secure.httpx.AsyncClient")
    async def test_get_ticker(self, mock_client, mock_bitvavo_response):
        """Test get_ticker endpoint"""
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_bitvavo_response["ticker"]
        mock_response.status_code = 200

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.aclose = AsyncMock()
        mock_client.return_value = mock_client_instance

        async with BitvavoAPI() as api:
            result = await api.get_ticker("BTC-EUR")

        assert result["market"] == "BTC-EUR"
        assert result["last"] == "45000.00"

    @pytest.mark.asyncio
    @patch("app.services.bitvavo_api_secure.httpx.AsyncClient")
    async def test_place_order(self, mock_client, mock_bitvavo_response):
        """Test place_order endpoint - returns simulated response in dry-run mode"""
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_bitvavo_response["order_response"]
        mock_response.status_code = 200

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.aclose = AsyncMock()
        mock_client.return_value = mock_client_instance

        api = BitvavoAPI(api_key="test_key", api_secret="test_secret")
        async with api:
            result = await api.place_order(
                market="BTC-EUR", side="buy", order_type="market", amount=0.001
            )

        # In dry-run mode, we get simulated responses
        assert "orderId" in result  # Order ID will be simulated
        assert result["market"] == "BTC-EUR"
        assert result["side"] == "buy"
        assert result.get("simulated").is_(True)  # Dry-run mode indicator

    @pytest.mark.asyncio
    async def test_api_without_session_raises_error(self):
        """Test that API methods raise error when session is not initialized"""
        api = BitvavoAPI()

        with pytest.raises(RuntimeError, match="API session not initialized"):
            await api.get_time()


class TestTradingHelpers:
    """Test cases for trading helper functions"""

    @pytest.mark.asyncio
    @patch("app.services.bitvavo_api_secure.httpx.AsyncClient")
    async def test_get_current_price(self, mock_client, mock_bitvavo_response):
        """Test get_current_price helper function"""
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_bitvavo_response["ticker"]
        mock_response.status_code = 200

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.aclose = AsyncMock()
        mock_client.return_value = mock_client_instance

        async with BitvavoAPI() as api:
            price = await TradingHelpers.get_current_price(api, "BTC-EUR")

        assert price == 45000.00

    @pytest.mark.asyncio
    async def test_calculate_position_size(self):
        """Test position size calculation"""
        # Risk €100, entry at €45000, stop loss at €44000
        risk_amount = 100.0
        entry_price = 45000.0
        stop_loss_price = 44000.0

        api = BitvavoAPI()  # Not needed for this calculation
        position_size = await TradingHelpers.calculate_position_size(
            api, "BTC-EUR", risk_amount, entry_price, stop_loss_price
        )

        expected_size = risk_amount / (entry_price - stop_loss_price)
        assert position_size == expected_size

    @pytest.mark.asyncio
    async def test_calculate_position_size_zero_risk_raises_error(self):
        """Test that zero risk raises ValueError"""
        api = BitvavoAPI()

        with pytest.raises(
            ValueError, match="Entry price and stop loss price cannot be the same"
        ):
            await TradingHelpers.calculate_position_size(
                api, "BTC-EUR", 100.0, 45000.0, 45000.0
            )

    @pytest.mark.asyncio
    @patch("app.services.bitvavo_api_secure.httpx.AsyncClient")
    async def test_place_stop_loss_order(self, mock_client, mock_bitvavo_response):
        """Test stop loss order placement - returns simulated response in dry-run mode"""
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_bitvavo_response["order_response"]
        mock_response.status_code = 200

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.aclose = AsyncMock()
        mock_client.return_value = mock_client_instance

        api = BitvavoAPI(api_key="test_key", api_secret="test_secret")
        async with api:
            result = await TradingHelpers.place_stop_loss_order(
                api, "BTC-EUR", "buy", 0.001, 44000.0
            )

        # In dry-run mode, we get simulated responses
        assert "orderId" in result  # Order ID will be simulated
        assert result.get("simulated").is_(True)  # Dry-run mode indicator

        # Note: In dry-run mode, actual API calls are not made
        # mock_client_instance.post.assert_called_once()  # Disabled for dry-run
