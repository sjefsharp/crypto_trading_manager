"""
Trading service module for order validation and trading logic
"""
from typing import Dict, Any, List


def validate_order_size(market: str, amount: float) -> Dict[str, Any]:
    """Validate if order size meets minimum requirements"""
    # Minimum order sizes for common markets (simplified)
    min_sizes = {
        "BTC-EUR": 0.001,
        "ETH-EUR": 0.01,
        "ADA-EUR": 1.0,
        "DOT-EUR": 0.1
    }
    
    min_size = min_sizes.get(market, 0.001)  # Default minimum
    
    if amount < min_size:
        return {
            "is_valid": False,
            "error": f"Order size {amount} is below minimum {min_size} for {market}"
        }
    
    return {
        "is_valid": True,
        "error": None
    }


def calculate_order_fees(order: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate trading fees for an order"""
    amount = order.get("amount", 0.0)
    price = order.get("price", 0.0)
    base_cost = amount * price
    
    # Bitvavo fee structure (simplified)
    fee_percentage = 0.0025  # 0.25%
    trading_fee = base_cost * fee_percentage
    total_cost = base_cost + trading_fee
    
    return {
        "base_cost": base_cost,
        "trading_fee": trading_fee,
        "total_cost": total_cost,
        "fee_percentage": fee_percentage * 100
    }


def check_sufficient_balance(balance: List[Dict], order: Dict[str, Any]) -> Dict[str, Any]:
    """Check if user has sufficient balance for order"""
    market = order.get("market", "")
    side = order.get("side", "")
    amount = order.get("amount", 0.0)
    price = order.get("price", 0.0)
    
    # Determine required currency
    if side == "buy":
        # Need quote currency (EUR for BTC-EUR)
        required_currency = market.split("-")[1] if "-" in market else "EUR"
        required_amount = amount * price
    else:  # sell
        # Need base currency (BTC for BTC-EUR)
        required_currency = market.split("-")[0] if "-" in market else market
        required_amount = amount
    
    # Find balance for required currency
    available_balance = 0.0
    for bal in balance:
        if bal.get("symbol") == required_currency:
            available_balance = bal.get("available", 0.0)
            break
    
    if available_balance >= required_amount:
        return {
            "sufficient": True,
            "message": "Sufficient balance available",
            "required": required_amount,
            "available": available_balance
        }
    else:
        return {
            "sufficient": False,
            "message": f"Insufficient {required_currency} balance. Required: {required_amount}, Available: {available_balance}",
            "required": required_amount,
            "available": available_balance
        }


def generate_stop_loss_order(main_order: Dict[str, Any], stop_loss_percentage: float) -> Dict[str, Any]:
    """Generate a stop loss order based on main order"""
    market = main_order.get("market")
    side = "sell" if main_order.get("side") == "buy" else "buy"
    amount = main_order.get("amount")
    price = main_order.get("price")
    
    # Calculate stop loss trigger price
    if main_order.get("side") == "buy":
        trigger_price = price * (1 - stop_loss_percentage)
    else:
        trigger_price = price * (1 + stop_loss_percentage)
    
    return {
        "market": market,
        "side": side,
        "orderType": "stopLoss",
        "amount": amount,
        "triggerPrice": trigger_price,
        "triggerType": "price"
    }


def generate_take_profit_order(main_order: Dict[str, Any], take_profit_percentage: float) -> Dict[str, Any]:
    """Generate a take profit order based on main order"""
    market = main_order.get("market")
    side = "sell" if main_order.get("side") == "buy" else "buy"
    amount = main_order.get("amount")
    price = main_order.get("price")
    
    # Calculate take profit price
    if main_order.get("side") == "buy":
        take_profit_price = price * (1 + take_profit_percentage)
    else:
        take_profit_price = price * (1 - take_profit_percentage)
    
    return {
        "market": market,
        "side": side,
        "orderType": "limit",
        "amount": amount,
        "price": take_profit_price
    }
