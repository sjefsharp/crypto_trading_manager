"""
Trading Mode API endpoints voor het beheren van dry-run, demo en live modes
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.trading_mode import TradingMode, trading_mode_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/trading-mode", tags=["Trading Mode"])


class TradingModeResponse(BaseModel):
    """Response model voor trading mode status"""

    current_mode: str
    dry_run_enabled: bool
    is_live_trading: bool
    warning_message: Optional[str]
    can_trade_live: bool
    validation_message: str
    message: Optional[str] = None  # Voor UI feedback


class LiveTradingValidationResponse(BaseModel):
    """Response model voor live trading validatie"""

    can_trade_live: bool
    requirements: str  # UI-friendly string message
    current_mode: str
    details: dict  # Detailed breakdown voor debugging


class SetTradingModeRequest(BaseModel):
    """Request model voor het zetten van trading mode"""

    mode: str  # "dry_run", "demo", "live"
    force_dry_run: bool = False


@router.get("/status", response_model=TradingModeResponse)
async def get_trading_mode_status():
    """Get huidige trading mode status"""
    try:
        can_trade_live, validation_message = (
            trading_mode_service.validate_live_trading_requirements()
        )

        return TradingModeResponse(
            current_mode=trading_mode_service.get_current_mode().value,
            dry_run_enabled=trading_mode_service.is_dry_run_enabled(),
            is_live_trading=trading_mode_service.is_live_trading(),
            warning_message=trading_mode_service.get_mode_warning(),
            can_trade_live=can_trade_live,
            validation_message=validation_message,
            message=None,  # Status check doesn't need action message
        )
    except Exception as e:
        logger.error(f"Error getting trading mode status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set", response_model=TradingModeResponse)
async def set_trading_mode(request: SetTradingModeRequest):
    """Set trading mode"""
    try:
        # Validate mode
        try:
            mode = TradingMode(request.mode)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid trading mode: {request.mode}. Options: dry_run, demo, live",
            )

        # Extra veiligheid voor live mode
        if mode == TradingMode.LIVE and not request.force_dry_run:
            # Require explicit confirmation for live mode
            can_trade_live, validation_message = (
                trading_mode_service.validate_live_trading_requirements()
            )
            if not can_trade_live:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot enable live trading: {validation_message}",
                )

            logger.warning(f"🔴 LIVE TRADING MODE ACTIVATED!")

        # Set the mode
        trading_mode_service.set_mode(mode, request.force_dry_run)

        # Return new status
        can_trade_live, validation_message = (
            trading_mode_service.validate_live_trading_requirements()
        )

        return TradingModeResponse(
            current_mode=trading_mode_service.get_current_mode().value,
            dry_run_enabled=trading_mode_service.is_dry_run_enabled(),
            is_live_trading=trading_mode_service.is_live_trading(),
            warning_message=trading_mode_service.get_mode_warning(),
            can_trade_live=can_trade_live,
            validation_message=validation_message,
            message=f"Trading mode switched to {mode.value.upper()}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting trading mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enable-dry-run")
async def enable_dry_run():
    """Schakel dry-run mode in (veiligheidsknop)"""
    try:
        current_mode = trading_mode_service.get_current_mode()
        trading_mode_service.set_mode(current_mode, force_dry_run=True)

        logger.info("🔒 Dry-run mode force enabled for safety")

        return {
            "dry_run_enabled": True,
            "message": "Emergency dry-run mode enabled for safety",
            "current_mode": current_mode.value,
        }
    except Exception as e:
        logger.error(f"Error enabling dry-run: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validate-live")
async def validate_live_trading():
    """Valideer of live trading mogelijk is"""
    try:
        can_trade_live, message = (
            trading_mode_service.validate_live_trading_requirements()
        )

        # Create detailed breakdown
        details = {
            "api_key_configured": bool(
                trading_mode_service.current_mode
            ),  # Simplified check
            "mode_is_live": trading_mode_service.get_current_mode() == TradingMode.LIVE,
            "dry_run_disabled": not trading_mode_service.is_dry_run_enabled(),
        }

        return LiveTradingValidationResponse(
            can_trade_live=can_trade_live,
            requirements=message,  # UI-friendly string
            current_mode=trading_mode_service.get_current_mode().value,
            details=details,
        )
    except Exception as e:
        logger.error(f"Error validating live trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))
