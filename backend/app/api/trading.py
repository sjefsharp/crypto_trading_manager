from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.bitvavo_api_secure import BitvavoAPI

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
async def get_balance(db: Session = Depends(get_db)) -> List[BalanceResponse]:
    """Get account balance for all currencies"""
    try:
        async with BitvavoAPI() as api:
            balance_result = await api.get_balance()
            balance_data = (
                balance_result.get("balance", [])
                if isinstance(balance_result, dict)
                else balance_result
            )

        balances = []
        for item in balance_data:
            balances.append(
                BalanceResponse(
                    symbol=str(item["symbol"]),
                    available=float(item["available"]),
                    in_order=float(item["inOrder"]),
                )
            )

        return balances
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/order", response_model=OrderResponse)
async def place_order(
    order: OrderRequest, db: Session = Depends(get_db)
) -> OrderResponse:
    """Place a new order"""
    try:
        async with BitvavoAPI() as api:
            order_result = await api.place_order(
                market=order.market,
                side=order.side,
                order_type=order.order_type,
                amount=order.amount,
                price=order.price,
            )

        return OrderResponse(
            order_id=order_result.get("orderId", ""),
            status=order_result.get("status", ""),
            message="Order placed successfully",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/buy")
async def buy_order(
    order: OrderRequest, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Place a buy order"""
    try:
        async with BitvavoAPI() as api:
            order_result = await api.place_order(
                market=order.market,
                side="buy",
                order_type=order.order_type,
                amount=order.amount,
                price=order.price,
            )

        return order_result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sell")
async def sell_order(
    order: OrderRequest, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Place a sell order"""
    try:
        async with BitvavoAPI() as api:
            order_result = await api.place_order(
                market=order.market,
                side="sell",
                order_type=order.order_type,
                amount=order.amount,
                price=order.price,
            )

        return order_result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders")
async def get_open_orders(market: Optional[str] = None) -> Dict[str, Any]:
    """Get open orders"""
    try:
        async with BitvavoAPI() as api:
            orders = await api.get_orders(market)
            return orders
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/order/{order_id}")
async def cancel_order(order_id: str) -> Dict[str, Any]:
    """Cancel an order"""
    try:
        async with BitvavoAPI() as api:
            result = await api.cancel_order(order_id)
            return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/order-history")
async def get_order_history(
    market: Optional[str] = None, limit: int = 100
) -> Dict[str, Any]:
    """Get order history"""
    try:
        async with BitvavoAPI() as api:
            history = await api.get_trades(market, limit)
            return history
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trade-history")
async def get_trade_history(
    market: Optional[str] = None, limit: int = 100
) -> Dict[str, Any]:
    """Get trade history"""
    try:
        async with BitvavoAPI() as api:
            history = await api.get_trades(market, limit)
            return history
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
