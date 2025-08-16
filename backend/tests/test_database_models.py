from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db
from app.models.database_models import Base, Portfolio, Position, Trade, User


class TestDatabaseModels:
    """Test cases for SQLAlchemy database models"""

    @pytest.fixture
    def test_engine(self):
        """Create in-memory SQLite database for testing"""
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        return engine

    @pytest.fixture
    def test_session(self, test_engine):
        """Create database session for testing"""
        TestingSessionLocal = sessionmaker(bind=test_engine)
        session = TestingSessionLocal()
        yield session
        session.close()

    def test_user_model_creation(self, test_session):
        """Test User model creation and fields"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword123",
            is_active=True,
        )

        test_session.add(user)
        test_session.commit()

        # Retrieve user
        retrieved_user = (
            test_session.query(User).filter(User.username == "testuser").first()
        )
        assert retrieved_user is not None
        assert retrieved_user.username == "testuser"
        assert retrieved_user.email == "test@example.com"
        assert retrieved_user.is_active is True
        assert retrieved_user.created_at is not None

    def test_user_model_relationships(self, test_session):
        """Test User model relationships with portfolios"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword123",
        )
        test_session.add(user)
        test_session.commit()

        # Create portfolio for user
        portfolio = Portfolio(
            user_id=user.id,
            name="Test Portfolio",
            description="Test portfolio description",
        )
        test_session.add(portfolio)
        test_session.commit()

        # Test relationship
        assert len(user.portfolios) == 1
        assert user.portfolios[0].name == "Test Portfolio"
        assert portfolio.user.username == "testuser"

    def test_portfolio_model_creation(self, test_session):
        """Test Portfolio model creation and fields"""
        # First create a user
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword123",
        )
        test_session.add(user)
        test_session.commit()

        # Create portfolio
        portfolio = Portfolio(
            user_id=user.id,
            name="My Crypto Portfolio",
            description="My main cryptocurrency portfolio",
            initial_balance=10000.0,
        )

        test_session.add(portfolio)
        test_session.commit()

        # Retrieve portfolio
        retrieved_portfolio = (
            test_session.query(Portfolio)
            .filter(Portfolio.name == "My Crypto Portfolio")
            .first()
        )
        assert retrieved_portfolio is not None
        assert retrieved_portfolio.name == "My Crypto Portfolio"
        assert retrieved_portfolio.description == "My main cryptocurrency portfolio"
        assert retrieved_portfolio.initial_balance == 10000.0
        assert retrieved_portfolio.current_balance == 10000.0  # Default value
        assert retrieved_portfolio.created_at is not None

    def test_trade_model_creation(self, test_session):
        """Test Trade model creation and fields"""
        # Create user and portfolio
        user = User(
            username="testuser", email="test@example.com", hashed_password="hash123"
        )
        test_session.add(user)
        test_session.commit()

        portfolio = Portfolio(
            user_id=user.id, name="Test Portfolio", description="Test"
        )
        test_session.add(portfolio)
        test_session.commit()

        # Create trade
        trade = Trade(
            user_id=user.id,
            portfolio_id=portfolio.id,
            exchange="bitvavo",
            market="BTC-EUR",
            side="buy",
            order_type="market",
            amount=0.001,
            price=45000.0,
            fee=0.25,
            order_id="test-order-123",
            status="filled",
        )

        test_session.add(trade)
        test_session.commit()

        # Retrieve trade
        retrieved_trade = (
            test_session.query(Trade).filter(Trade.order_id == "test-order-123").first()
        )
        assert retrieved_trade is not None
        assert retrieved_trade.market == "BTC-EUR"
        assert retrieved_trade.side == "buy"
        assert retrieved_trade.amount == 0.001
        assert retrieved_trade.price == 45000.0
        assert retrieved_trade.status == "filled"
        assert retrieved_trade.created_at is not None

    def test_position_model_creation(self, test_session):
        """Test Position model creation and fields"""
        # Create user and portfolio
        user = User(
            username="testuser", email="test@example.com", hashed_password="hash123"
        )
        test_session.add(user)
        test_session.commit()

        portfolio = Portfolio(
            user_id=user.id, name="Test Portfolio", description="Test"
        )
        test_session.add(portfolio)
        test_session.commit()

        # Create position
        position = Position(
            portfolio_id=portfolio.id,
            symbol="BTC",
            amount=0.001,
            average_price=45000.0,
            current_price=46000.0,
            unrealized_pnl=1.0,
        )

        test_session.add(position)
        test_session.commit()

        # Retrieve position
        retrieved_position = (
            test_session.query(Position).filter(Position.symbol == "BTC").first()
        )
        assert retrieved_position is not None
        assert retrieved_position.symbol == "BTC"
        assert retrieved_position.amount == 0.001
        assert retrieved_position.average_price == 45000.0
        assert retrieved_position.current_price == 46000.0
        assert retrieved_position.unrealized_pnl == 1.0
        # updated_at is only set on updates, not on initial insert
        assert retrieved_position.created_at is not None

    def test_portfolio_positions_relationship(self, test_session):
        """Test Portfolio-Position relationship"""
        # Create user and portfolio
        user = User(
            username="testuser", email="test@example.com", hashed_password="hash123"
        )
        test_session.add(user)
        test_session.commit()

        portfolio = Portfolio(
            user_id=user.id, name="Test Portfolio", description="Test"
        )
        test_session.add(portfolio)
        test_session.commit()

        # Create multiple positions
        position1 = Position(
            portfolio_id=portfolio.id, symbol="BTC", amount=0.001, average_price=45000.0
        )
        position2 = Position(
            portfolio_id=portfolio.id, symbol="ETH", amount=0.1, average_price=3000.0
        )

        test_session.add_all([position1, position2])
        test_session.commit()

        # Test relationships
        assert len(portfolio.positions) == 2
        symbols = [pos.symbol for pos in portfolio.positions]
        assert "BTC" in symbols
        assert "ETH" in symbols

        # Test back reference
        assert position1.portfolio.name == "Test Portfolio"
        assert position2.portfolio.name == "Test Portfolio"

    def test_portfolio_trades_relationship(self, test_session):
        """Test Portfolio-Trade relationship"""
        # Create user and portfolio
        user = User(
            username="testuser", email="test@example.com", hashed_password="hash123"
        )
        test_session.add(user)
        test_session.commit()

        portfolio = Portfolio(
            user_id=user.id, name="Test Portfolio", description="Test"
        )
        test_session.add(portfolio)
        test_session.commit()

        # Create multiple trades
        trade1 = Trade(
            user_id=user.id,
            portfolio_id=portfolio.id,
            exchange="bitvavo",
            market="BTC-EUR",
            side="buy",
            order_type="market",
            amount=0.001,
            price=45000.0,
            order_id="order-1",
        )
        trade2 = Trade(
            user_id=user.id,
            portfolio_id=portfolio.id,
            exchange="bitvavo",
            market="ETH-EUR",
            side="sell",
            order_type="limit",
            amount=0.1,
            price=3000.0,
            order_id="order-2",
        )

        test_session.add_all([trade1, trade2])
        test_session.commit()

        # Test relationships
        assert len(portfolio.trades) == 2
        markets = [trade.market for trade in portfolio.trades]
        assert "BTC-EUR" in markets
        assert "ETH-EUR" in markets

        # Test back reference
        assert trade1.portfolio.name == "Test Portfolio"
        assert trade2.portfolio.name == "Test Portfolio"

    def test_model_string_representations(self, test_session):
        """Test __str__ methods of models"""
        # Create user
        user = User(
            username="testuser", email="test@example.com", hashed_password="hash123"
        )
        test_session.add(user)
        test_session.commit()

        # Create portfolio
        portfolio = Portfolio(
            user_id=user.id, name="Test Portfolio", description="Test"
        )
        test_session.add(portfolio)
        test_session.commit()

        # Create trade
        trade = Trade(
            user_id=user.id,
            portfolio_id=portfolio.id,
            exchange="bitvavo",
            market="BTC-EUR",
            side="buy",
            order_type="market",
            amount=0.001,
            price=45000.0,
            order_id="order-1",
        )
        test_session.add(trade)
        test_session.commit()

        # Test string representations
        assert str(user) == "User(username=testuser)"
        assert str(portfolio) == "Portfolio(name=Test Portfolio)"
        assert str(trade) == "Trade(market=BTC-EUR, side=buy, amount=0.001)"

    def test_user_unique_constraints(self, test_session):
        """Test unique constraints on User model"""
        # Create first user
        user1 = User(
            username="testuser", email="test@example.com", hashed_password="hash123"
        )
        test_session.add(user1)
        test_session.commit()

        # Try to create second user with same username
        user2 = User(
            username="testuser",
            email="different@example.com",
            hashed_password="hash456",
        )
        test_session.add(user2)

        with pytest.raises(Exception):  # Should raise integrity error
            test_session.commit()

        test_session.rollback()

        # Try to create user with same email
        user3 = User(
            username="differentuser",
            email="test@example.com",
            hashed_password="hash789",
        )
        test_session.add(user3)

        with pytest.raises(Exception):  # Should raise integrity error
            test_session.commit()

    def test_cascade_delete_user_portfolios(self, test_session):
        """Test cascade delete when user is deleted"""
        # Create user with portfolio
        user = User(
            username="testuser", email="test@example.com", hashed_password="hash123"
        )
        test_session.add(user)
        test_session.commit()

        portfolio = Portfolio(
            user_id=user.id, name="Test Portfolio", description="Test"
        )
        test_session.add(portfolio)
        test_session.commit()

        # Delete user
        test_session.delete(user)
        test_session.commit()

        # Check that portfolio is also deleted
        remaining_portfolios = test_session.query(Portfolio).all()
        assert len(remaining_portfolios) == 0
