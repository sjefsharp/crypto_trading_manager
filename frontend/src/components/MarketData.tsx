import React, { useState, useEffect } from "react";
import axios from "axios";
import { Market, TickerData, CandleData, APIError, InputChangeHandler } from "@/types";

const MarketData: React.FC = () => {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [tickers, setTickers] = useState<TickerData[]>([]);
  const [candles, setCandles] = useState<CandleData[]>([]);
  const [selectedMarket, setSelectedMarket] = useState<string>("BTC-EUR");
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMarkets = async (): Promise<void> => {
      try {
        setLoading(true);
        setError(null);

        const response = await axios.get<{ data: Market[] }>("/api/v1/markets");
        const activeMarkets = response.data.data.filter(
          (market: Market) => market.status === "trading"
        );
        setMarkets(activeMarkets);
      } catch (err) {
        const error = err as APIError;
        setError("Failed to fetch market data: " + (error.message || "Unknown error"));
      } finally {
        setLoading(false);
      }
    };

    fetchMarkets();
  }, []);

  useEffect(() => {
    const fetchTickers = async (): Promise<void> => {
      try {
        const response = await axios.get<{ data: TickerData[] }>("/api/v1/ticker/24hr");
        setTickers(response.data.data);
      } catch (err) {
        console.error("Failed to fetch ticker data:", err);
      }
    };

    fetchTickers();
  }, []);

  const fetchCandleData = async (market: string): Promise<void> => {
    try {
      const response = await axios.get<{ data: CandleData[] }>(`/api/v1/candles/${market}`, {
        params: { interval: "1h", limit: 24 },
      });
      setCandles(response.data.data);
    } catch (err) {
      console.error("Failed to fetch candle data:", err);
    }
  };

  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('nl-NL', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 8,
    }).format(price);
  };

  const formatVolume = (volume: number): string => {
    if (volume >= 1_000_000) {
      return `${(volume / 1_000_000).toFixed(1)}M`;
    } else if (volume >= 1_000) {
      return `${(volume / 1_000).toFixed(1)}K`;
    }
    return volume.toFixed(2);
  };

  const calculatePriceChange = (current: number, high: number, low: number): number => {
    const midPrice = (high + low) / 2;
    return ((current - midPrice) / midPrice) * 100;
  };

  const handleMarketSelect: InputChangeHandler = (e) => {
    const market = e.target.value;
    setSelectedMarket(market);
    fetchCandleData(market);
  };

  if (loading) {
    return (
      <main className="market-data" aria-live="polite">
        <div className="loading-container" role="status" aria-label="Loading market data">
          <div className="spinner" aria-hidden="true"></div>
          <span className="sr-only">Loading market data...</span>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="market-data">
        <div className="error-container" role="alert">
          <h2>Error</h2>
          <p>{error}</p>
          <button 
            className="btn btn--primary"
            onClick={() => window.location.reload()}
            type="button"
          >
            Retry
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="market-data">
      <div className="container">
        <header className="market-data-header">
          <h1>Market Data</h1>
          <p className="subtitle">Real-time cryptocurrency market information</p>
        </header>

        <section className="market-selector card" aria-labelledby="market-selector-heading">
          <h2 id="market-selector-heading" className="sr-only">Select Market</h2>
          <div className="form-group">
            <label htmlFor="market-select" className="form-label">
              Select Market for Detailed View
            </label>
            <select
              id="market-select"
              className="form-select"
              value={selectedMarket}
              onChange={handleMarketSelect}
              aria-describedby="market-select-help"
            >
              {markets
                .filter((m) => m.quote === "EUR")
                .map((market) => (
                  <option key={market.market} value={market.market}>
                    {market.market}
                  </option>
                ))}
            </select>
            <div id="market-select-help" className="form-help text-muted">
              Choose a trading pair to view detailed candle data
            </div>
          </div>
        </section>

        <section className="card" aria-labelledby="ticker-heading">
          <header className="card-header">
            <h2 id="ticker-heading">Live Market Tickers</h2>
            <p className="text-muted">24-hour trading statistics for EUR pairs</p>
          </header>

          <div className="table-container">
            <table role="table" aria-label="Live cryptocurrency market tickers">
              <thead>
                <tr>
                  <th scope="col">Market</th>
                  <th scope="col">Last Price</th>
                  <th scope="col">24h Change</th>
                  <th scope="col">24h Volume</th>
                  <th scope="col">Bid</th>
                  <th scope="col">Ask</th>
                </tr>
              </thead>
              <tbody>
                {tickers
                  .filter((ticker) => ticker.market.includes("EUR"))
                  .map((ticker) => {
                    const priceChange = calculatePriceChange(
                      ticker.last,
                      ticker.high,
                      ticker.low
                    );
                    return (
                      <tr key={ticker.market}>
                        <td>
                          <strong>{ticker.market}</strong>
                        </td>
                        <td>{formatPrice(ticker.last)}</td>
                        <td
                          className={
                            priceChange >= 0 ? "price-positive" : "price-negative"
                          }
                        >
                          <span aria-label={`${priceChange >= 0 ? 'Increased' : 'Decreased'} by ${Math.abs(priceChange).toFixed(2)} percent`}>
                            {priceChange >= 0 ? "+" : ""}{priceChange.toFixed(2)}%
                          </span>
                          <br />
                          <small>
                            H: {formatPrice(ticker.high)} / L: {formatPrice(ticker.low)}
                          </small>
                        </td>
                        <td>{formatVolume(ticker.volume)}</td>
                        <td>{formatPrice(ticker.bid)}</td>
                        <td>{formatPrice(ticker.ask)}</td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
        </section>

        {candles.length > 0 && (
          <section className="card" aria-labelledby="candle-heading">
            <header className="card-header">
              <h2 id="candle-heading">
                24-Hour Candle Data for {selectedMarket}
              </h2>
              <p className="text-muted">Hourly price movements over the last 24 hours</p>
            </header>

            <div className="table-container">
              <table role="table" aria-label={`Hourly candle data for ${selectedMarket}`}>
                <thead>
                  <tr>
                    <th scope="col">Time</th>
                    <th scope="col">Open</th>
                    <th scope="col">High/Low</th>
                    <th scope="col">Close</th>
                    <th scope="col">Volume</th>
                  </tr>
                </thead>
                <tbody>
                  {candles.map((candle, index) => {
                    const date = new Date(candle.timestamp);
                    const isGreen = candle.close >= candle.open;
                    return (
                      <tr key={index}>
                        <td>
                          <time dateTime={date.toISOString()}>
                            {date.toLocaleDateString('nl-NL')} {date.toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' })}
                          </time>
                        </td>
                        <td>{formatPrice(candle.open)}</td>
                        <td>
                          <span className="price-positive">
                            {formatPrice(candle.high)}
                          </span>
                          {" / "}
                          <span className="price-negative">
                            {formatPrice(candle.low)}
                          </span>
                        </td>
                        <td>
                          <span
                            className={isGreen ? "price-positive" : "price-negative"}
                            aria-label={`Close price ${formatPrice(candle.close)}, ${isGreen ? 'higher' : 'lower'} than open`}
                          >
                            {formatPrice(candle.close)}
                          </span>
                        </td>
                        <td>{formatVolume(candle.volume)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </div>
    </main>
  );
};

export default MarketData;
