"""
Market data service module for processing and analyzing market data
"""

from datetime import datetime
from typing import Any, Dict, List, cast


def process_ticker_data(raw_ticker: Dict[str, Any]) -> Dict[str, Any]:
    """Process raw ticker data from exchange"""
    processed = {}

    # Convert string values to floats
    for key, value in raw_ticker.items():
        if key in [
            "price",
            "high",
            "low",
            "volume",
            "bid",
            "ask",
            "bestBid",
            "bestAsk",
        ]:
            try:
                processed[key] = float(value)
            except (ValueError, TypeError):
                processed[key] = 0.0
        else:
            processed[key] = value

    # Calculate spread if bid/ask available
    if "bid" in processed and "ask" in processed:
        processed["spread"] = processed["ask"] - processed["bid"]
        if processed["ask"] > 0:
            processed["spread_percentage"] = (
                processed["spread"] / processed["ask"]
            ) * 100
        else:
            processed["spread_percentage"] = 0.0

    return processed


def process_candle_data(raw_candles: List[Any]) -> List[Dict[str, Any]]:
    """Process raw candle data into standardized format"""
    processed_candles: List[Dict[str, Any]] = []

    for candle in raw_candles:
        if isinstance(candle, (list, tuple)) and len(candle) >= 6:
            candle_list = cast(List[Any], candle)
            processed_candle: Dict[str, Any] = {
                "timestamp": float(candle_list[0]),
                "open": float(candle_list[1]),
                "high": float(candle_list[2]),
                "low": float(candle_list[3]),
                "close": float(candle_list[4]),
                "volume": float(candle_list[5]),
            }

            # Convert timestamp to datetime if needed
            timestamp_value = processed_candle["timestamp"]
            if isinstance(timestamp_value, str):
                timestamp_value = float(timestamp_value)

            timestamp_seconds = float(timestamp_value)
            if timestamp_seconds > 1000000000000:  # Milliseconds
                timestamp_seconds = timestamp_seconds / 1000

            processed_candle["datetime"] = datetime.fromtimestamp(timestamp_seconds)
            processed_candles.append(processed_candle)

    return processed_candles


def calculate_price_change(
    current_price: float, previous_price: float
) -> Dict[str, Any]:
    """Calculate price change metrics"""
    absolute_change = current_price - previous_price

    percentage_change = 0.0
    if previous_price > 0:
        percentage_change = (absolute_change / previous_price) * 100

    direction = (
        "up" if absolute_change > 0 else "down" if absolute_change < 0 else "neutral"
    )

    return {
        "absolute_change": absolute_change,
        "percentage_change": percentage_change,
        "direction": direction,
    }


def check_price_alerts(
    alerts: List[Dict[str, Any]], market: str, current_price: float
) -> List[Dict[str, Any]]:
    """Check if any price alerts should be triggered"""
    triggered_alerts = []

    for alert in alerts:
        if not alert.get("active", True):
            continue

        if alert.get("market") != market:
            continue

        condition = alert.get("condition")
        alert_price = alert.get("price", 0.0)

        triggered = False

        if condition == "above" and current_price > alert_price:
            triggered = True
        elif condition == "below" and current_price < alert_price:
            triggered = True
        elif condition == "equal" and abs(current_price - alert_price) < (
            alert_price * 0.001
        ):  # 0.1% tolerance
            triggered = True

        if triggered:
            triggered_alerts.append(alert)

    return triggered_alerts


def calculate_moving_average(prices: List[float], period: int) -> float:
    """Calculate simple moving average"""
    if len(prices) < period:
        return 0.0

    recent_prices = prices[-period:]
    return sum(recent_prices) / len(recent_prices)


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """Calculate Relative Strength Index"""
    if len(prices) < period + 1:
        return 50.0  # Neutral value

    # Calculate price changes
    gains: List[float] = []
    losses: List[float] = []

    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(abs(change))

    # Calculate average gains and losses
    if len(gains) >= period:
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    return 50.0


def detect_trend(
    prices: List[float], short_period: int = 5, long_period: int = 20
) -> str:
    """Detect price trend based on moving averages"""
    if len(prices) < long_period:
        return "neutral"

    short_ma = calculate_moving_average(prices, short_period)
    long_ma = calculate_moving_average(prices, long_period)

    if short_ma > long_ma * 1.02:  # 2% above
        return "bullish"
    elif short_ma < long_ma * 0.98:  # 2% below
        return "bearish"
    else:
        return "neutral"
