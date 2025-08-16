"""
Simulated trading mode service voor demo/dry-run functionaliteit
"""

import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class TradingMode(Enum):
    """Trading mode enum"""

    DRY_RUN = "dry_run"
    DEMO = "demo"
    LIVE = "live"


class TradingModeService:
    """Service voor het beheren van trading modes en simulatie van trades"""

    def __init__(self):
        self.current_mode = TradingMode(settings.TRADING_MODE)
        self.dry_run_enabled = settings.DRY_RUN_ENABLED

    def get_current_mode(self) -> TradingMode:
        """Get huidige trading mode"""
        return self.current_mode

    def is_dry_run_enabled(self) -> bool:
        """Check of dry run mode actief is"""
        return self.dry_run_enabled or self.current_mode != TradingMode.LIVE

    def is_live_trading(self) -> bool:
        """Check of live trading actief is"""
        return self.current_mode == TradingMode.LIVE and not self.dry_run_enabled

    def set_mode(self, mode: TradingMode, force_dry_run: bool = False) -> None:
        """Set trading mode"""
        self.current_mode = mode
        if force_dry_run:
            self.dry_run_enabled = True
        logger.info(
            f"Trading mode set to: {mode.value}, dry_run: {self.dry_run_enabled}"
        )

    def simulate_order_response(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simuleer een order response voor dry-run/demo mode"""
        order_id = f"SIM-{uuid.uuid4().hex[:8].upper()}"

        # Simuleer verschillende order statuses op basis van parameters
        if order_data.get("order_type") == "market":
            status = "filled"
            filled_quantity = order_data.get("amount", 0)
            filled_price = order_data.get("price", 45000.0)  # Default simulatie prijs
        else:
            status = "open"
            filled_quantity = 0
            filled_price = None

        simulated_response = {
            "orderId": order_id,
            "market": order_data.get("market", "BTC-EUR"),
            "side": order_data.get("side", "buy"),
            "orderType": order_data.get("order_type", "market"),
            "amount": str(order_data.get("amount", 0)),
            "price": (
                str(order_data.get("price", 0)) if order_data.get("price") else None
            ),
            "status": status,
            "filledAmount": str(filled_quantity),
            "filledPrice": str(filled_price) if filled_price else None,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "fee": "0.0025",  # Simuleer 0.25% fee
            "feeCurrency": "EUR",
            "settlement": "instant",
            # Dry run indicator
            "simulated": True,
            "trading_mode": self.current_mode.value,
        }

        logger.info(
            f"[{self.current_mode.value.upper()}] Simulated order: {order_id} - {order_data}"
        )

        return simulated_response

    def simulate_balance_response(self) -> List[Dict[str, str]]:
        """Simuleer account balance voor dry-run/demo mode"""
        simulated_balance = [
            {"symbol": "EUR", "available": "10000.00", "inOrder": "0.00"},
            {"symbol": "BTC", "available": "0.1", "inOrder": "0.0"},
            {"symbol": "ETH", "available": "2.5", "inOrder": "0.0"},
        ]

        logger.info(f"[{self.current_mode.value.upper()}] Simulated balance retrieved")
        return simulated_balance

    def get_mode_warning(self) -> Optional[str]:
        """Get waarschuwing text voor huidige mode"""
        if self.current_mode == TradingMode.DRY_RUN:
            return "⚠️ DRY RUN MODE - Geen echte trades worden uitgevoerd"
        elif self.current_mode == TradingMode.DEMO:
            return "🧪 DEMO MODE - Trades worden gesimuleerd met demo data"
        elif self.current_mode == TradingMode.LIVE and self.dry_run_enabled:
            return "🔒 LIVE MODE met DRY RUN - Veiligheidslock actief"
        elif self.current_mode == TradingMode.LIVE:
            return "🔴 LIVE TRADING MODE - Echte trades worden uitgevoerd!"
        return None

    def validate_live_trading_requirements(self) -> tuple[bool, str]:
        """Valideer of live trading mogelijk is"""
        if not settings.BITVAVO_API_KEY or not settings.BITVAVO_API_SECRET:
            return False, "API credentials niet geconfigureerd"

        if self.current_mode != TradingMode.LIVE:
            return False, f"Trading mode is {self.current_mode.value}, niet live"

        if self.dry_run_enabled:
            return False, "Dry run mode is nog steeds actief"

        return True, "Live trading requirements voldaan"


# Global instance
trading_mode_service = TradingModeService()
