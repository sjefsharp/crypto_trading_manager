from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class User(Base):
    """User model for authentication and settings"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    api_keys = relationship(
        "APIKey", back_populates="user", cascade="all, delete-orphan"
    )
    portfolios = relationship(
        "Portfolio", back_populates="user", cascade="all, delete-orphan"
    )
    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")

    def __str__(self) -> str:
        return f"User(username={self.username})"


class APIKey(Base):
    """Encrypted API keys for different exchanges"""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exchange = Column(String(50), nullable=False)  # bitvavo, binance, etc.
    encrypted_api_key = Column(Text, nullable=False)
    encrypted_api_secret = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="api_keys")


class Portfolio(Base):
    """Portfolio tracking"""

    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    total_value = Column(Float, default=0.0)
    initial_balance = Column(Float, default=0.0)  # Add for test compatibility
    current_balance = Column(Float, default=0.0)  # Add for test compatibility
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="portfolios")
    positions = relationship("Position", back_populates="portfolio")
    trades = relationship("Trade", back_populates="portfolio")

    def __init__(self, **kwargs: Any) -> None:
        # Handle balance aliasing
        if "initial_balance" in kwargs and "current_balance" not in kwargs:
            kwargs["current_balance"] = kwargs["initial_balance"]
        elif "current_balance" in kwargs and "initial_balance" not in kwargs:
            kwargs["initial_balance"] = kwargs["current_balance"]
        super().__init__(**kwargs)

    def __str__(self) -> str:
        return f"Portfolio(name={self.name})"


class Position(Base):
    """Current positions in portfolio"""

    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(20), nullable=False)  # BTC, ETH, etc.
    amount = Column(Float, nullable=False)  # Alias for quantity for test compatibility
    quantity = Column(Float, nullable=False)  # Keep both for backward compatibility
    average_price = Column(Float, nullable=False)
    current_price = Column(Float)
    unrealized_pnl = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="positions")

    def __init__(self, **kwargs: Any) -> None:
        # Handle amount/quantity aliasing
        if "amount" in kwargs and "quantity" not in kwargs:
            kwargs["quantity"] = kwargs["amount"]
        elif "quantity" in kwargs and "amount" not in kwargs:
            kwargs["amount"] = kwargs["quantity"]
        super().__init__(**kwargs)


class Trade(Base):
    """Trade execution records"""

    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    exchange = Column(String(50), nullable=False)
    market = Column(String(20), nullable=False)  # BTC-EUR format for test compatibility
    symbol = Column(String(20), nullable=False)  # Keep both for backward compatibility
    side = Column(String(10), nullable=False)  # buy, sell
    order_type = Column(String(20), nullable=False)  # market, limit, stop-loss, etc.
    amount = Column(Float, nullable=False)  # Alias for quantity for test compatibility
    quantity = Column(Float, nullable=False)  # Keep both for backward compatibility
    price = Column(Float)
    filled_quantity = Column(Float, default=0.0)
    filled_price = Column(Float)
    status = Column(
        String(20), default="pending"
    )  # pending, filled, cancelled, rejected
    exchange_order_id = Column(String(100))
    order_id = Column(String(100))  # Alias for exchange_order_id for test compatibility
    fee = Column(Float, default=0.0)  # Alias for fees for test compatibility
    fees = Column(Float, default=0.0)  # Keep both for backward compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="trades")
    portfolio = relationship("Portfolio", back_populates="trades")

    def __init__(self, **kwargs: Any) -> None:
        # Handle field aliasing for test compatibility
        if "amount" in kwargs and "quantity" not in kwargs:
            kwargs["quantity"] = kwargs["amount"]
        elif "quantity" in kwargs and "amount" not in kwargs:
            kwargs["amount"] = kwargs["quantity"]

        if "market" in kwargs and "symbol" not in kwargs:
            # Extract symbol from market (BTC-EUR -> BTC)
            kwargs["symbol"] = kwargs["market"].split("-")[0]
        elif "symbol" in kwargs and "market" not in kwargs:
            kwargs["market"] = f"{kwargs['symbol']}-EUR"  # Default to EUR pair

        if "order_id" in kwargs and "exchange_order_id" not in kwargs:
            kwargs["exchange_order_id"] = kwargs["order_id"]
        elif "exchange_order_id" in kwargs and "order_id" not in kwargs:
            kwargs["order_id"] = kwargs["exchange_order_id"]

        if "fee" in kwargs and "fees" not in kwargs:
            kwargs["fees"] = kwargs["fee"]
        elif "fees" in kwargs and "fee" not in kwargs:
            kwargs["fee"] = kwargs["fees"]

        super().__init__(**kwargs)

    def __str__(self) -> str:
        return f"Trade(market={self.market}, side={self.side}, amount={self.amount})"


class Strategy(Base):
    """Trading strategies configuration"""

    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    strategy_type = Column(
        String(50), nullable=False
    )  # dca, stop_loss, technical_analysis
    config = Column(Text)  # JSON configuration
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MarketData(Base):
    """Historical market data storage"""

    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    source = Column(String(50), default="bitvavo")


class TechnicalIndicator(Base):
    """Calculated technical indicators"""

    __tablename__ = "technical_indicators"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    indicator_name = Column(String(50), nullable=False)  # ema, rsi, macd, etc.
    value = Column(Float, nullable=False)
    parameters = Column(Text)  # JSON with indicator parameters
    created_at = Column(DateTime(timezone=True), server_default=func.now())


__all__ = [
    "Base",
    "User",
    "Portfolio",
    "APIKey",
    "Trade",
    "Position",
    "Strategy",
    "MarketData",
    "TechnicalIndicator",
]
