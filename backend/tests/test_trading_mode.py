"""
Tests voor Trading Mode Service en API endpoints
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.trading_mode import TradingMode, trading_mode_service


class TestTradingModeService:
    """Test cases voor TradingModeService"""

    def test_default_dry_run_mode(self):
        """Test dat default mode dry_run is"""
        assert trading_mode_service.get_current_mode() == TradingMode.DRY_RUN
        assert trading_mode_service.is_dry_run_enabled().is_(True)
        assert trading_mode_service.is_live_trading().is_(False)

    def test_mode_switching(self):
        """Test het wisselen van trading modes"""
        # Test demo mode
        trading_mode_service.set_mode(TradingMode.DEMO)
        assert trading_mode_service.get_current_mode() == TradingMode.DEMO
        assert trading_mode_service.is_dry_run_enabled().is_(
            True
        )  # Still dry run in demo

        # Test live mode with forced dry run
        trading_mode_service.set_mode(TradingMode.LIVE, force_dry_run=True)
        assert trading_mode_service.get_current_mode() == TradingMode.LIVE
        assert trading_mode_service.is_dry_run_enabled().is_(True)
        assert trading_mode_service.is_live_trading().is_(False)

    def test_warning_messages(self):
        """Test warning messages voor verschillende modes"""
        trading_mode_service.set_mode(TradingMode.DRY_RUN)
        warning = trading_mode_service.get_mode_warning()
        assert "DRY RUN MODE" in warning

        trading_mode_service.set_mode(TradingMode.DEMO)
        warning = trading_mode_service.get_mode_warning()
        assert "DEMO MODE" in warning

        trading_mode_service.set_mode(TradingMode.LIVE, force_dry_run=True)
        warning = trading_mode_service.get_mode_warning()
        assert "DRY RUN" in warning

    def test_simulate_order_response(self):
        """Test order simulatie"""
        order_data = {
            "market": "BTC-EUR",
            "side": "buy",
            "order_type": "market",
            "amount": 0.001,
        }

        response = trading_mode_service.simulate_order_response(order_data)

        assert response["market"] == "BTC-EUR"
        assert response["side"] == "buy"
        assert response["orderType"] == "market"
        assert response["simulated"].is_(True)
        assert response["status"] == "filled"  # Market orders get filled
        assert "SIM-" in response["orderId"]

    def test_simulate_balance_response(self):
        """Test balance simulatie"""
        balance = trading_mode_service.simulate_balance_response()

        assert len(balance) >= 3  # EUR, BTC, ETH
        assert any(item["symbol"] == "EUR" for item in balance)
        assert any(item["symbol"] == "BTC" for item in balance)
        assert all("available" in item for item in balance)

    @patch("app.services.trading_mode.settings.BITVAVO_API_KEY", "test_key")
    @patch("app.services.trading_mode.settings.BITVAVO_API_SECRET", "test_secret")
    def test_live_trading_validation_success(self):
        """Test successful live trading validation"""
        trading_mode_service.set_mode(TradingMode.LIVE, force_dry_run=False)
        trading_mode_service.dry_run_enabled = False

        can_trade, message = trading_mode_service.validate_live_trading_requirements()
        assert can_trade.is_(True)
        assert "voldaan" in message.lower()

    def test_live_trading_validation_no_credentials(self):
        """Test live trading validation zonder credentials"""
        with patch("app.services.trading_mode.settings.BITVAVO_API_KEY", None):
            can_trade, message = (
                trading_mode_service.validate_live_trading_requirements()
            )
            assert can_trade.is_(False)
            assert "credentials" in message.lower()


class TestTradingModeAPI:
    """Test cases voor Trading Mode API endpoints"""

    def setup_method(self):
        """Setup voor elke test"""
        self.client = TestClient(app)
        # Reset to default mode
        trading_mode_service.set_mode(TradingMode.DRY_RUN, force_dry_run=True)

    def test_get_trading_mode_status(self):
        """Test get trading mode status endpoint"""
        response = self.client.get("/api/v1/trading-mode/status")
        assert response.status_code == 200

        data = response.json()
        assert data["current_mode"] == "dry_run"
        assert data["dry_run_enabled"].is_(True)
        assert data["is_live_trading"].is_(False)
        assert data["warning_message"] is not None

    def test_set_trading_mode_dry_run(self):
        """Test set trading mode naar dry_run"""
        request_data = {"mode": "dry_run", "force_dry_run": False}

        response = self.client.post("/api/v1/trading-mode/set", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["current_mode"] == "dry_run"
        assert data["dry_run_enabled"].is_(True)

    def test_set_trading_mode_demo(self):
        """Test set trading mode naar demo"""
        request_data = {"mode": "demo", "force_dry_run": False}

        response = self.client.post("/api/v1/trading-mode/set", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["current_mode"] == "demo"
        assert data["dry_run_enabled"].is_(True)  # Demo is still dry run

    def test_set_invalid_trading_mode(self):
        """Test set invalid trading mode"""
        request_data = {"mode": "invalid_mode", "force_dry_run": False}

        response = self.client.post("/api/v1/trading-mode/set", json=request_data)
        assert response.status_code == 400
        assert "Invalid trading mode" in response.json()["detail"]

    @patch("app.services.trading_mode.settings.BITVAVO_API_KEY", None)
    def test_set_live_mode_without_credentials(self):
        """Test set live mode zonder API credentials"""
        request_data = {"mode": "live", "force_dry_run": False}

        response = self.client.post("/api/v1/trading-mode/set", json=request_data)
        assert response.status_code == 400
        assert "Cannot enable live trading" in response.json()["detail"]

    def test_enable_dry_run_safety(self):
        """Test emergency dry-run enable"""
        response = self.client.post("/api/v1/trading-mode/enable-dry-run")
        assert response.status_code == 200

        data = response.json()
        assert data["dry_run_enabled"].is_(True)
        assert "enabled" in data["message"].lower()

    def test_validate_live_trading(self):
        """Test live trading validation endpoint"""
        response = self.client.get("/api/v1/trading-mode/validate-live")
        assert response.status_code == 200

        data = response.json()
        assert "can_trade_live" in data
        assert "requirements" in data
        assert "current_mode" in data

    def test_health_check_includes_trading_mode(self):
        """Test dat health check trading mode info bevat"""
        response = self.client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "trading_mode" in data
        assert "mode_warning" in data
        assert data["trading_mode"] == "dry_run"
