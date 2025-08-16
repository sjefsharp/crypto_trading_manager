from typing import List

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
async def get_markets():
    """Get all available trading markets"""
    try:
        api = BitvavoAPI()
        markets_data = await api.get_markets()

        markets = []
        for market in markets_data:
            markets.append(
                MarketInfo(
                    market=market["market"],
                    status=market["status"],
                    base=market["base"],
                    quote=market["quote"],
                    pricePrecision=market["pricePrecision"],
                    minOrderInQuoteAsset=market["minOrderInQuoteAsset"],
                    minOrderInBaseAsset=market["minOrderInBaseAsset"],
                    orderTypes=market["orderTypes"],
                )
            )

        return markets
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ticker", response_model=List[TickerInfo])
async def get_all_tickers():
    """Get ticker information for all markets"""
    try:
        api = BitvavoAPI()
        ticker_data = await api.get_ticker()

        tickers = []
        for ticker in ticker_data:
            tickers.append(
                TickerInfo(
                    market=ticker["market"],
                    last=float(ticker["last"]),
                    high=float(ticker["high"]),
                    low=float(ticker["low"]),
                    volume=float(ticker["volume"]),
                    volumeQuote=float(ticker["volumeQuote"]),
                    bid=float(ticker["bid"]),
                    ask=float(ticker["ask"]),
                    timestamp=int(ticker["timestamp"]),
                )
            )

        return tickers
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ticker/{market}", response_model=TickerInfo)
async def get_ticker(market: str):
    """Get ticker information for a specific market"""
    try:
        api = BitvavoAPI()
        ticker_data = await api.get_ticker(market)

        return TickerInfo(
            market=ticker_data["market"],
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
async def get_orderbook(market: str, depth: int = 50):
    """Get orderbook for a specific market"""
    try:
        api = BitvavoAPI()
        orderbook = await api.get_orderbook(market, depth)
        return orderbook
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trades/{market}")
async def get_recent_trades(market: str, limit: int = 100):
    """Get recent trades for a market"""
    try:
        api = BitvavoAPI()
        trades = await api.get_trades(market, limit)
        return trades
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/candles/{market}", response_model=List[CandleData])
async def get_candles(market: str, interval: str = "1h", limit: int = 100):
    """Get candlestick data for a market

    Available intervals: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
    """
    try:
        api = BitvavoAPI()
        candles_data = await api.get_candles(market, interval, limit)

        candles = []
        for candle in candles_data:
            candles.append(
                CandleData(
                    timestamp=int(candle[0]),
                    open=float(candle[1]),
                    high=float(candle[2]),
                    low=float(candle[3]),
                    close=float(candle[4]),
                    volume=float(candle[5]),
                )
            )

        return candles
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/price/{market}")
async def get_current_price(market: str):
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
