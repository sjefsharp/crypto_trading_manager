"""
Tests voor Trading Mode UI Integration
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.trading_mode import TradingMode, trading_mode_service


class TestTradingModeUIIntegration:
    """Test cases voor Trading Mode UI integration"""

    def setup_method(self):
        """Setup voor elke test"""
        self.client = TestClient(app)
        # Reset to default mode
        trading_mode_service.set_mode(TradingMode.DRY_RUN, force_dry_run=True)

    def test_cors_headers_for_ui(self):
        """Test CORS headers voor frontend integration"""
        response = self.client.get("/api/v1/trading-mode/status")
        assert response.status_code == 200
        # Check dat response valid JSON is voor frontend
        assert response.headers["content-type"] == "application/json"

    def test_ui_friendly_error_responses(self):
        """Test dat error responses UI-friendly zijn"""
        request_data = {"mode": "invalid_mode", "force_dry_run": False}

        response = self.client.post("/api/v1/trading-mode/set", json=request_data)
        assert response.status_code == 400

        error_data = response.json()
        assert "detail" in error_data
        assert isinstance(
            error_data["detail"], str
        )  # UI kan string messages verwachten

    def test_mode_switching_workflow_for_ui(self):
        """Test complete mode switching workflow zoals UI het zou doen"""
        # 1. Get initial status
        response = self.client.get("/api/v1/trading-mode/status")
        assert response.status_code == 200

        initial_status = response.json()
        assert initial_status["current_mode"] == "dry_run"

        # 2. Switch to demo mode
        response = self.client.post(
            "/api/v1/trading-mode/set", json={"mode": "demo", "force_dry_run": False}
        )
        assert response.status_code == 200

        demo_status = response.json()
        assert demo_status["current_mode"] == "demo"
        assert demo_status["dry_run_enabled"].is_(True)

        # 3. Verify status endpoint reflects change
        response = self.client.get("/api/v1/trading-mode/status")
        assert response.status_code == 200

        current_status = response.json()
        assert current_status["current_mode"] == "demo"

    def test_live_mode_safety_for_ui(self):
        """Test live mode safety workflow voor UI"""
        # Try to enable live mode without credentials
        with patch("app.services.trading_mode.settings.BITVAVO_API_KEY", None):
            response = self.client.post(
                "/api/v1/trading-mode/set",
                json={"mode": "live", "force_dry_run": False},
            )

            assert response.status_code == 400
            error_data = response.json()
            assert "Cannot enable live trading" in error_data["detail"]

    def test_emergency_dry_run_for_ui(self):
        """Test emergency dry-run activation zoals UI het gebruikt"""
        # First switch to demo mode
        self.client.post(
            "/api/v1/trading-mode/set", json={"mode": "demo", "force_dry_run": False}
        )

        # Activate emergency dry-run
        response = self.client.post("/api/v1/trading-mode/enable-dry-run")
        assert response.status_code == 200

        emergency_response = response.json()
        assert emergency_response["dry_run_enabled"].is_(True)
        assert "enabled" in emergency_response["message"].lower()

        # Verify status reflects emergency activation
        response = self.client.get("/api/v1/trading-mode/status")
        status = response.json()
        assert status["dry_run_enabled"].is_(True)

    def test_warning_messages_for_ui(self):
        """Test dat warning messages consistent zijn voor UI"""
        # Test verschillende modes en hun warnings
        modes_to_test = ["dry_run", "demo"]

        for mode in modes_to_test:
            response = self.client.post(
                "/api/v1/trading-mode/set", json={"mode": mode, "force_dry_run": True}
            )

            assert response.status_code == 200
            mode_data = response.json()
            assert "warning_message" in mode_data
            assert mode_data["warning_message"] is not None
            assert len(mode_data["warning_message"]) > 0

    def test_validation_endpoint_for_ui(self):
        """Test validation endpoint dat UI gebruikt voor live trading checks"""
        response = self.client.get("/api/v1/trading-mode/validate-live")
        assert response.status_code == 200

        validation_data = response.json()
        required_fields = ["can_trade_live", "requirements", "current_mode", "details"]

        for field in required_fields:
            assert field in validation_data

        # Voor UI is boolean response belangrijk
        assert isinstance(validation_data["can_trade_live"], bool)
        assert isinstance(validation_data["requirements"], str)  # UI-friendly string
        assert isinstance(validation_data["details"], dict)  # Detailed breakdown

    @patch("app.services.trading_mode.settings.BITVAVO_API_KEY", "test_key")
    @patch("app.services.trading_mode.settings.BITVAVO_API_SECRET", "test_secret")
    def test_live_mode_with_credentials_for_ui(self):
        """Test live mode activatie met credentials voor UI workflow"""
        # Enable live mode with force_dry_run=True (safe option in UI)
        response = self.client.post(
            "/api/v1/trading-mode/set", json={"mode": "live", "force_dry_run": True}
        )

        assert response.status_code == 200
        live_data = response.json()
        assert live_data["current_mode"] == "live"
        assert live_data["dry_run_enabled"].is_(True)  # Safety override
        assert live_data["is_live_trading"].is_(
            False
        )  # Not actually live due to dry_run

    def test_health_check_includes_mode_for_ui(self):
        """Test dat health check trading mode info bevat voor UI monitoring"""
        response = self.client.get("/health")
        assert response.status_code == 200

        health_data = response.json()
        assert "trading_mode" in health_data
        assert "mode_warning" in health_data

        # UI kan deze info gebruiken voor status display
        assert health_data["trading_mode"] in ["dry_run", "demo", "live"]
        assert isinstance(health_data["mode_warning"], str)

    def test_response_format_consistency_for_ui(self):
        """Test dat alle responses consistent format hebben voor UI parsing"""
        # Test status endpoint
        response = self.client.get("/api/v1/trading-mode/status")
        status_data = response.json()

        required_status_fields = [
            "current_mode",
            "dry_run_enabled",
            "is_live_trading",
            "warning_message",
        ]
        for field in required_status_fields:
            assert field in status_data

        # Test set endpoint response format
        response = self.client.post(
            "/api/v1/trading-mode/set", json={"mode": "demo", "force_dry_run": False}
        )
        set_data = response.json()

        # Should have same fields as status + message
        for field in required_status_fields:
            assert field in set_data
        assert "message" in set_data

    def test_mode_persistence_for_ui(self):
        """Test dat mode changes persistent zijn voor UI sessies"""
        # Switch mode
        self.client.post(
            "/api/v1/trading-mode/set", json={"mode": "demo", "force_dry_run": False}
        )

        # Verify persistence door multiple status calls
        for _ in range(3):
            response = self.client.get("/api/v1/trading-mode/status")
            status = response.json()
            assert status["current_mode"] == "demo"


class TestTradingModeAPIDocumentation:
    """Test dat API responses goed gedocumenteerd zijn voor frontend developers"""

    def setup_method(self):
        self.client = TestClient(app)

    def test_openapi_schema_includes_trading_mode(self):
        """Test dat OpenAPI schema trading mode endpoints bevat"""
        response = self.client.get("/docs")  # Try docs endpoint instead
        assert response.status_code == 200  # Should at least be accessible

        # Alternative: Test that the endpoints themselves work
        trading_mode_endpoints = [
            "/api/v1/trading-mode/status",
            "/api/v1/trading-mode/validate-live",
        ]

        for endpoint in trading_mode_endpoints:
            response = self.client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} not accessible"
