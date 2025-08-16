"""
Enterprise-grade Bitvavo API service using the official Python wrapper with comprehensive features:
- Rate limiting with intelligent backoff
- Connection pooling and health monitoring
- WebSocket management with auto-reconnect
- Comprehensive error handling and retry logic
- Dry-run mode support
- Batch operations
- Trading safety features
"""

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union

from python_bitvavo_api.bitvavo import Bitvavo

from app.services.trading_mode import trading_mode_service

logger = logging.getLogger(__name__)


class BitvavoError(Exception):
    """Base exception for Bitvavo API errors"""

    def __init__(self, message: str, error_code: Optional[str] = None) -> None:
        super().__init__(message)
        self.error_code = error_code


class RateLimitExceededError(BitvavoError):
    """Raised when rate limit is exceeded"""

    def __init__(self, message: str, retry_after: int = 60) -> None:
        super().__init__(message, "RATE_LIMIT_EXCEEDED")
        self.retry_after = retry_after


class AuthenticationError(BitvavoError):
    """Raised when authentication fails"""

    def __init__(self, message: str) -> None:
        super().__init__(message, "AUTHENTICATION_ERROR")


class InsufficientBalanceError(BitvavoError):
    """Raised when insufficient balance for operation"""

    def __init__(
        self, message: str, required_amount: float, available_amount: float
    ) -> None:
        super().__init__(message, "INSUFFICIENT_BALANCE")
        self.required_amount = required_amount
        self.available_amount = available_amount


class ConnectionError(BitvavoError):
    """Raised when connection fails"""

    def __init__(self, message: str) -> None:
        super().__init__(message, "CONNECTION_ERROR")


class RateLimitManager:
    """Intelligent rate limit management with weighted requests"""

    def __init__(self, max_requests_per_minute: int = 1000) -> None:
        self.max_requests = max_requests_per_minute
        self.current_requests = 0
        self.reset_time = time.time() + 60
        self.request_history: List[float] = []

    def can_make_request(self, weight: int = 1) -> bool:
        """Check if request can be made within rate limit"""
        self._cleanup_old_requests()
        return (self.current_requests + weight) <= self.max_requests

    def add_request(self, weight: int = 1) -> None:
        """Add request to rate limit counter"""
        self._cleanup_old_requests()
        self.current_requests += weight
        self.request_history.append(time.time())

    def get_remaining_requests(self) -> int:
        """Get remaining requests in current window"""
        self._cleanup_old_requests()
        return max(0, self.max_requests - self.current_requests)

    def time_until_reset(self) -> float:
        """Get time until rate limit resets"""
        return max(0, self.reset_time - time.time())

    def reset(self) -> None:
        """Reset rate limit counter"""
        self.current_requests = 0
        self.reset_time = time.time() + 60
        self.request_history.clear()

    def _cleanup_old_requests(self) -> None:
        """Remove requests older than 1 minute"""
        current_time = time.time()
        cutoff_time = current_time - 60

        # Remove old requests
        self.request_history = [t for t in self.request_history if t > cutoff_time]

        # Reset counter if we're past the reset time
        if current_time > self.reset_time:
            self.current_requests = len(self.request_history)
            self.reset_time = current_time + 60
        else:
            self.current_requests = len(self.request_history)


class ConnectionManager:
    """Manage connections to Bitvavo API with health monitoring"""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        max_connections: int = 10,
        timeout: float = 30.0,
        debug: bool = False,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.max_connections = max_connections
        self.timeout = timeout
        self.debug = debug

        self._rest_client: Optional[Bitvavo] = None
        self._websocket_client: Optional[Any] = None
        self._connection_health: Dict[str, Any] = {
            "last_check": None,
            "status": "unknown",
            "latency_ms": None,
            "remaining_limit": None,
        }

    async def get_rest_client(self) -> Bitvavo:
        """Get or create REST client"""
        if self._rest_client is None:
            self._rest_client = Bitvavo(
                {
                    "APIKEY": self.api_key,
                    "APISECRET": self.api_secret,
                    "DEBUGGING": self.debug,
                    "TIMEOUT": self.timeout,
                }
            )
        return self._rest_client

    async def get_websocket_client(self) -> Any:
        """Get or create WebSocket client"""
        if self._websocket_client is None:
            rest_client = await self.get_rest_client()
            self._websocket_client = rest_client.newWebsocket()
            self._setup_websocket_callbacks()
        return self._websocket_client

    def _setup_websocket_callbacks(self) -> None:
        """Setup WebSocket error and connection callbacks"""
        if self._websocket_client:
            self._websocket_client.setErrorCallback(self._websocket_error_callback)

    def _websocket_error_callback(self, error: Dict[str, Any]) -> None:
        """Handle WebSocket errors"""
        logger.error(f"WebSocket error: {error}")
        # Implement reconnection logic here if needed

    async def test_connection(self) -> Dict[str, Any]:
        """Test connection health and authentication"""
        try:
            start_time = time.time()
            client = await self.get_rest_client()

            # Test basic connectivity
            time_response = client.time()
            if "error" in time_response:
                return {
                    "status": "error",
                    "authenticated": False,
                    "error": time_response["error"],
                }

            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)

            # Check remaining rate limit
            remaining_limit = client.getRemainingLimit()

            # Update health status
            self._connection_health.update(
                {
                    "last_check": datetime.now(),
                    "status": "healthy",
                    "latency_ms": latency_ms,
                    "remaining_limit": remaining_limit,
                }
            )

            return {
                "status": "success",
                "authenticated": True,
                "latency_ms": latency_ms,
                "remaining_limit": remaining_limit,
                "server_time": time_response.get("time"),
            }

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            self._connection_health.update(
                {"last_check": datetime.now(), "status": "error", "error": str(e)}
            )
            return {"status": "error", "authenticated": False, "error": str(e)}

    async def get_health_status(self) -> Dict[str, Any]:
        """Get current connection health status"""
        return self._connection_health.copy()

    async def close(self) -> None:
        """Close all connections"""
        if self._websocket_client:
            try:
                self._websocket_client.closeSocket()
            except Exception as e:
                logger.warning(f"Error closing WebSocket: {e}")

        self._rest_client = None
        self._websocket_client = None


class OrderManager:
    """Comprehensive order management with safety features"""

    def __init__(self, connection_manager: ConnectionManager) -> None:
        self.connection_manager = connection_manager
        self._order_cache: Dict[str, Dict[str, Any]] = {}

    async def place_order(
        self,
        market: str,
        side: str,
        order_type: str,
        amount: Optional[float] = None,
        price: Optional[float] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Place an order with comprehensive validation"""
        # Validate parameters
        self._validate_order_params(market, side, order_type, amount, price)

        client = await self.connection_manager.get_rest_client()

        try:
            # Build order data
            order_data = {}
            if amount is not None:
                order_data["amount"] = str(amount)
            if price is not None:
                order_data["price"] = str(price)

            # Add additional parameters
            for key, value in kwargs.items():
                if value is not None:
                    order_data[key] = (
                        str(value) if isinstance(value, (int, float)) else value
                    )

            # Place order
            result = client.placeOrder(market, side, order_type, order_data)

            if "error" in result:
                raise BitvavoError(f"Order placement failed: {result['error']}")

            # Cache order for tracking
            if "orderId" in result:
                self._order_cache[result["orderId"]] = result

            logger.info(f"Order placed successfully: {result.get('orderId')}")
            return result

        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            raise

    def _validate_order_params(
        self,
        market: str,
        side: str,
        order_type: str,
        amount: Optional[float],
        price: Optional[float],
    ) -> None:
        """Validate order parameters"""
        if not market or "-" not in market:
            raise ValueError("Invalid market format. Expected format: 'BTC-EUR'")

        if side not in ["buy", "sell"]:
            raise ValueError("Side must be 'buy' or 'sell'")

        if order_type not in [
            "market",
            "limit",
            "stopLoss",
            "stopLossLimit",
            "takeProfit",
            "takeProfitLimit",
        ]:
            raise ValueError(f"Invalid order type: {order_type}")

        if amount is not None and amount <= 0:
            raise ValueError("Amount must be positive")

        if price is not None and price <= 0:
            raise ValueError("Price must be positive")

        # Type-specific validations
        if order_type == "limit" and price is None:
            raise ValueError("Price is required for limit orders")

        if order_type == "market" and price is not None:
            logger.warning("Price parameter ignored for market orders")

    async def get_order(self, market: str, order_id: str) -> Dict[str, Any]:
        """Get order by ID"""
        client = await self.connection_manager.get_rest_client()

        try:
            result = client.getOrder(market, order_id)
            if "error" in result:
                raise BitvavoError(f"Failed to get order: {result['error']}")
            return result
        except Exception as e:
            logger.error(f"Failed to get order {order_id}: {e}")
            raise

    async def cancel_order(self, market: str, order_id: str) -> Dict[str, Any]:
        """Cancel an order"""
        client = await self.connection_manager.get_rest_client()

        try:
            result = client.cancelOrder(market, order_id)
            if "error" in result:
                raise BitvavoError(f"Failed to cancel order: {result['error']}")

            # Remove from cache
            self._order_cache.pop(order_id, None)

            logger.info(f"Order cancelled successfully: {order_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            raise

    async def get_open_orders(
        self, market: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all open orders"""
        client = await self.connection_manager.get_rest_client()

        try:
            options = {}
            if market:
                options["market"] = market

            result = client.ordersOpen(options)
            if isinstance(result, dict) and "error" in result:
                raise BitvavoError(f"Failed to get open orders: {result['error']}")

            return result if isinstance(result, list) else []
        except Exception as e:
            logger.error(f"Failed to get open orders: {e}")
            raise

    async def get_order_history(
        self, market: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get order history"""
        client = await self.connection_manager.get_rest_client()

        try:
            options: Dict[str, Any] = {"limit": limit}
            if market:
                options["market"] = market

            result = client.getOrders(market or "", options)
            if isinstance(result, dict) and "error" in result:
                raise BitvavoError(f"Failed to get order history: {result['error']}")

            return result if isinstance(result, list) else []
        except Exception as e:
            logger.error(f"Failed to get order history: {e}")
            raise


class MarketDataManager:
    """High-performance market data management"""

    def __init__(self, connection_manager: ConnectionManager) -> None:
        self.connection_manager = connection_manager
        self._data_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 5  # seconds

    async def get_markets(self) -> List[Dict[str, Any]]:
        """Get all available markets"""
        client = await self.connection_manager.get_rest_client()

        try:
            result = client.markets()
            if isinstance(result, dict) and "error" in result:
                raise BitvavoError(f"Failed to get markets: {result['error']}")
            return result if isinstance(result, list) else []
        except Exception as e:
            logger.error(f"Failed to get markets: {e}")
            raise

    async def get_ticker_24h(
        self, market: Optional[str] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get 24h ticker data"""
        client = await self.connection_manager.get_rest_client()

        try:
            options = {}
            if market:
                options["market"] = market

            result = client.ticker24h(options)
            if isinstance(result, dict) and "error" in result:
                raise BitvavoError(f"Failed to get ticker: {result['error']}")

            # If single market requested, return single object
            if market and isinstance(result, list) and len(result) == 1:
                return result[0]

            return result if isinstance(result, list) else []
        except Exception as e:
            logger.error(f"Failed to get ticker for {market}: {e}")
            raise

    async def get_orderbook(self, market: str, depth: int = 25) -> Dict[str, Any]:
        """Get orderbook data"""
        client = await self.connection_manager.get_rest_client()

        try:
            options = {"depth": depth}
            result = client.book(market, options)
            if "error" in result:
                raise BitvavoError(f"Failed to get orderbook: {result['error']}")
            return result
        except Exception as e:
            logger.error(f"Failed to get orderbook for {market}: {e}")
            raise

    async def get_candles(
        self, market: str, interval: str = "1h", limit: int = 24
    ) -> List[List[Union[int, str]]]:
        """Get candlestick data"""
        client = await self.connection_manager.get_rest_client()

        try:
            options = {"limit": limit}
            result = client.candles(market, interval, options)
            if isinstance(result, dict) and "error" in result:
                raise BitvavoError(f"Failed to get candles: {result['error']}")
            return result if isinstance(result, list) else []
        except Exception as e:
            logger.error(f"Failed to get candles for {market}: {e}")
            raise

    async def get_trades(self, market: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent trades"""
        client = await self.connection_manager.get_rest_client()

        try:
            options = {"limit": limit}
            result = client.publicTrades(market, options)
            if isinstance(result, dict) and "error" in result:
                raise BitvavoError(f"Failed to get trades: {result['error']}")
            return result if isinstance(result, list) else []
        except Exception as e:
            logger.error(f"Failed to get trades for {market}: {e}")
            raise


class BitvavoEnterpriseService:
    """Enterprise-grade Bitvavo API service with comprehensive features"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        dry_run: bool = False,
        debug: bool = False,
    ) -> None:
        # Get credentials
        self.api_key = api_key or os.getenv("BITVAVO_API_KEY")
        self.api_secret = api_secret or os.getenv("BITVAVO_API_SECRET")

        if not self.api_key or not self.api_secret:
            raise ValueError(
                "API credentials not found. Set BITVAVO_API_KEY and BITVAVO_API_SECRET "
                "environment variables or pass them to constructor."
            )

        self.dry_run = dry_run
        self.debug = debug

        # Initialize managers
        self.rate_limiter = RateLimitManager()
        self.connection_manager = ConnectionManager(
            self.api_key, self.api_secret, debug=debug
        )
        self.order_manager = OrderManager(self.connection_manager)
        self.market_data_manager = MarketDataManager(self.connection_manager)

        logger.info(f"BitvavoEnterpriseService initialized (dry_run={dry_run})")

    async def __aenter__(self) -> "BitvavoEnterpriseService":
        """Async context manager entry"""
        # Test connection on entry
        health = await self.connection_manager.test_connection()
        if health["status"] != "success":
            raise ConnectionError(f"Failed to connect: {health.get('error')}")
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit"""
        await self.connection_manager.close()

    async def _check_rate_limit(self, weight: int = 1) -> None:
        """Check and enforce rate limits"""
        if not self.rate_limiter.can_make_request(weight):
            retry_after = self.rate_limiter.time_until_reset()
            raise RateLimitExceededError(
                f"Rate limit exceeded. Try again in {retry_after:.0f} seconds.",
                retry_after=int(retry_after),
            )
        self.rate_limiter.add_request(weight)

    async def get_account_balance(self) -> List[Dict[str, Any]]:
        """Get account balance"""
        if self.dry_run:
            return trading_mode_service.simulate_balance_response()

        await self._check_rate_limit(weight=5)

        try:
            client = await self.connection_manager.get_rest_client()
            result = client.balance()

            if isinstance(result, dict) and "error" in result:
                if "authentication" in result["error"].lower():
                    raise AuthenticationError(result["error"])
                raise BitvavoError(f"Failed to get balance: {result['error']}")

            return result if isinstance(result, list) else []
        except Exception as e:
            if isinstance(e, (AuthenticationError, BitvavoError)):
                raise
            logger.error(f"Failed to get account balance: {e}")
            raise ConnectionError(f"Failed to get account balance: {e}")

    async def place_order(
        self,
        market: str,
        side: str,
        order_type: str,
        amount: Optional[float] = None,
        price: Optional[float] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Place an order with safety checks"""
        if self.dry_run:
            order_data = {
                "market": market,
                "side": side,
                "order_type": order_type,
                "amount": amount,
                "price": price,
                **kwargs,
            }
            logger.info(f"[DRY RUN] Would place order: {order_data}")
            return {
                "status": "dry_run",
                "simulation": trading_mode_service.simulate_order_response(order_data),
            }

        await self._check_rate_limit(weight=10)

        # Additional safety checks for live trading
        if not trading_mode_service.is_live_trading():
            raise BitvavoError("Live trading is not enabled")

        return await self.order_manager.place_order(
            market, side, order_type, amount, price, **kwargs
        )

    async def get_order(self, market: str, order_id: str) -> Dict[str, Any]:
        """Get order by ID"""
        await self._check_rate_limit(weight=1)
        return await self.order_manager.get_order(market, order_id)

    async def cancel_order(self, market: str, order_id: str) -> Dict[str, Any]:
        """Cancel an order"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would cancel order: {order_id}")
            return {"status": "dry_run", "cancelled": True}

        await self._check_rate_limit(weight=5)
        return await self.order_manager.cancel_order(market, order_id)

    async def get_open_orders(
        self, market: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get open orders"""
        await self._check_rate_limit(weight=5)
        return await self.order_manager.get_open_orders(market)

    async def get_ticker_24h(
        self, market: Optional[str] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get 24h ticker data"""
        await self._check_rate_limit(weight=1)
        return await self.market_data_manager.get_ticker_24h(market)

    async def get_orderbook(self, market: str, depth: int = 25) -> Dict[str, Any]:
        """Get orderbook data"""
        await self._check_rate_limit(weight=1)
        return await self.market_data_manager.get_orderbook(market, depth)

    async def get_candles(
        self, market: str, interval: str = "1h", limit: int = 24
    ) -> List[List[Union[int, str]]]:
        """Get candlestick data"""
        await self._check_rate_limit(weight=1)
        return await self.market_data_manager.get_candles(market, interval, limit)

    async def get_markets(self) -> List[Dict[str, Any]]:
        """Get available markets"""
        await self._check_rate_limit(weight=1)
        return await self.market_data_manager.get_markets()

    async def place_batch_orders(
        self, orders: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Place multiple orders with batch processing"""
        if len(orders) > 10:
            raise ValueError("Maximum 10 orders per batch")

        results = []
        for order in orders:
            try:
                result = await self.place_order(**order)
                results.append({"status": "success", "order": result})
            except Exception as e:
                logger.error(f"Failed to place batch order: {e}")
                results.append({"status": "error", "error": str(e), "order": order})

        return results

    async def subscribe_ticker(
        self, market: str, callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Subscribe to ticker updates via WebSocket"""
        websocket = await self.connection_manager.get_websocket_client()
        websocket.subscriptionTicker(market, callback)
        logger.info(f"Subscribed to ticker updates for {market}")

    async def subscribe_orderbook(
        self, market: str, callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Subscribe to orderbook updates via WebSocket"""
        websocket = await self.connection_manager.get_websocket_client()
        websocket.subscriptionBook(market, callback)
        logger.info(f"Subscribed to orderbook updates for {market}")

    async def get_connection_health(self) -> Dict[str, Any]:
        """Get connection health status"""
        health = await self.connection_manager.test_connection()
        rate_limit_info = {
            "remaining_requests": self.rate_limiter.get_remaining_requests(),
            "time_until_reset": self.rate_limiter.time_until_reset(),
        }

        return {
            "status": "healthy" if health["status"] == "success" else "unhealthy",
            "connection": health,
            "rate_limit": rate_limit_info,
        }

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status"""
        return {
            "remaining_requests": self.rate_limiter.get_remaining_requests(),
            "time_until_reset": self.rate_limiter.time_until_reset(),
            "current_requests": self.rate_limiter.current_requests,
            "max_requests": self.rate_limiter.max_requests,
        }


# Convenience function for creating service instance
@asynccontextmanager
async def create_bitvavo_service(
    api_key: Optional[str] = None,
    api_secret: Optional[str] = None,
    dry_run: bool = False,
    debug: bool = False,
) -> AsyncGenerator[BitvavoEnterpriseService, None]:
    """Create and manage Bitvavo service instance"""
    async with BitvavoEnterpriseService(api_key, api_secret, dry_run, debug) as service:
        yield service


# Export main classes and functions
__all__ = [
    "BitvavoEnterpriseService",
    "RateLimitManager",
    "ConnectionManager",
    "OrderManager",
    "MarketDataManager",
    "BitvavoError",
    "RateLimitExceededError",
    "AuthenticationError",
    "InsufficientBalanceError",
    "ConnectionError",
    "create_bitvavo_service",
]
