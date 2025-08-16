import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock, AsyncMock


class TestPortfolioOperations:
    """Test cases for portfolio operations and calculations"""
    
    def test_calculate_portfolio_performance(self):
        """Test portfolio performance calculation"""
        from app.services.portfolio_service import calculate_portfolio_performance
        
        # Mock portfolio data
        portfolio_data = {
            "initial_balance": 10000.0,
            "current_balance": 12000.0,
            "positions": [
                {
                    "symbol": "BTC",
                    "amount": 0.1,
                    "average_price": 40000.0,
                    "current_price": 45000.0
                },
                {
                    "symbol": "ETH", 
                    "amount": 2.0,
                    "average_price": 2500.0,
                    "current_price": 3000.0
                }
            ]
        }
        
        performance = calculate_portfolio_performance(portfolio_data)
        
        # Check calculated values
        assert performance["total_return_percentage"] > 0
        assert performance["unrealized_pnl"] > 0
        assert "positions_performance" in performance
        assert len(performance["positions_performance"]) == 2
    
    def test_update_portfolio_positions(self):
        """Test portfolio position updates"""
        from app.services.portfolio_service import update_portfolio_positions
        
        # Mock existing positions
        existing_positions = [
            {"symbol": "BTC", "amount": 0.1, "average_price": 40000.0},
            {"symbol": "ETH", "amount": 1.0, "average_price": 2500.0}
        ]
        
        # Mock new trade
        new_trade = {
            "symbol": "BTC",
            "side": "buy",
            "amount": 0.05,
            "price": 45000.0
        }
        
        updated_positions = update_portfolio_positions(existing_positions, new_trade)
        
        # BTC position should be updated
        btc_position = next(pos for pos in updated_positions if pos["symbol"] == "BTC")
        assert abs(btc_position["amount"] - 0.15) < 1e-10  # Use floating point tolerance
        
        # Average price should be recalculated
        expected_avg_price = ((0.1 * 40000.0) + (0.05 * 45000.0)) / 0.15
        assert abs(btc_position["average_price"] - expected_avg_price) < 0.01
    
    def test_calculate_position_pnl(self):
        """Test position P&L calculation"""
        from app.services.portfolio_service import calculate_position_pnl
        
        position = {
            "symbol": "BTC",
            "amount": 0.1,
            "average_price": 40000.0,
            "current_price": 45000.0
        }
        
        pnl = calculate_position_pnl(position)
        
        expected_pnl = 0.1 * (45000.0 - 40000.0)  # 500.0
        assert pnl["unrealized_pnl"] == expected_pnl
        assert pnl["percentage_change"] == 12.5  # 5000/40000 * 100
        assert pnl["market_value"] == 4500.0  # 0.1 * 45000
    
    def test_rebalance_portfolio_suggestions(self):
        """Test portfolio rebalancing suggestions"""
        from app.services.portfolio_service import get_rebalance_suggestions
        
        portfolio = {
            "total_value": 10000.0,
            "positions": [
                {"symbol": "BTC", "market_value": 7000.0},  # 70%
                {"symbol": "ETH", "market_value": 2000.0},  # 20%
                {"symbol": "ADA", "market_value": 1000.0}   # 10%
            ]
        }
        
        target_allocation = {
            "BTC": 0.5,  # 50%
            "ETH": 0.3,  # 30%
            "ADA": 0.2   # 20%
        }
        
        suggestions = get_rebalance_suggestions(portfolio, target_allocation)
        
        # Should suggest selling BTC and buying ETH/ADA
        assert any(s["action"] == "sell" and s["symbol"] == "BTC" for s in suggestions)
        assert any(s["action"] == "buy" and s["symbol"] == "ETH" for s in suggestions)
        assert any(s["action"] == "buy" and s["symbol"] == "ADA" for s in suggestions)


class TestTradingLogic:
    """Test cases for trading logic and order management"""
    
    def test_validate_order_size(self):
        """Test order size validation"""
        from app.services.trading_service import validate_order_size
        
        # Test minimum order size
        result = validate_order_size("BTC-EUR", 0.00001)  # Below minimum
        assert result["is_valid"] is False
        assert "minimum" in result["error"].lower()
        
        # Test valid order size
        result = validate_order_size("BTC-EUR", 0.001)  # Valid size
        assert result["is_valid"] is True
        assert result["error"] is None
    
    def test_calculate_order_fees(self):
        """Test trading fee calculation"""
        from app.services.trading_service import calculate_order_fees
        
        order = {
            "market": "BTC-EUR",
            "side": "buy",
            "amount": 0.1,
            "price": 45000.0
        }
        
        fees = calculate_order_fees(order)
        
        # Standard Bitvavo fee is 0.25%
        expected_fee = 0.1 * 45000.0 * 0.0025  # 11.25 EUR
        assert abs(fees["trading_fee"] - expected_fee) < 0.01
        assert fees["total_cost"] > fees["base_cost"]
    
    def test_check_sufficient_balance(self):
        """Test balance sufficiency check"""
        from app.services.trading_service import check_sufficient_balance
        
        balance = [
            {"symbol": "EUR", "available": 5000.0},
            {"symbol": "BTC", "available": 0.1}
        ]
        
        # Test buying with sufficient EUR balance
        order = {
            "market": "BTC-EUR",
            "side": "buy",
            "amount": 0.001,
            "price": 45000.0
        }
        
        result = check_sufficient_balance(balance, order)
        assert result["sufficient"] is True
        
        # Test buying with insufficient EUR balance
        order["amount"] = 1.0  # Would cost 45000 EUR
        result = check_sufficient_balance(balance, order)
        assert result["sufficient"] is False
        assert "insufficient" in result["message"].lower()
    
    def test_calculate_stop_loss_order(self):
        """Test stop loss order generation"""
        from app.services.trading_service import generate_stop_loss_order
        
        main_order = {
            "market": "BTC-EUR",
            "side": "buy",
            "amount": 0.1,
            "price": 45000.0
        }
        
        stop_loss_order = generate_stop_loss_order(main_order, stop_loss_percentage=0.05)
        
        assert stop_loss_order["market"] == "BTC-EUR"
        assert stop_loss_order["side"] == "sell"  # Opposite of main order
        assert stop_loss_order["amount"] == 0.1
        assert stop_loss_order["orderType"] == "stopLoss"
        assert stop_loss_order["triggerPrice"] == 42750.0  # 5% below 45000
    
    def test_calculate_take_profit_order(self):
        """Test take profit order generation"""
        from app.services.trading_service import generate_take_profit_order
        
        main_order = {
            "market": "BTC-EUR",
            "side": "buy",
            "amount": 0.1,
            "price": 45000.0
        }
        
        take_profit_order = generate_take_profit_order(main_order, take_profit_percentage=0.10)
        
        assert take_profit_order["market"] == "BTC-EUR"
        assert take_profit_order["side"] == "sell"  # Opposite of main order
        assert take_profit_order["amount"] == 0.1
        assert take_profit_order["orderType"] == "limit"
        assert abs(take_profit_order["price"] - 49500.0) < 0.01  # 10% above 45000 with tolerance


class TestMarketDataProcessing:
    """Test cases for market data processing and analysis"""
    
    def test_process_ticker_data(self):
        """Test ticker data processing"""
        from app.services.market_service import process_ticker_data
        
        raw_ticker = {
            "market": "BTC-EUR",
            "price": "45000.00",
            "high": "46000.00",
            "low": "44000.00",
            "volume": "123.45",
            "bid": "44950.00",
            "ask": "45050.00"
        }
        
        processed = process_ticker_data(raw_ticker)
        
        # Should convert strings to floats
        assert processed["price"] == 45000.0
        assert processed["high"] == 46000.0
        assert processed["volume"] == 123.45
        
        # Should calculate spread
        assert processed["spread"] == 100.0  # 45050 - 44950
        assert processed["spread_percentage"] > 0
    
    def test_process_candle_data(self):
        """Test candlestick data processing"""
        from app.services.market_service import process_candle_data
        
        raw_candles = [
            [1692115200000, "45000.00", "45100.00", "44900.00", "45050.00", "10.5"],
            [1692118800000, "45050.00", "45200.00", "45000.00", "45150.00", "8.2"]
        ]
        
        processed = process_candle_data(raw_candles)
        
        assert len(processed) == 2
        
        # Check first candle
        first_candle = processed[0]
        assert first_candle["open"] == 45000.0
        assert first_candle["high"] == 45100.0
        assert first_candle["low"] == 44900.0
        assert first_candle["close"] == 45050.0
        assert first_candle["volume"] == 10.5
        assert "timestamp" in first_candle
    
    def test_calculate_price_change(self):
        """Test price change calculation"""
        from app.services.market_service import calculate_price_change
        
        current_price = 45000.0
        previous_price = 43000.0
        
        change_data = calculate_price_change(current_price, previous_price)
        
        assert change_data["absolute_change"] == 2000.0
        assert change_data["percentage_change"] == pytest.approx(4.65, rel=1e-2)  # 2000/43000 * 100
        assert change_data["direction"] == "up"
    
    def test_detect_price_alerts(self):
        """Test price alert detection"""
        from app.services.market_service import check_price_alerts
        
        alerts = [
            {"market": "BTC-EUR", "condition": "above", "price": 44000.0, "active": True},
            {"market": "BTC-EUR", "condition": "below", "price": 44000.0, "active": True}  # Set to same price so only "above" triggers
        ]
        
        current_price = 45000.0
        
        triggered_alerts = check_price_alerts(alerts, "BTC-EUR", current_price)
        
        # Should trigger only the "above 44000" alert
        assert len(triggered_alerts) == 1
        assert triggered_alerts[0]["condition"] == "above"
        assert triggered_alerts[0]["price"] == 44000.0


class TestRiskManagement:
    """Test cases for risk management features"""
    
    def test_calculate_position_risk(self):
        """Test position risk calculation"""
        from app.services.risk_service import calculate_position_risk
        
        position = {
            "symbol": "BTC",
            "amount": 0.1,
            "average_price": 40000.0,
            "current_price": 45000.0
        }
        
        portfolio_value = 10000.0
        portfolio_balance = 10000.0  # Add missing parameter
        
        risk_metrics = calculate_position_risk(position, portfolio_value, portfolio_balance)
        
        assert "position_size_percentage" in risk_metrics
        assert "unrealized_pnl_percentage" in risk_metrics
        assert "risk_score" in risk_metrics
        
        # Position value should be 4500 (0.1 * 45000), so 45% of portfolio
        assert risk_metrics["position_size_percentage"] == 45.0
    
    def test_validate_order_risk(self):
        """Test order risk validation"""
        from app.services.risk_service import validate_order_risk
        
        order = {
            "market": "BTC-EUR",
            "side": "buy",
            "amount": 0.5,  # Large order
            "price": 45000.0
        }
        
        portfolio_value = 10000.0
        risk_limits = {
            "max_position_size_percentage": 20.0,
            "max_order_value": 5000.0
        }
        
        risk_check = validate_order_risk(order, portfolio_value, risk_limits)
        
        # Should fail risk checks due to large position size
        assert risk_check["approved"] is False
        assert "risk" in risk_check["reason"].lower()
    
    def test_calculate_portfolio_risk_score(self):
        """Test portfolio risk score calculation"""
        from app.services.risk_service import calculate_portfolio_risk_score
        
        portfolio = {
            "positions": [
                {"symbol": "BTC", "market_value": 5000.0, "volatility": 0.8},
                {"symbol": "ETH", "market_value": 3000.0, "volatility": 0.6},
                {"symbol": "EUR", "market_value": 2000.0, "volatility": 0.01}
            ],
            "total_value": 10000.0
        }
        
        risk_score = calculate_portfolio_risk_score(portfolio)
        
        assert 0 <= risk_score <= 100
        assert isinstance(risk_score, float)
        
        # Higher crypto allocation should result in higher risk score
        assert risk_score > 50  # With 80% in crypto, should be risky
