from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database_models import Trade, User
from app.services.bitvavo_api_secure import (
    BitvavoAPI,
    calculate_stop_loss,
    calculate_take_profit,
)

router = APIRouter()


# Pydantic models for request/response
class OrderRequest(BaseModel):
    market: str
    side: str  # buy or sell
    order_type: str  # market, limit, stopLoss, etc.
    amount: float
    price: Optional[float] = None
    trigger_amount: Optional[float] = None
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None


class OrderResponse(BaseModel):
    order_id: str
    status: str
    message: str


class BalanceResponse(BaseModel):
    symbol: str
    available: float
    in_order: float


@router.get("/balance", response_model=List[BalanceResponse])
async def get_balance(db: Session = Depends(get_db)):
    """Get account balance from Bitvavo"""
    try:
        api = BitvavoAPI()
        balance_data = await api.get_balance()

        balances = []
        for item in balance_data:
            balances.append(
                BalanceResponse(
                    symbol=item["symbol"],
                    available=float(item["available"]),
                    in_order=float(item["inOrder"]),
                )
            )

        return balances
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/order", response_model=OrderResponse)
async def place_order(order_request: OrderRequest, db: Session = Depends(get_db)):
    """Place a new trading order"""
    try:
        api = BitvavoAPI()
        # Place the main order
        order_result = await api.place_order(
            market=order_request.market,
            side=order_request.side,
            order_type=order_request.order_type,
            amount=order_request.amount,
            price=order_request.price,
        )

        order_id = order_result["orderId"]

        # If this is a buy/sell order with stop loss or take profit, place additional orders
        if order_request.stop_loss_price and order_request.order_type in [
            "market",
            "limit",
        ]:
            # Place stop loss order
            stop_loss_side = "sell" if order_request.side == "buy" else "buy"
            await api.place_order(
                market=order_request.market,
                side=stop_loss_side,
                order_type="stopLoss",
                amount=order_request.amount,
                triggerPrice=order_request.stop_loss_price,
            )

        if order_request.take_profit_price and order_request.order_type in [
            "market",
            "limit",
        ]:
            # Place take profit order
            take_profit_side = "sell" if order_request.side == "buy" else "buy"
            await api.place_order(
                market=order_request.market,
                side=take_profit_side,
                order_type="limit",
                amount=order_request.amount,
                price=order_request.take_profit_price,
            )

        # Save trade to database
        # TODO: Add user authentication and get actual user_id
        trade = Trade(
            user_id=1,  # Placeholder for now
            exchange="bitvavo",
            symbol=order_request.market,
            side=order_request.side,
            order_type=order_request.order_type,
            quantity=order_request.amount,
            price=order_request.price,
            exchange_order_id=order_id,
            status="pending",
        )
        db.add(trade)
        db.commit()

        return OrderResponse(
            order_id=order_id, status="success", message="Order placed successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders")
async def get_open_orders(market: Optional[str] = None):
    """Get open orders"""
    try:
        api = BitvavoAPI()
        orders = await api.get_orders(market)
        return orders
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/order/{order_id}")
async def cancel_order(order_id: str):
    """Cancel a specific order"""
    try:
        api = BitvavoAPI()
        result = await api.cancel_order(order_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/order-history")
async def get_order_history(market: Optional[str] = None, limit: int = 100):
    """Get order history"""
    try:
        api = BitvavoAPI()
        history = await api.get_trades(market, limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trade-history")
async def get_trade_history(market: Optional[str] = None, limit: int = 100):
    """Get trade history"""
    try:
        api = BitvavoAPI()
        history = await api.get_trades(market, limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
