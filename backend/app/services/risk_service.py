"""
Risk management service module for trading risk assessment and management
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


def calculate_position_risk(
    position: Dict[str, Any], portfolio_value: float, portfolio_balance: float
) -> Dict[str, Any]:
    """Calculate risk metrics for a single position"""
    amount = position.get("amount", 0.0)
    current_price = position.get("current_price", 0.0)
    average_price = position.get("average_price", position.get("entry_price", 0.0))

    # Current position value
    current_value = amount * current_price

    # Position cost
    position_cost = amount * average_price

    # Unrealized P&L
    unrealized_pnl = current_value - position_cost

    # Position size as percentage of portfolio
    position_size_percentage = (
        (current_value / portfolio_value * 100) if portfolio_value > 0 else 0
    )

    # Unrealized P&L percentage
    unrealized_pnl_percentage = (
        (unrealized_pnl / position_cost * 100) if position_cost > 0 else 0
    )

    # Risk score based on position size and volatility
    risk_score = position_size_percentage

    # Risk level based on position size
    risk_level = "low"
    if position_size_percentage > 30:
        risk_level = "high"
    elif position_size_percentage > 15:
        risk_level = "medium"

    return {
        "current_value": current_value,
        "position_cost": position_cost,
        "unrealized_pnl": unrealized_pnl,
        "position_size_percentage": position_size_percentage,
        "unrealized_pnl_percentage": unrealized_pnl_percentage,
        "risk_score": risk_score,
        "risk_level": risk_level,
        # Keep old keys for backward compatibility
        "position_percentage": position_size_percentage,
    }


def calculate_portfolio_risk(
    portfolio: Dict[str, Any], market_data: Dict[str, float]
) -> Dict[str, Any]:
    """Calculate overall portfolio risk metrics"""
    total_value = portfolio.get("total_value", 0.0)
    positions = portfolio.get("positions", [])

    high_risk_positions = 0
    medium_risk_positions = 0
    total_exposure = 0.0
    max_position_risk = 0.0

    position_risks = []

    for position in positions:
        market = position.get("market", "")
        current_price = market_data.get(market, 0.0)

        if current_price > 0:
            # Add current_price to position data for the risk calculation
            position_with_price = position.copy()
            position_with_price["current_price"] = current_price

            risk_data = calculate_position_risk(
                position_with_price, total_value, total_value
            )
            position_risks.append(risk_data)

            exposure = risk_data["position_size_percentage"]
            total_exposure += exposure
            max_position_risk = max(max_position_risk, exposure)

            if risk_data["risk_level"] == "high":
                high_risk_positions += 1
            elif risk_data["risk_level"] == "medium":
                medium_risk_positions += 1

    # Overall risk assessment
    overall_risk = "low"
    if high_risk_positions > 2 or max_position_risk > 40:
        overall_risk = "high"
    elif high_risk_positions > 0 or medium_risk_positions > 3 or max_position_risk > 25:
        overall_risk = "medium"

    return {
        "overall_risk": overall_risk,
        "high_risk_positions": high_risk_positions,
        "medium_risk_positions": medium_risk_positions,
        "total_exposure": total_exposure,
        "max_position_risk": max_position_risk,
        "position_risks": position_risks,
    }


def check_order_risk(
    order: Dict[str, Any], portfolio: Dict[str, Any], market_price: float
) -> Dict[str, Any]:
    """Check risk factors for a new order"""
    order_type = order.get("side", "buy")
    amount = order.get("amount", 0.0)
    market = order.get("market", "")

    # Order value
    order_value = amount * market_price

    # Portfolio values
    total_value = portfolio.get("total_value", 0.0)
    available_balance = portfolio.get("available_balance", 0.0)

    # Order size as percentage of portfolio
    order_percentage = (order_value / total_value * 100) if total_value > 0 else 0

    # Check for sufficient balance
    sufficient_balance = available_balance >= order_value

    # Risk warnings
    warnings = []

    if order_percentage > 25:
        warnings.append("Large order size - over 25% of portfolio")
    elif order_percentage > 15:
        warnings.append("Medium order size - over 15% of portfolio")

    if not sufficient_balance:
        warnings.append("Insufficient balance for order")

    # Check existing position concentration
    existing_positions = portfolio.get("positions", [])
    current_exposure = 0.0
    for position in existing_positions:
        if position.get("market") == market:
            position_value = position.get("amount", 0.0) * market_price
            current_exposure = (
                (position_value / total_value * 100) if total_value > 0 else 0
            )
            break

    total_exposure = current_exposure + order_percentage
    if total_exposure > 40:
        warnings.append(f"High concentration risk - {total_exposure:.1f}% in {market}")

    # Risk level
    risk_level = "low"
    if len(warnings) > 1 or order_percentage > 25:
        risk_level = "high"
    elif len(warnings) > 0 or order_percentage > 15:
        risk_level = "medium"

    return {
        "risk_level": risk_level,
        "order_percentage": order_percentage,
        "sufficient_balance": sufficient_balance,
        "warnings": warnings,
        "current_exposure": current_exposure,
        "total_exposure": total_exposure,
    }


def calculate_stop_loss_price(
    entry_price: float, side: str, risk_percentage: float = 5.0
) -> float:
    """Calculate stop loss price based on risk percentage"""
    if side.lower() == "buy":
        # For long positions, stop loss is below entry price
        stop_loss = entry_price * (1 - risk_percentage / 100)
    else:
        # For short positions, stop loss is above entry price
        stop_loss = entry_price * (1 + risk_percentage / 100)

    return stop_loss


def calculate_take_profit_price(
    entry_price: float,
    side: str,
    profit_ratio: float = 2.0,
    risk_percentage: float = 5.0,
) -> float:
    """Calculate take profit price based on risk-reward ratio"""
    profit_percentage = risk_percentage * profit_ratio

    if side.lower() == "buy":
        # For long positions, take profit is above entry price
        take_profit = entry_price * (1 + profit_percentage / 100)
    else:
        # For short positions, take profit is below entry price
        take_profit = entry_price * (1 - profit_percentage / 100)

    return take_profit


def check_drawdown_limits(
    portfolio_history: List[Dict[str, Any]], max_drawdown: float = 20.0
) -> Dict[str, Any]:
    """Check if portfolio is approaching maximum drawdown limits"""
    if len(portfolio_history) < 2:
        return {"warning": False, "current_drawdown": 0.0}

    # Find peak value
    peak_value = max(entry.get("total_value", 0.0) for entry in portfolio_history)
    current_value = portfolio_history[-1].get("total_value", 0.0)

    # Calculate current drawdown
    current_drawdown = (
        ((peak_value - current_value) / peak_value * 100) if peak_value > 0 else 0.0
    )

    # Check warning levels
    warning = current_drawdown > (max_drawdown * 0.8)  # Warning at 80% of max
    critical = current_drawdown > max_drawdown

    return {
        "warning": warning,
        "critical": critical,
        "current_drawdown": current_drawdown,
        "max_drawdown": max_drawdown,
        "peak_value": peak_value,
        "current_value": current_value,
    }


def generate_risk_recommendations(risk_analysis: Dict[str, Any]) -> List[str]:
    """Generate risk management recommendations based on analysis"""
    recommendations = []

    overall_risk = risk_analysis.get("overall_risk", "low")
    high_risk_positions = risk_analysis.get("high_risk_positions", 0)
    max_position_risk = risk_analysis.get("max_position_risk", 0.0)

    if overall_risk == "high":
        recommendations.append(
            "Consider reducing position sizes to lower portfolio risk"
        )

    if high_risk_positions > 0:
        recommendations.append(
            f"Review {high_risk_positions} high-risk positions for potential reduction"
        )

    if max_position_risk > 30:
        recommendations.append(
            "Largest position exceeds 30% of portfolio - consider diversifying"
        )

    total_exposure = risk_analysis.get("total_exposure", 0.0)
    if total_exposure > 80:
        recommendations.append(
            "Portfolio is highly concentrated - consider adding more positions"
        )

    return recommendations


def validate_order_risk(
    order: Dict[str, Any], portfolio_value: float, risk_limits: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate if an order meets risk management criteria"""
    order_value = order.get("amount", 0.0) * order.get("price", 0.0)
    position_size_percentage = (
        (order_value / portfolio_value * 100) if portfolio_value > 0 else 0
    )

    max_position_size = risk_limits.get("max_position_size_percentage", 25.0)
    max_order_value = risk_limits.get("max_order_value", float("inf"))

    approved = True
    reasons = []

    if position_size_percentage > max_position_size:
        approved = False
        reasons.append(
            f"High risk: position size {position_size_percentage:.1f}% exceeds maximum {max_position_size}%"
        )

    if order_value > max_order_value:
        approved = False
        reasons.append(
            f"High risk: order value {order_value:.2f} exceeds maximum {max_order_value}"
        )

    return {
        "approved": approved,
        "reason": "; ".join(reasons) if reasons else "Order meets risk criteria",
        "position_size_percentage": position_size_percentage,
        "order_value": order_value,
    }


def calculate_portfolio_risk_score(portfolio: Dict[str, Any]) -> float:
    """Calculate a risk score (0-100) for the portfolio based on composition and volatility"""
    positions = portfolio.get("positions", [])
    total_value = portfolio.get("total_value", 0.0)

    if not positions or total_value <= 0:
        return 0.0

    weighted_volatility = 0.0
    crypto_allocation = 0.0
    max_position_weight = 0.0

    for position in positions:
        market_value = position.get("market_value", 0.0)
        volatility = position.get("volatility", 0.0)
        symbol = position.get("symbol", "").upper()

        # Calculate position weight
        weight = market_value / total_value
        max_position_weight = max(max_position_weight, weight)

        # Add to weighted volatility
        weighted_volatility += weight * volatility

        # Track crypto allocation (exclude EUR/USD/fiat)
        if symbol not in ["EUR", "USD", "USDT", "USDC"]:
            crypto_allocation += weight

    # Base risk score from weighted volatility (0-100 scale)
    risk_score = min(weighted_volatility * 100, 100)

    # Add concentration risk penalty
    if max_position_weight > 0.5:  # More than 50% in one asset
        risk_score += 20
    elif max_position_weight > 0.3:  # More than 30% in one asset
        risk_score += 10

    # Add crypto concentration penalty
    if crypto_allocation > 0.8:  # More than 80% in crypto
        risk_score += 15
    elif crypto_allocation > 0.6:  # More than 60% in crypto
        risk_score += 10

    return min(risk_score, 100.0)
