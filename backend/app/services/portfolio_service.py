"""
Portfolio service module for portfolio management operations
"""

from typing import Any, Dict, List


def calculate_portfolio_performance(portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate portfolio performance metrics"""
    initial_balance = portfolio_data.get("initial_balance", 0.0)
    current_balance = portfolio_data.get("current_balance", 0.0)
    positions = portfolio_data.get("positions", [])

    # Calculate total unrealized P&L
    total_unrealized_pnl = 0.0
    positions_performance = []

    for position in positions:
        amount = position.get("amount", 0.0)
        avg_price = position.get("average_price", 0.0)
        current_price = position.get("current_price", 0.0)

        unrealized_pnl = amount * (current_price - avg_price)
        total_unrealized_pnl += unrealized_pnl

        position_perf = {
            "symbol": position.get("symbol"),
            "unrealized_pnl": unrealized_pnl,
            "percentage_change": (
                ((current_price - avg_price) / avg_price * 100)
                if avg_price > 0
                else 0.0
            ),
        }
        positions_performance.append(position_perf)

    # Calculate total return percentage
    total_return_percentage = 0.0
    if initial_balance > 0:
        total_return_percentage = (
            (current_balance - initial_balance) / initial_balance
        ) * 100

    return {
        "total_return_percentage": total_return_percentage,
        "unrealized_pnl": total_unrealized_pnl,
        "positions_performance": positions_performance,
        "total_value": current_balance + total_unrealized_pnl,
    }


def update_portfolio_positions(
    existing_positions: List[Dict], new_trade: Dict[str, Any]
) -> List[Dict]:
    """Update portfolio positions based on new trade"""
    symbol = new_trade.get("symbol")
    side = new_trade.get("side")
    amount = new_trade.get("amount", 0.0)
    price = new_trade.get("price", 0.0)

    # Find existing position for this symbol
    position_found = False
    updated_positions = []

    for position in existing_positions:
        if position.get("symbol") == symbol:
            position_found = True
            existing_amount = position.get("amount", 0.0)
            existing_avg_price = position.get("average_price", 0.0)

            if side == "buy":
                # Add to position
                new_amount = existing_amount + amount
                new_avg_price = (
                    (existing_amount * existing_avg_price) + (amount * price)
                ) / new_amount

                updated_position = position.copy()
                updated_position["amount"] = new_amount
                updated_position["average_price"] = new_avg_price
                updated_positions.append(updated_position)
            else:  # sell
                # Reduce position
                new_amount = max(0, existing_amount - amount)
                updated_position = position.copy()
                updated_position["amount"] = new_amount
                if new_amount > 0:
                    updated_positions.append(updated_position)
        else:
            updated_positions.append(position)

    # If position not found and it's a buy, create new position
    if not position_found and side == "buy":
        new_position = {
            "symbol": symbol,
            "amount": amount,
            "average_price": price,
            "current_price": price,
        }
        updated_positions.append(new_position)

    return updated_positions


def calculate_position_pnl(position: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate P&L for a single position"""
    amount = position.get("amount", 0.0)
    average_price = position.get("average_price", 0.0)
    current_price = position.get("current_price", 0.0)

    unrealized_pnl = amount * (current_price - average_price)
    percentage_change = 0.0
    if average_price > 0:
        percentage_change = ((current_price - average_price) / average_price) * 100

    market_value = amount * current_price

    return {
        "unrealized_pnl": unrealized_pnl,
        "percentage_change": percentage_change,
        "market_value": market_value,
    }


def get_rebalance_suggestions(
    portfolio: Dict[str, Any], target_allocation: Dict[str, float]
) -> List[Dict[str, Any]]:
    """Generate portfolio rebalancing suggestions"""
    total_value = portfolio.get("total_value", 0.0)
    positions = portfolio.get("positions", [])
    suggestions = []

    # Calculate current allocation
    current_allocation = {}
    for position in positions:
        symbol = position.get("symbol")
        market_value = position.get("market_value", 0.0)
        current_allocation[symbol] = (
            market_value / total_value if total_value > 0 else 0.0
        )

    # Generate suggestions
    for symbol, target_percentage in target_allocation.items():
        current_percentage = current_allocation.get(symbol, 0.0)
        difference = target_percentage - current_percentage

        if abs(difference) > 0.01:  # Only suggest if difference > 1%
            target_value = total_value * target_percentage
            current_value = total_value * current_percentage
            value_difference = target_value - current_value

            suggestion = {
                "symbol": symbol,
                "action": "buy" if difference > 0 else "sell",
                "target_percentage": target_percentage * 100,
                "current_percentage": current_percentage * 100,
                "value_difference": abs(value_difference),
                "description": f"{'Buy' if difference > 0 else 'Sell'} {abs(value_difference):.2f} EUR worth of {symbol}",
            }
            suggestions.append(suggestion)

    return suggestions
