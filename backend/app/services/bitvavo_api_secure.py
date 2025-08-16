"""
Updated Bitvavo API client with secure configuration and dry-run support
"""

import hashlib
import hmac
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import httpx

from app.services.trading_mode import trading_mode_service

logger = logging.getLogger(__name__)


class BitvavoAPI:
    """Bitvavo API client with secure credential management"""

    def __init__(self, api_key: str = None, api_secret: str = None):
        """Initialize Bitvavo API client"""
        self.base_url = "https://api.bitvavo.com/v2"
        self.rate_limit = 1000  # requests per minute
        self.session = None

        # Use provided credentials first
        if api_key and api_secret:
            self.api_key = api_key
            self.api_secret = api_secret
        else:
            # Check if we're in test mode (pytest running)
            import sys

            if "pytest" in sys.modules:
                # In test mode, only use environment variables
                import os

                self.api_key = os.getenv("BITVAVO_API_KEY")
                self.api_secret = os.getenv("BITVAVO_API_SECRET")
            else:
                # Try to load from database first (user's stored keys)
                try:
                    from app.services.db_api_key_service import get_db_api_key_service

                    db_service = get_db_api_key_service()
                    self.api_key, self.api_secret = db_service.get_bitvavo_credentials()
                except Exception as e:
                    print(f"Could not load from database: {e}")
                    self.api_key, self.api_secret = None, None

                # Fallback to environment variables
                if not self.api_key or not self.api_secret:
                    import os

                    self.api_key = os.getenv("BITVAVO_API_KEY")
                    self.api_secret = os.getenv("BITVAVO_API_SECRET")

        if not self.api_key or not self.api_secret:
            if "pytest" not in sys.modules:  # Only show warning in production
                print(
                    "⚠️ Bitvavo API credentials not found. Some features will be limited."
                )
                print("Configure API keys via the frontend settings.")

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session and hasattr(self.session, "aclose"):
            await self.session.aclose()
        self.session = None

    def _generate_signature(
        self, timestamp: str, method: str, url: str, body: str = ""
    ) -> str:
        """Generate HMAC signature for Bitvavo API authentication"""
        if not self.api_secret:
            raise ValueError("API secret not configured")

        string_to_sign = f"{timestamp}{method}{url}{body}"
        signature = hmac.new(
            self.api_secret.encode(), string_to_sign.encode(), hashlib.sha256
        ).hexdigest()
        return signature

    def _get_headers(
        self, method: str, endpoint: str, body: str = ""
    ) -> Dict[str, str]:
        """Generate authentication headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Crypto Trading Manager/1.0",
        }

        if not self.api_key or not self.api_secret:
            return headers

        timestamp = str(int(time.time() * 1000))
        url = f"/v2{endpoint}"
        signature = self._generate_signature(timestamp, method.upper(), url, body)

        headers.update(
            {
                "bitvavo-access-key": self.api_key,
                "bitvavo-access-signature": signature,
                "bitvavo-access-timestamp": timestamp,
            }
        )

        return headers

    async def _make_request(
        self, method: str, endpoint: str, params: Dict = None, body: Dict = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Bitvavo API"""
        if not self.session:
            raise RuntimeError(
                "API session not initialized. Use 'async with BitvavoAPI() as api:' pattern"
            )

        url = f"{self.base_url}{endpoint}"

        # Prepare request body
        request_body = ""
        if body:
            request_body = json.dumps(body)

        # Generate headers
        headers = self._get_headers(method, endpoint, request_body)

        try:
            if method.upper() == "GET":
                response = await self.session.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = await self.session.post(url, headers=headers, json=body)
            elif method.upper() == "DELETE":
                response = await self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Handle response
            if response.status_code == 200:
                return await response.json()
            else:
                error_data = response.text
                try:
                    error_json = await response.json()
                    return {
                        "error": error_json.get("error", error_data),
                        "status_code": response.status_code,
                    }
                except:
                    return {"error": error_data, "status_code": response.status_code}

        except httpx.TimeoutException:
            return {"error": "Request timeout", "status_code": 408}
        except httpx.ConnectError:
            return {"error": "Connection failed", "status_code": 503}
        except Exception as e:
            return {"error": str(e), "status_code": 500}

    async def test_connection(self) -> Dict[str, Any]:
        """Test API connection and authentication"""
        if not self.api_key or not self.api_secret:
            return {
                "status": "error",
                "message": "API credentials not configured",
                "authenticated": False,
            }

        try:
            result = await self._make_request("GET", "/time")
            if "error" in result:
                return {
                    "status": "error",
                    "message": f"API connection failed: {result['error']}",
                    "authenticated": False,
                }

            # Test authenticated endpoint
            balance_result = await self._make_request("GET", "/balance")
            if "error" in balance_result:
                return {
                    "status": "error",
                    "message": f"Authentication failed: {balance_result['error']}",
                    "authenticated": False,
                }

            return {
                "status": "success",
                "message": "API connection and authentication successful",
                "authenticated": True,
                "server_time": result.get("time"),
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection test failed: {str(e)}",
                "authenticated": False,
            }

    async def get_time(self) -> Dict[str, Any]:
        """Get server time"""
        result = await self._make_request("GET", "/time")
        if "error" in result:
            raise Exception(f"Failed to get server time: {result['error']}")

        return result

    async def get_balance(self) -> List[Dict[str, Any]]:
        """Get account balance with dry-run support"""
        if not self.api_key or not self.api_secret:
            raise ValueError("API credentials not configured")

        # Check if dry-run mode is enabled
        if trading_mode_service.is_dry_run_enabled():
            warning = trading_mode_service.get_mode_warning()
            logger.info(f"{warning}")
            logger.info(f"[DRY RUN] Returning simulated balance")

            # Return simulated balance
            return trading_mode_service.simulate_balance_response()

        # Live trading - get real balance
        logger.info("🔴 LIVE TRADING: Getting real account balance")

        result = await self._make_request("GET", "/balance")
        if "error" in result:
            raise Exception(f"Failed to get balance: {result['error']}")

        return result

    async def get_markets(self) -> List[Dict[str, Any]]:
        """Get available markets"""
        result = await self._make_request("GET", "/markets")
        if "error" in result:
            raise Exception(f"Failed to get markets: {result['error']}")

        return result

    async def get_ticker(self, market: str = None) -> Dict[str, Any]:
        """Get ticker information"""
        endpoint = "/ticker/24hr"
        params = {"market": market} if market else {}

        result = await self._make_request("GET", endpoint, params=params)
        if "error" in result:
            raise Exception(f"Failed to get ticker: {result['error']}")

        return result

    async def get_candles(
        self, market: str, interval: str = "1h", limit: int = 24
    ) -> List[List]:
        """Get candlestick data"""
        params = {"market": market, "interval": interval, "limit": limit}

        result = await self._make_request("GET", f"/{market}/candles", params=params)
        if "error" in result:
            raise Exception(f"Failed to get candles: {result['error']}")

        return result

    async def place_order(
        self,
        market: str,
        side: str,
        order_type: str,
        amount: Optional[float] = None,
        price: Optional[float] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Place a trading order with dry-run support"""
        if not self.api_key or not self.api_secret:
            raise ValueError("API credentials not configured")

        order_data = {
            "market": market,
            "side": side,
            "order_type": order_type,  # Normalized key name
        }

        if amount:
            order_data["amount"] = amount
        if price:
            order_data["price"] = price

        # Add additional parameters
        for key, value in kwargs.items():
            if value is not None:
                order_data[key] = value

        # Check if dry-run mode is enabled
        if trading_mode_service.is_dry_run_enabled():
            warning = trading_mode_service.get_mode_warning()
            logger.warning(f"{warning}")
            logger.info(f"[DRY RUN] Would place order: {order_data}")

            # Return simulated response
            return trading_mode_service.simulate_order_response(order_data)

        # Live trading - proceed with actual API call
        if not trading_mode_service.is_live_trading():
            raise Exception(
                "Live trading not enabled. Check trading mode configuration."
            )

        # Validate live trading requirements
        can_trade, message = trading_mode_service.validate_live_trading_requirements()
        if not can_trade:
            raise Exception(f"Live trading validation failed: {message}")

        logger.warning("🔴 LIVE TRADING: Placing real order!")

        # Convert to API format for real request
        api_order_data = {"market": market, "side": side, "orderType": order_type}

        if amount:
            api_order_data["amount"] = str(amount)
        if price:
            api_order_data["price"] = str(price)

        # Add additional parameters
        for key, value in kwargs.items():
            if value is not None:
                api_order_data[key] = (
                    str(value) if isinstance(value, (int, float)) else value
                )

        result = await self._make_request("POST", "/order", body=api_order_data)
        if "error" in result:
            raise Exception(f"Failed to place order: {result['error']}")

        return result

    async def get_orders(self, market: str = None) -> List[Dict[str, Any]]:
        """Get open orders"""
        if not self.api_key or not self.api_secret:
            raise ValueError("API credentials not configured")

        params = {"market": market} if market else {}
        result = await self._make_request("GET", "/orders", params=params)

        if "error" in result:
            raise Exception(f"Failed to get orders: {result['error']}")

        return result

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order"""
        if not self.api_key or not self.api_secret:
            raise ValueError("API credentials not configured")

        result = await self._make_request("DELETE", f"/order/{order_id}")
        if "error" in result:
            raise Exception(f"Failed to cancel order: {result['error']}")

        return result

    async def get_trades(
        self, market: str = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get trade history"""
        if not self.api_key or not self.api_secret:
            raise ValueError("API credentials not configured")

        params = {"limit": limit}
        if market:
            params["market"] = market

        result = await self._make_request("GET", "/trades", params=params)
        if "error" in result:
            raise Exception(f"Failed to get trades: {result['error']}")

        return result

    async def handle_api_error(self, error: Exception) -> Dict[str, Any]:
        """Handle and format API errors"""
        error_message = str(error).lower()

        if "network" in error_message or "connection" in error_message:
            return {
                "status": "error",
                "message": "Network connection failed. Please check your internet connection.",
                "type": "network_error",
                "retry_after": 30,
            }
        elif "rate" in error_message or "limit" in error_message:
            return {
                "status": "error",
                "message": "Rate limit exceeded. Please wait before making more requests.",
                "type": "rate_limit",
                "retry_after": 60,
            }
        elif "authentication" in error_message or "api key" in error_message:
            return {
                "status": "error",
                "message": "Authentication failed. Please check your API credentials.",
                "type": "auth_error",
            }
        elif "insufficient" in error_message:
            return {
                "status": "error",
                "message": "Insufficient balance for this operation.",
                "type": "balance_error",
            }
        else:
            return {
                "status": "error",
                "message": f"API error: {str(error)}",
                "type": "api_error",
            }


# Helper functions for trading operations
def calculate_stop_loss(price: float, side: str, stop_loss_percentage: float) -> float:
    """Calculate stop loss price"""
    if side == "buy":
        result = price * (1 - stop_loss_percentage)
    else:  # sell
        result = price * (1 + stop_loss_percentage)

    # Round to avoid floating point precision issues
    return round(result, 8)


def calculate_take_profit(
    price: float, side: str, take_profit_percentage: float
) -> float:
    """Calculate take profit price"""
    if side == "buy":
        result = price * (1 + take_profit_percentage)
    else:  # sell
        result = price * (1 - take_profit_percentage)

    # Round to avoid floating point precision issues
    return round(result, 8)


def format_bitvavo_response(
    response: Dict[str, Any], message: str, is_error: bool = False
) -> Dict[str, Any]:
    """Format Bitvavo API response for consistent output"""
    if is_error:
        return {"status": "error", "message": message, "error": response}
    else:
        return {"status": "success", "message": message, "data": response}


def validate_market_pair(market: str) -> bool:
    """Validate market pair format"""
    if not market or "-" not in market:
        return False

    parts = market.split("-")
    if len(parts) != 2:
        return False

    base_currency, quote_currency = parts

    # Check each part has reasonable length (2-6 chars for crypto symbols)
    if len(base_currency) < 2 or len(base_currency) > 6:
        return False
    if len(quote_currency) < 2 or len(quote_currency) > 6:
        return False

    # Check each part contains only alphanumeric characters (no special chars)
    if not base_currency.isalnum() or not quote_currency.isalnum():
        return False

    # Check for uppercase (crypto symbols are typically uppercase)
    if not base_currency.isupper() or not quote_currency.isupper():
        return False

    return True


def calculate_portfolio_value(positions: List[Dict[str, Any]]) -> float:
    """Calculate total portfolio value"""
    total_value = 0.0
    for position in positions:
        amount = position.get("amount", 0.0)
        current_price = position.get("current_price", 0.0)
        total_value += amount * current_price
    return total_value


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100


def parse_bitvavo_timestamp(timestamp) -> Optional[Any]:
    """Parse Bitvavo timestamp to datetime"""
    try:
        from datetime import datetime

        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp / 1000)
        return None
    except:
        return None


def round_to_step_size(amount: float, decimals: int) -> float:
    """Round amount to specified decimal places"""
    return round(amount, decimals)


def validate_order_parameters(params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Validate order parameters"""
    required_fields = ["market", "side", "orderType"]

    for field in required_fields:
        if field not in params:
            return False, f"Required field '{field}' is missing"

    # Additional validation could be added here
    return True, None


def sanitize_api_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Remove sensitive data from API response"""
    sensitive_keys = ["apiKey", "signature", "timestamp", "internalData"]

    cleaned_response = {}
    for key, value in response.items():
        if key not in sensitive_keys:
            cleaned_response[key] = value

    return cleaned_response


class TradingHelpers:
    """Helper class for trading operations"""

    @staticmethod
    async def get_current_price(api: BitvavoAPI, market: str) -> float:
        """Get current price for a market"""
        ticker = await api.get_ticker(market)
        return float(ticker.get("last", 0.0))

    @staticmethod
    async def calculate_position_size(
        api: BitvavoAPI,
        market: str,
        risk_amount: float,
        entry_price: float,
        stop_loss_price: float,
    ) -> float:
        """Calculate position size based on risk amount"""
        if entry_price == stop_loss_price:
            raise ValueError("Entry price and stop loss price cannot be the same")

        price_difference = abs(entry_price - stop_loss_price)
        position_size = risk_amount / price_difference
        return position_size

    @staticmethod
    async def place_stop_loss_order(
        api: BitvavoAPI, market: str, side: str, amount: float, stop_price: float
    ) -> Dict[str, Any]:
        """Place a stop-loss order"""
        return await api.place_order(
            market=market,
            side=side,
            order_type="stopLoss",
            amount=amount,
            triggerAmount=stop_price,
        )
