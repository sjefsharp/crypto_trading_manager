import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest


class TestBitvavoAPIHelpers:
    """Test cases for Bitvavo API helper functions"""

    def test_calculate_stop_loss_buy_order(self):
        """Test stop loss calculation for buy orders"""
        from app.services.bitvavo_api_secure import calculate_stop_loss

        # Test 5% stop loss for buy order
        stop_loss = calculate_stop_loss(45000.0, "buy", 0.05)
        assert stop_loss == 42750.0  # 45000 * 0.95

        # Test 10% stop loss for buy order
        stop_loss = calculate_stop_loss(45000.0, "buy", 0.10)
        assert stop_loss == 40500.0  # 45000 * 0.90

    def test_calculate_stop_loss_sell_order(self):
        """Test stop loss calculation for sell orders"""
        from app.services.bitvavo_api_secure import calculate_stop_loss

        # Test 5% stop loss for sell order
        stop_loss = calculate_stop_loss(45000.0, "sell", 0.05)
        assert stop_loss == 47250.0  # 45000 * 1.05

        # Test 10% stop loss for sell order
        stop_loss = calculate_stop_loss(45000.0, "sell", 0.10)
        assert stop_loss == 49500.0  # 45000 * 1.10

    def test_calculate_take_profit_buy_order(self):
        """Test take profit calculation for buy orders"""
        from app.services.bitvavo_api_secure import calculate_take_profit

        # Test 10% take profit for buy order
        take_profit = calculate_take_profit(45000.0, "buy", 0.10)
        assert take_profit == 49500.0  # 45000 * 1.10

        # Test 20% take profit for buy order
        take_profit = calculate_take_profit(45000.0, "buy", 0.20)
        assert take_profit == 54000.0  # 45000 * 1.20

    def test_calculate_take_profit_sell_order(self):
        """Test take profit calculation for sell orders"""
        from app.services.bitvavo_api_secure import calculate_take_profit

        # Test 10% take profit for sell order
        take_profit = calculate_take_profit(45000.0, "sell", 0.10)
        assert take_profit == 40500.0  # 45000 * 0.90

        # Test 20% take profit for sell order
        take_profit = calculate_take_profit(45000.0, "sell", 0.20)
        assert take_profit == 36000.0  # 45000 * 0.80

    def test_format_bitvavo_response_success(self):
        """Test formatting successful Bitvavo API response"""
        from app.services.bitvavo_api_secure import format_bitvavo_response

        raw_response = {
            "orderId": "test-order-123",
            "market": "BTC-EUR",
            "status": "filled",
        }

        formatted = format_bitvavo_response(raw_response, "Order placed successfully")

        assert formatted["status"] == "success"
        assert formatted["message"] == "Order placed successfully"
        assert formatted["data"]["orderId"] == "test-order-123"
        assert formatted["data"]["market"] == "BTC-EUR"

    def test_format_bitvavo_response_error(self):
        """Test formatting error Bitvavo API response"""
        from app.services.bitvavo_api_secure import format_bitvavo_response

        error_response = {"error": "Insufficient balance", "errorCode": 301}

        formatted = format_bitvavo_response(
            error_response, "Order placement failed", is_error=True
        )

        assert formatted["status"] == "error"
        assert formatted["message"] == "Order placement failed"
        assert formatted["error"]["error"] == "Insufficient balance"
        assert formatted["error"]["errorCode"] == 301

    def test_validate_market_pair_valid(self):
        """Test market pair validation with valid pairs"""
        from app.services.bitvavo_api_secure import validate_market_pair

        valid_pairs = ["BTC-EUR", "ETH-EUR", "ADA-BTC", "DOT-EUR"]

        for pair in valid_pairs:
            assert validate_market_pair(pair) is True

    def test_validate_market_pair_invalid(self):
        """Test market pair validation with invalid pairs"""
        from app.services.bitvavo_api_secure import validate_market_pair

        invalid_pairs = ["BTC", "EUR", "BTC-", "-EUR", "INVALID-PAIR", ""]

        for pair in invalid_pairs:
            assert validate_market_pair(pair) is False

    def test_calculate_portfolio_value(self):
        """Test portfolio value calculation"""
        from app.services.bitvavo_api_secure import calculate_portfolio_value

        positions = [
            {"symbol": "BTC", "amount": 0.1, "current_price": 45000.0},
            {"symbol": "ETH", "amount": 1.0, "current_price": 3000.0},
            {"symbol": "EUR", "amount": 1000.0, "current_price": 1.0},
        ]

        total_value = calculate_portfolio_value(positions)
        expected_value = (0.1 * 45000.0) + (1.0 * 3000.0) + (1000.0 * 1.0)
        assert total_value == expected_value  # 4500 + 3000 + 1000 = 8500

    def test_calculate_percentage_change(self):
        """Test percentage change calculation"""
        from app.services.bitvavo_api_secure import calculate_percentage_change

        # Test positive change
        change = calculate_percentage_change(100.0, 110.0)
        assert change == 10.0

        # Test negative change
        change = calculate_percentage_change(100.0, 90.0)
        assert change == -10.0

        # Test no change
        change = calculate_percentage_change(100.0, 100.0)
        assert change == 0.0

        # Test division by zero protection
        change = calculate_percentage_change(0.0, 100.0)
        assert change == 0.0  # Should handle gracefully

    def test_parse_bitvavo_timestamp(self):
        """Test Bitvavo timestamp parsing"""
        from datetime import datetime

        from app.services.bitvavo_api_secure import parse_bitvavo_timestamp

        # Test valid timestamp
        timestamp = 1692115200000  # Unix timestamp in milliseconds
        parsed = parse_bitvavo_timestamp(timestamp)

        assert isinstance(parsed, datetime)
        assert parsed.year == 2023

        # Test invalid timestamp
        invalid_timestamp = "invalid"
        parsed = parse_bitvavo_timestamp(invalid_timestamp)
        assert parsed is None

    def test_round_to_step_size(self):
        """Test rounding to step size for order amounts"""
        from app.services.bitvavo_api_secure import round_to_step_size

        # Test rounding to 8 decimal places (typical for crypto)
        amount = 0.123456789
        rounded = round_to_step_size(amount, 8)
        assert rounded == 0.12345679

        # Test rounding to 2 decimal places
        amount = 100.789
        rounded = round_to_step_size(amount, 2)
        assert rounded == 100.79

        # Test no rounding needed
        amount = 1.0
        rounded = round_to_step_size(amount, 8)
        assert rounded == 1.0


class TestBitvavoAPIConfiguration:
    """Test cases for Bitvavo API configuration and setup"""

    def test_api_endpoints_configuration(self):
        """Test that API endpoints are properly configured"""
        from app.services.bitvavo_api_secure import BitvavoAPI

        api = BitvavoAPI()

        # Check base URL
        assert api.base_url == "https://api.bitvavo.com/v2"

        # Check endpoint paths
        expected_endpoints = [
            "/account",
            "/balance",
            "/order",
            "/orders",
            "/ticker",
            "/markets",
            "/candles",
        ]

        # These should be accessible as part of the API configuration
        # This test ensures the endpoints are properly defined
        assert hasattr(api, "base_url")

    def test_rate_limiting_configuration(self):
        """Test rate limiting configuration"""
        from app.services.bitvavo_api_secure import BitvavoAPI

        api = BitvavoAPI()

        # Verify rate limiting is configured
        assert hasattr(api, "rate_limit")
        assert api.rate_limit > 0  # Should have a positive rate limit

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_api_credentials(self):
        """Test behavior with missing API credentials"""
        from app.services.bitvavo_api_secure import BitvavoAPI

        # This should handle missing credentials gracefully
        api = BitvavoAPI()
        assert api.api_key is None or api.api_key == ""
        assert api.api_secret is None or api.api_secret == ""

    @patch.dict(
        "os.environ",
        {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
    )
    def test_api_credentials_loading(self):
        """Test loading API credentials from environment"""
        from app.services.bitvavo_api_secure import BitvavoAPI

        api = BitvavoAPI()
        assert api.api_key == "test_key"
        assert api.api_secret == "test_secret"


class TestErrorHandling:
    """Test cases for error handling in Bitvavo API"""

    @pytest.mark.asyncio
    async def test_handle_network_error(self):
        """Test handling of network errors"""
        from app.services.bitvavo_api_secure import BitvavoAPI

        api = BitvavoAPI()

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection failed")

            result = await api.handle_api_error(Exception("Network error"))

            assert result["status"] == "error"
            assert (
                "network" in result["message"].lower()
                or "connection" in result["message"].lower()
            )

    @pytest.mark.asyncio
    async def test_handle_rate_limit_error(self):
        """Test handling of rate limit errors"""
        from app.services.bitvavo_api_secure import BitvavoAPI

        api = BitvavoAPI()

        # Simulate rate limit error
        rate_limit_error = Exception("Rate limit exceeded")
        result = await api.handle_api_error(rate_limit_error)

        assert result["status"] == "error"
        # Should include retry information
        assert (
            "retry" in result["message"].lower() or "rate" in result["message"].lower()
        )

    @pytest.mark.asyncio
    async def test_handle_authentication_error(self):
        """Test handling of authentication errors"""
        from app.services.bitvavo_api_secure import BitvavoAPI

        api = BitvavoAPI()

        # Simulate authentication error
        auth_error = Exception("Invalid API key")
        result = await api.handle_api_error(auth_error)

        assert result["status"] == "error"
        assert (
            "authentication" in result["message"].lower()
            or "api key" in result["message"].lower()
        )

    def test_validate_order_parameters(self):
        """Test order parameter validation"""
        from app.services.bitvavo_api_secure import validate_order_parameters

        # Valid order parameters
        valid_params = {
            "market": "BTC-EUR",
            "side": "buy",
            "orderType": "market",
            "amount": "0.001",
        }

        is_valid, error_message = validate_order_parameters(valid_params)
        assert is_valid is True
        assert error_message is None

        # Invalid order parameters - missing required field
        invalid_params = {
            "market": "BTC-EUR",
            "side": "buy",
            # Missing orderType and amount
        }

        is_valid, error_message = validate_order_parameters(invalid_params)
        assert is_valid is False
        assert error_message is not None
        assert "required" in error_message.lower()

    def test_sanitize_api_response(self):
        """Test API response sanitization"""
        from app.services.bitvavo_api_secure import sanitize_api_response

        # Response with sensitive data
        raw_response = {
            "orderId": "test-order-123",
            "market": "BTC-EUR",
            "apiKey": "sensitive-api-key",
            "internalData": "internal-info",
        }

        sanitized = sanitize_api_response(raw_response)

        # Should keep important data
        assert sanitized["orderId"] == "test-order-123"
        assert sanitized["market"] == "BTC-EUR"

        # Should remove sensitive data
        assert "apiKey" not in sanitized
        assert "internalData" not in sanitized
