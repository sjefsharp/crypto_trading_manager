from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database_models import Portfolio, Position, Trade
from app.services.bitvavo_api_secure import BitvavoAPI

router = APIRouter()


# Pydantic models
class PortfolioCreate(BaseModel):
    name: str
    description: str = ""


class PortfolioResponse(BaseModel):
    id: int
    name: str
    description: str
    total_value: float
    is_active: bool


class PositionResponse(BaseModel):
    id: int
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    unrealized_pnl: float


class TradeResponse(BaseModel):
    id: int
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: float
    filled_quantity: float
    filled_price: float
    status: str
    created_at: str


@router.post("/", response_model=PortfolioResponse)
async def create_portfolio(
    portfolio: PortfolioCreate, db: Session = Depends(get_db)
) -> PortfolioResponse:
    """Create a new portfolio"""
    try:
        # TODO: Add user authentication and get actual user_id
        db_portfolio = Portfolio(
            user_id=1,  # Placeholder
            name=portfolio.name,
            description=portfolio.description,
        )
        db.add(db_portfolio)
        db.commit()
        db.refresh(db_portfolio)

        return PortfolioResponse(
            id=db_portfolio.id,  # type: ignore
            name=db_portfolio.name,  # type: ignore
            description=db_portfolio.description or "",  # type: ignore
            total_value=db_portfolio.total_value,  # type: ignore
            is_active=db_portfolio.is_active,  # type: ignore
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[PortfolioResponse])
async def get_portfolios(db: Session = Depends(get_db)) -> List[PortfolioResponse]:
    """Get all portfolios for the user"""
    try:
        # TODO: Add user authentication and filter by actual user_id
        portfolios = db.query(Portfolio).filter(Portfolio.user_id == 1).all()

        result = []
        for portfolio in portfolios:
            result.append(
                PortfolioResponse(
                    id=portfolio.id,  # type: ignore
                    name=portfolio.name,  # type: ignore
                    description=portfolio.description or "",  # type: ignore
                    total_value=portfolio.total_value,  # type: ignore
                    is_active=portfolio.is_active,  # type: ignore
                )
            )

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: int, db: Session = Depends(get_db)
) -> PortfolioResponse:
    """Get a specific portfolio"""
    try:
        portfolio = (
            db.query(Portfolio)
            .filter(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == 1,  # TODO: Use actual user_id
            )
            .first()
        )

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        return PortfolioResponse(
            id=portfolio.id,  # type: ignore
            name=portfolio.name,  # type: ignore
            description=portfolio.description or "",  # type: ignore
            total_value=portfolio.total_value,  # type: ignore
            is_active=portfolio.is_active,  # type: ignore
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) without wrapping them
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{portfolio_id}/positions", response_model=List[PositionResponse])
async def get_portfolio_positions(
    portfolio_id: int, db: Session = Depends(get_db)
) -> List[PositionResponse]:
    """Get all positions in a portfolio"""
    try:
        positions = (
            db.query(Position).filter(Position.portfolio_id == portfolio_id).all()
        )

        result = []
        for position in positions:
            result.append(
                PositionResponse(
                    id=position.id,  # type: ignore
                    symbol=position.symbol,  # type: ignore
                    quantity=position.quantity,  # type: ignore
                    average_price=position.average_price,  # type: ignore
                    current_price=position.current_price or 0.0,  # type: ignore
                    unrealized_pnl=position.unrealized_pnl,  # type: ignore
                )
            )

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{portfolio_id}/trades", response_model=List[TradeResponse])
async def get_portfolio_trades(
    portfolio_id: int, db: Session = Depends(get_db)
) -> List[TradeResponse]:
    """Get all trades for a portfolio"""
    try:
        trades = (
            db.query(Trade)
            .filter(
                Trade.portfolio_id == portfolio_id,
                Trade.user_id == 1,  # TODO: Use actual user_id
            )
            .all()
        )

        result = []
        for trade in trades:
            result.append(
                TradeResponse(
                    id=trade.id,  # type: ignore
                    symbol=trade.symbol,  # type: ignore
                    side=trade.side,  # type: ignore
                    order_type=trade.order_type,  # type: ignore
                    quantity=trade.quantity,  # type: ignore
                    price=trade.price or 0.0,  # type: ignore
                    filled_quantity=trade.filled_quantity,  # type: ignore
                    filled_price=trade.filled_price or 0.0,  # type: ignore
                    status=str(trade.status),
                    created_at=trade.created_at.isoformat() if trade.created_at else "",
                )
            )

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{portfolio_id}/update-positions")
async def update_portfolio_positions(
    portfolio_id: int, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update portfolio positions with current market prices"""
    try:
        positions = (
            db.query(Position).filter(Position.portfolio_id == portfolio_id).all()
        )

        async with BitvavoAPI() as api:
            for position in positions:
                # Get current price for the symbol
                market = f"{position.symbol}-EUR"  # Assuming EUR as quote currency
                try:
                    ticker = await api.get_ticker(market)
                    current_price = float(ticker["last"])

                    # Update position with current price and calculate P&L
                    position.current_price = current_price  # type: ignore
                    position.unrealized_pnl = (  # type: ignore
                        current_price - position.average_price
                    ) * position.quantity

                except Exception as e:
                    print(f"Error updating price for {position.symbol}: {e}")
                    continue

        # Calculate total portfolio value
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if portfolio:
            total_value = sum(
                (pos.current_price or 0) * pos.quantity for pos in positions
            )
            portfolio.total_value = total_value  # type: ignore

        db.commit()

        return {"message": "Portfolio positions updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
