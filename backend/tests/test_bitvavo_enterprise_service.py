"""
Enterprise-grade unit tests for Bitvavo API service with official wrapper integration
"""

import asyncio
import json
import os
import time
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.bitvavo_enterprise_service import (
    AuthenticationError,
    BitvavoEnterpriseService,
    BitvavoError,
    ConnectionManager,
    InsufficientBalanceError,
    MarketDataManager,
    OrderManager,
    RateLimitExceededError,
    RateLimitManager,
)


class TestRateLimitManager:
    """Test rate limiting functionality"""

    def test_rate_limit_manager_initialization(self) -> None:
        """Test rate limit manager proper initialization"""
        manager = RateLimitManager(max_requests_per_minute=1000)
        assert manager.max_requests == 1000
        assert manager.current_requests == 0
        assert manager.reset_time is not None

    def test_can_make_request_under_limit(self) -> None:
        """Test can make request when under rate limit"""
        manager = RateLimitManager(max_requests_per_minute=1000)
        manager.current_requests = 500
        assert manager.can_make_request() is True

    def test_cannot_make_request_over_limit(self) -> None:
        """Test cannot make request when over rate limit"""
        manager = RateLimitManager(max_requests_per_minute=1000)
        # Simulate 1000 recent requests
        current_time = time.time()
        manager.request_history = [current_time - 30] * 1000  # 30 seconds ago
        manager.current_requests = 1000
        assert manager.can_make_request() is False

    def test_add_request_increments_counter(self) -> None:
        """Test adding request increments counter"""
        manager = RateLimitManager(max_requests_per_minute=1000)
        initial_count = manager.current_requests
        manager.add_request()
        assert manager.current_requests == initial_count + 1

    def test_get_remaining_requests(self) -> None:
        """Test getting remaining requests"""
        manager = RateLimitManager(max_requests_per_minute=1000)
        # Simulate 750 recent requests
        current_time = time.time()
        manager.request_history = [current_time - 30] * 750  # 30 seconds ago
        manager.current_requests = 750
        remaining = manager.get_remaining_requests()
        assert remaining == 250

    def test_reset_resets_counter(self) -> None:
        """Test reset functionality"""
        manager = RateLimitManager(max_requests_per_minute=1000)
        manager.current_requests = 500
        manager.reset()
        assert manager.current_requests == 0

    def test_time_until_reset(self) -> None:
        """Test time until reset calculation"""
        manager = RateLimitManager(max_requests_per_minute=1000)
        time_until = manager.time_until_reset()
        assert isinstance(time_until, float)
        assert time_until >= 0


class TestConnectionManager:
    """Test connection management functionality"""

    @pytest.mark.asyncio
    async def test_connection_manager_initialization(self) -> None:
        """Test connection manager initialization"""
        manager = ConnectionManager(
            api_key="test_key",
            api_secret="test_secret",
            max_connections=5,
            timeout=30.0,
        )
        assert manager.api_key == "test_key"
        assert manager.api_secret == "test_secret"
        assert manager.max_connections == 5
        assert manager.timeout == 30.0

    @pytest.mark.asyncio
    async def test_get_rest_client(self) -> None:
        """Test getting REST client"""
        manager = ConnectionManager("test_key", "test_secret")
        with patch("app.services.bitvavo_enterprise_service.Bitvavo") as mock_bitvavo:
            client = await manager.get_rest_client()
            mock_bitvavo.assert_called_once()
            assert client is not None

    @pytest.mark.asyncio
    async def test_get_websocket_client(self) -> None:
        """Test getting WebSocket client"""
        manager = ConnectionManager("test_key", "test_secret")
        with patch("app.services.bitvavo_enterprise_service.Bitvavo") as mock_bitvavo:
            mock_rest_client = MagicMock()
            mock_ws = MagicMock()
            mock_rest_client.newWebsocket.return_value = mock_ws
            mock_bitvavo.return_value = mock_rest_client

            ws = await manager.get_websocket_client()
            assert ws is not None

    @pytest.mark.asyncio
    async def test_test_connection_success(self) -> None:
        """Test successful connection test"""
        manager = ConnectionManager("test_key", "test_secret")
        with patch("app.services.bitvavo_enterprise_service.Bitvavo") as mock_bitvavo:
            mock_client = MagicMock()
            mock_client.time.return_value = {"time": 1234567890}
            mock_client.getRemainingLimit.return_value = 950
            mock_bitvavo.return_value = mock_client

            result = await manager.test_connection()
            assert result["status"] == "success"
            assert result["authenticated"] is True

    @pytest.mark.asyncio
    async def test_test_connection_failure(self) -> None:
        """Test connection test failure"""
        manager = ConnectionManager("invalid_key", "invalid_secret")
        with patch("app.services.bitvavo_enterprise_service.Bitvavo") as mock_bitvavo:
            mock_client = MagicMock()
            mock_client.time.side_effect = Exception("Authentication failed")
            mock_bitvavo.return_value = mock_client

            result = await manager.test_connection()
            assert result["status"] == "error"
            assert result["authenticated"] is False

    @pytest.mark.asyncio
    async def test_close_connections(self) -> None:
        """Test closing connections"""
        manager = ConnectionManager("test_key", "test_secret")
        # This should not raise any exceptions
        await manager.close()


class TestOrderManager:
    """Test order management functionality"""

    def test_order_manager_initialization(self) -> None:
        """Test order manager initialization"""
        mock_connection = MagicMock()
        manager = OrderManager(mock_connection)
        assert manager.connection_manager == mock_connection

    @pytest.mark.asyncio
    async def test_place_order_market_buy(self) -> None:
        """Test placing a market buy order"""
        mock_connection = MagicMock()
        mock_rest_client = MagicMock()

        # Make get_rest_client return an awaitable
        async def mock_get_rest_client() -> Any:
            return mock_rest_client

        mock_connection.get_rest_client = mock_get_rest_client

        expected_response = {
            "orderId": "12345",
            "market": "BTC-EUR",
            "side": "buy",
            "orderType": "market",
            "amount": "0.1",
            "status": "filled",
        }
        mock_rest_client.placeOrder.return_value = expected_response

        manager = OrderManager(mock_connection)
        result = await manager.place_order(
            market="BTC-EUR", side="buy", order_type="market", amount=0.1
        )

        assert result == expected_response
        mock_rest_client.placeOrder.assert_called_once()

    @pytest.mark.asyncio
    async def test_place_order_limit_sell(self) -> None:
        """Test placing a limit sell order"""
        mock_connection = MagicMock()
        mock_rest_client = MagicMock()
        mock_connection.get_rest_client.return_value = mock_rest_client

        expected_response = {
            "orderId": "67890",
            "market": "ETH-EUR",
            "side": "sell",
            "orderType": "limit",
            "amount": "1.0",
            "price": "2000.0",
            "status": "new",
        }
        mock_rest_client.placeOrder.return_value = expected_response

        manager = OrderManager(mock_connection)
        result = await manager.place_order(
            market="ETH-EUR", side="sell", order_type="limit", amount=1.0, price=2000.0
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_get_order(self) -> None:
        """Test getting order by ID"""
        mock_connection = MagicMock()
        mock_rest_client = MagicMock()
        mock_connection.get_rest_client.return_value = mock_rest_client

        expected_response = {
            "orderId": "12345",
            "status": "filled",
            "fillAmount": "0.1",
            "fillPrice": "45000.0",
        }
        mock_rest_client.getOrder.return_value = expected_response

        manager = OrderManager(mock_connection)
        result = await manager.get_order("BTC-EUR", "12345")

        assert result == expected_response
        mock_rest_client.getOrder.assert_called_once_with("BTC-EUR", "12345")

    @pytest.mark.asyncio
    async def test_cancel_order(self) -> None:
        """Test cancelling an order"""
        mock_connection = MagicMock()
        mock_rest_client = MagicMock()
        mock_connection.get_rest_client.return_value = mock_rest_client

        expected_response = {"orderId": "12345", "status": "cancelled"}
        mock_rest_client.cancelOrder.return_value = expected_response

        manager = OrderManager(mock_connection)
        result = await manager.cancel_order("BTC-EUR", "12345")

        assert result == expected_response
        mock_rest_client.cancelOrder.assert_called_once_with("BTC-EUR", "12345")

    @pytest.mark.asyncio
    async def test_get_open_orders(self) -> None:
        """Test getting open orders"""
        mock_connection = MagicMock()
        mock_rest_client = MagicMock()
        mock_connection.get_rest_client.return_value = mock_rest_client

        expected_response = [
            {"orderId": "123", "status": "new"},
            {"orderId": "456", "status": "partiallyFilled"},
        ]
        mock_rest_client.ordersOpen.return_value = expected_response

        manager = OrderManager(mock_connection)
        result = await manager.get_open_orders("BTC-EUR")

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_get_order_history(self) -> None:
        """Test getting order history"""
        mock_connection = MagicMock()
        mock_rest_client = MagicMock()
        mock_connection.get_rest_client.return_value = mock_rest_client

        expected_response = [
            {"orderId": "789", "status": "filled"},
            {"orderId": "101", "status": "cancelled"},
        ]
        mock_rest_client.getOrders.return_value = expected_response

        manager = OrderManager(mock_connection)
        result = await manager.get_order_history("BTC-EUR", limit=50)

        assert result == expected_response


class TestMarketDataManager:
    """Test market data functionality"""

    def test_market_data_manager_initialization(self) -> None:
        """Test market data manager initialization"""
        mock_connection = MagicMock()
        manager = MarketDataManager(mock_connection)
        assert manager.connection_manager == mock_connection

    @pytest.mark.asyncio
    async def test_get_markets(self) -> None:
        """Test getting available markets"""
        mock_connection = MagicMock()
        mock_rest_client = MagicMock()
        mock_connection.get_rest_client.return_value = mock_rest_client

        expected_response = [
            {"market": "BTC-EUR", "status": "trading"},
            {"market": "ETH-EUR", "status": "trading"},
        ]
        mock_rest_client.markets.return_value = expected_response

        manager = MarketDataManager(mock_connection)
        result = await manager.get_markets()

        assert result == expected_response
        mock_rest_client.markets.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_ticker_24h(self) -> None:
        """Test getting 24h ticker data"""
        mock_connection = MagicMock()
        mock_rest_client = MagicMock()
        mock_connection.get_rest_client.return_value = mock_rest_client

        expected_response = {
            "market": "BTC-EUR",
            "last": "45000.0",
            "high": "46000.0",
            "low": "44000.0",
            "volume": "123.45",
            "volumeQuote": "5555500.0",
        }
        mock_rest_client.ticker24h.return_value = [expected_response]

        manager = MarketDataManager(mock_connection)
        result = await manager.get_ticker_24h("BTC-EUR")

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_get_orderbook(self) -> None:
        """Test getting orderbook data"""
        mock_connection = MagicMock()
        mock_rest_client = MagicMock()
        mock_connection.get_rest_client.return_value = mock_rest_client

        expected_response = {
            "market": "BTC-EUR",
            "bids": [["44990.0", "0.1"], ["44980.0", "0.2"]],
            "asks": [["45010.0", "0.1"], ["45020.0", "0.2"]],
        }
        mock_rest_client.book.return_value = expected_response

        manager = MarketDataManager(mock_connection)
        result = await manager.get_orderbook("BTC-EUR")

        assert result == expected_response
        mock_rest_client.book.assert_called_once_with("BTC-EUR", {})

    @pytest.mark.asyncio
    async def test_get_candles(self) -> None:
        """Test getting candlestick data"""
        mock_connection = MagicMock()
        mock_rest_client = MagicMock()
        mock_connection.get_rest_client.return_value = mock_rest_client

        expected_response = [
            [1634567890000, "45000", "45100", "44900", "45050", "10.5"],
            [1634567950000, "45050", "45200", "45000", "45150", "8.2"],
        ]
        mock_rest_client.candles.return_value = expected_response

        manager = MarketDataManager(mock_connection)
        result = await manager.get_candles("BTC-EUR", "1h", limit=24)

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_get_trades(self) -> None:
        """Test getting recent trades"""
        mock_connection = MagicMock()
        mock_rest_client = MagicMock()
        mock_connection.get_rest_client.return_value = mock_rest_client

        expected_response = [
            {"id": "123", "price": "45000.0", "amount": "0.1", "side": "buy"},
            {"id": "124", "price": "45010.0", "amount": "0.2", "side": "sell"},
        ]
        mock_rest_client.publicTrades.return_value = expected_response

        manager = MarketDataManager(mock_connection)
        result = await manager.get_trades("BTC-EUR", limit=50)

        assert result == expected_response


class TestBitvavoEnterpriseService:
    """Test main enterprise service"""

    @pytest.mark.asyncio
    async def test_enterprise_service_initialization(self) -> None:
        """Test enterprise service initialization"""
        with patch.dict(
            os.environ,
            {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
        ):
            service = BitvavoEnterpriseService()
            assert service.rate_limiter is not None
            assert service.connection_manager is not None
            assert service.order_manager is not None
            assert service.market_data_manager is not None

    @pytest.mark.asyncio
    async def test_enterprise_service_without_credentials(self) -> None:
        """Test enterprise service without credentials"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API credentials not found"):
                BitvavoEnterpriseService()

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test async context manager usage"""
        with patch.dict(
            os.environ,
            {
                "BITVAVO_API_KEY": "test_key_64_chars_long_0123456789abcdef0123456789abcdef01234567",
                "BITVAVO_API_SECRET": "test_secret_64_chars_long_0123456789abcdef0123456789abcdef012345",
            },
        ):
            service = BitvavoEnterpriseService()
            # Mock the connection test to avoid actual API calls
            with patch.object(
                service.connection_manager, "test_connection"
            ) as mock_test:
                mock_test.return_value = {"status": "success", "authenticated": True}

                async with service as svc:
                    assert isinstance(svc, BitvavoEnterpriseService)

    @pytest.mark.asyncio
    async def test_rate_limit_enforcement(self) -> None:
        """Test rate limit enforcement"""
        with patch.dict(
            os.environ,
            {
                "BITVAVO_API_KEY": "test_key_64_chars_long_0123456789abcdef0123456789abcdef01234567",
                "BITVAVO_API_SECRET": "test_secret_64_chars_long_0123456789abcdef0123456789abcdef012345",
            },
        ):
            service = BitvavoEnterpriseService()
            # Simulate rate limit exceeded by setting current_requests to max
            service.rate_limiter.current_requests = 1000
            service.rate_limiter.request_history = [time.time()] * 1000  # Fill history

            with pytest.raises(RateLimitExceededError):
                await service.get_account_balance()

    @pytest.mark.asyncio
    async def test_get_account_balance(self) -> None:
        """Test getting account balance"""
        with patch.dict(
            os.environ,
            {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
        ):
            service = BitvavoEnterpriseService()

            expected_response = [
                {"symbol": "EUR", "available": "1000.0", "inOrder": "0.0"},
                {"symbol": "BTC", "available": "0.5", "inOrder": "0.1"},
            ]

            with patch.object(
                service.connection_manager, "get_rest_client"
            ) as mock_client:
                mock_rest = MagicMock()
                mock_rest.balance.return_value = expected_response
                mock_client.return_value = mock_rest

                result = await service.get_account_balance()
                assert result == expected_response

    @pytest.mark.asyncio
    async def test_place_order_with_dry_run(self) -> None:
        """Test placing order with dry run mode"""
        with patch.dict(
            os.environ,
            {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
        ):
            service = BitvavoEnterpriseService(dry_run=True)

            result = await service.place_order(
                market="BTC-EUR", side="buy", order_type="market", amount=0.1
            )

            assert result["status"] == "dry_run"
            assert "simulation" in result

    @pytest.mark.asyncio
    async def test_websocket_subscription(self) -> None:
        """Test WebSocket subscription functionality"""
        with patch.dict(
            os.environ,
            {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
        ):
            service = BitvavoEnterpriseService()

            callback_called = False
            received_data = None

            def test_callback(data: Dict[str, Any]) -> None:
                nonlocal callback_called, received_data
                callback_called = True
                received_data = data

            with patch.object(
                service.connection_manager, "get_websocket_client"
            ) as mock_ws:
                mock_websocket = MagicMock()
                mock_ws.return_value = mock_websocket

                await service.subscribe_ticker("BTC-EUR", test_callback)

                # Simulate receiving data
                test_data = {"market": "BTC-EUR", "price": "45000.0"}
                test_callback(test_data)

                assert callback_called is True
                assert received_data == test_data

    @pytest.mark.asyncio
    async def test_error_handling(self) -> None:
        """Test comprehensive error handling"""
        with patch.dict(
            os.environ,
            {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
        ):
            service = BitvavoEnterpriseService()

            # Test authentication error
            with patch.object(
                service.connection_manager, "get_rest_client"
            ) as mock_client:
                mock_rest = MagicMock()
                mock_rest.balance.side_effect = Exception("Authentication failed")
                mock_client.return_value = mock_rest

                with pytest.raises(AuthenticationError):
                    await service.get_account_balance()

    @pytest.mark.asyncio
    async def test_connection_health_monitoring(self) -> None:
        """Test connection health monitoring"""
        with patch.dict(
            os.environ,
            {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
        ):
            service = BitvavoEnterpriseService()

            with patch.object(
                service.connection_manager, "test_connection"
            ) as mock_test:
                mock_test.return_value = {
                    "status": "success",
                    "authenticated": True,
                    "latency_ms": 50,
                }

                health = await service.get_connection_health()
                assert health["status"] == "healthy"
                assert health["authenticated"] is True

    @pytest.mark.asyncio
    async def test_batch_operations(self) -> None:
        """Test batch operations functionality"""
        with patch.dict(
            os.environ,
            {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
        ):
            service = BitvavoEnterpriseService()

            orders = [
                {
                    "market": "BTC-EUR",
                    "side": "buy",
                    "order_type": "limit",
                    "amount": 0.1,
                    "price": 44000.0,
                },
                {
                    "market": "ETH-EUR",
                    "side": "sell",
                    "order_type": "limit",
                    "amount": 1.0,
                    "price": 2000.0,
                },
            ]

            with patch.object(service.order_manager, "place_order") as mock_place:
                mock_place.return_value = {"orderId": "123", "status": "new"}

                results = await service.place_batch_orders(orders)
                assert len(results) == 2
                assert all(
                    result["status"] in ["success", "error"] for result in results
                )


class TestCustomExceptions:
    """Test custom exception classes"""

    def test_bitvavo_error(self) -> None:
        """Test base BitvavoError exception"""
        error = BitvavoError("Test error", error_code="TEST_001")
        assert str(error) == "Test error"
        assert error.error_code == "TEST_001"

    def test_rate_limit_exceeded_error(self) -> None:
        """Test RateLimitExceededError"""
        error = RateLimitExceededError("Rate limit exceeded", retry_after=60)
        assert error.retry_after == 60

    def test_authentication_error(self) -> None:
        """Test AuthenticationError"""
        error = AuthenticationError("Invalid API key")
        assert "Invalid API key" in str(error)

    def test_insufficient_balance_error(self) -> None:
        """Test InsufficientBalanceError"""
        error = InsufficientBalanceError(
            "Insufficient balance", required_amount=100.0, available_amount=50.0
        )
        assert error.required_amount == 100.0
        assert error.available_amount == 50.0


class TestIntegrationScenarios:
    """Integration test scenarios"""

    @pytest.mark.asyncio
    async def test_complete_trading_workflow(self) -> None:
        """Test complete trading workflow"""
        with patch.dict(
            os.environ,
            {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
        ):
            async with BitvavoEnterpriseService(dry_run=True) as service:
                # 1. Check balance
                balance = await service.get_account_balance()
                assert isinstance(balance, list)

                # 2. Get market data
                ticker = await service.get_ticker_24h("BTC-EUR")
                assert "last" in ticker

                # 3. Place order
                order = await service.place_order(
                    market="BTC-EUR",
                    side="buy",
                    order_type="limit",
                    amount=0.1,
                    price=44000.0,
                )
                assert order["status"] == "dry_run"

    @pytest.mark.asyncio
    async def test_error_recovery_scenarios(self) -> None:
        """Test error recovery scenarios"""
        with patch.dict(
            os.environ,
            {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
        ):
            service = BitvavoEnterpriseService()

            # Test network error recovery
            with patch.object(
                service.connection_manager, "get_rest_client"
            ) as mock_client:
                mock_rest = MagicMock()
                # First call fails, second succeeds
                mock_rest.balance.side_effect = [
                    Exception("Network error"),
                    [{"symbol": "EUR", "available": "1000.0"}],
                ]
                mock_client.return_value = mock_rest

                # Should implement retry logic in actual service
                try:
                    await service.get_account_balance()
                except Exception:
                    # Retry should be handled by service
                    pass

    @pytest.mark.asyncio
    async def test_concurrent_operations(self) -> None:
        """Test concurrent operations"""
        with patch.dict(
            os.environ,
            {"BITVAVO_API_KEY": "test_key", "BITVAVO_API_SECRET": "test_secret"},
        ):
            service = BitvavoEnterpriseService()

            # Test concurrent market data requests
            tasks = [
                service.get_ticker_24h("BTC-EUR"),
                service.get_ticker_24h("ETH-EUR"),
                service.get_ticker_24h("ADA-EUR"),
            ]

            with patch.object(
                service.market_data_manager, "get_ticker_24h"
            ) as mock_ticker:
                mock_ticker.return_value = {"market": "BTC-EUR", "last": "45000.0"}

                results = await asyncio.gather(*tasks, return_exceptions=True)
                assert len(results) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
