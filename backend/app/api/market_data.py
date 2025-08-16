from typing import Any, Dict, List, cast

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.bitvavo_api_secure import BitvavoAPI

router = APIRouter()


# Pydantic models
class MarketInfo(BaseModel):
    market: str
    status: str
    base: str
    quote: str
    pricePrecision: int
    minOrderInQuoteAsset: str
    minOrderInBaseAsset: str
    orderTypes: List[str]


class TickerInfo(BaseModel):
    market: str
    last: float
    high: float
    low: float
    volume: float
    volumeQuote: float
    bid: float
    ask: float
    timestamp: int


class CandleData(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


@router.get("/markets", response_model=List[MarketInfo])
async def get_markets() -> List[MarketInfo]:
    """Get all available trading markets"""
    try:
        api = BitvavoAPI()
        markets_data = await api.get_markets()

        markets: List[MarketInfo] = []
        for market_data in markets_data:
            market_dict = cast(Dict[str, Any], market_data)
            markets.append(
                MarketInfo(
                    market=str(market_dict.get("market", "")),
                    status=str(market_dict.get("status", "")),
                    base=str(market_dict.get("base", "")),
                    quote=str(market_dict.get("quote", "")),
                    pricePrecision=int(market_dict.get("pricePrecision", 0)),
                    minOrderInQuoteAsset=str(
                        market_dict.get("minOrderInQuoteAsset", "")
                    ),
                    minOrderInBaseAsset=str(market_dict.get("minOrderInBaseAsset", "")),
                    orderTypes=(
                        cast(List[str], market_dict.get("orderTypes", []))
                        if isinstance(market_dict.get("orderTypes"), list)
                        else []
                    ),
                )
            )

        return markets
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ticker", response_model=List[TickerInfo])
async def get_all_tickers() -> List[TickerInfo]:
    """Get ticker information for all markets"""
    try:
        api = BitvavoAPI()
        ticker_data = await api.get_ticker()

        tickers: List[TickerInfo] = []
        for ticker in ticker_data:
            ticker_dict = cast(Dict[str, Any], ticker)
            tickers.append(
                TickerInfo(
                    market=str(ticker_dict["market"]),
                    last=float(ticker_dict["last"]),
                    high=float(ticker_dict["high"]),
                    low=float(ticker_dict["low"]),
                    volume=float(ticker_dict["volume"]),
                    volumeQuote=float(ticker_dict["volumeQuote"]),
                    bid=float(ticker_dict["bid"]),
                    ask=float(ticker_dict["ask"]),
                    timestamp=int(ticker_dict["timestamp"]),
                )
            )

        return tickers
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ticker/{market}", response_model=TickerInfo)
async def get_ticker(market: str) -> TickerInfo:
    """Get ticker information for a specific market"""
    try:
        api = BitvavoAPI()
        ticker_data = await api.get_ticker(market)

        return TickerInfo(
            market=str(ticker_data["market"]),
            last=float(ticker_data["last"]),
            high=float(ticker_data["high"]),
            low=float(ticker_data["low"]),
            volume=float(ticker_data["volume"]),
            volumeQuote=float(ticker_data["volumeQuote"]),
            bid=float(ticker_data["bid"]),
            ask=float(ticker_data["ask"]),
            timestamp=int(ticker_data["timestamp"]),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orderbook/{market}")
async def get_orderbook(market: str, depth: int = 50) -> Dict[str, Any]:
    """Get orderbook for a specific market"""
    try:
        async with BitvavoAPI() as api:
            # Use available ticker or market depth data instead
            ticker = await api.get_ticker(market)
            return {"market": market, "ticker": ticker, "depth": depth}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trades/{market}")
async def get_recent_trades(market: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get recent trades for a market"""
    try:
        api = BitvavoAPI()
        trades = await api.get_trades(market, limit)
        return cast(List[Dict[str, Any]], trades)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/candles/{market}", response_model=List[CandleData])
async def get_candles(
    market: str, interval: str = "1h", limit: int = 100
) -> List[CandleData]:
    """Get candlestick data for a market

    Available intervals: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
    """
    try:
        api = BitvavoAPI()
        candles_data = await api.get_candles(market, interval, limit)

        candles: List[CandleData] = []
        for candle in candles_data:
            candle_list = cast(List[Any], candle)
            candles.append(
                CandleData(
                    timestamp=int(candle_list[0]),
                    open=float(candle_list[1]),
                    high=float(candle_list[2]),
                    low=float(candle_list[3]),
                    close=float(candle_list[4]),
                    volume=float(candle_list[5]),
                )
            )

        return candles
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/price/{market}")
async def get_current_price(market: str) -> Dict[str, Any]:
    """Get current price for a market"""
    try:
        api = BitvavoAPI()
        ticker = await api.get_ticker(market)

        return {
            "market": market,
            "price": float(ticker["last"]),
            "timestamp": int(ticker["timestamp"]),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
