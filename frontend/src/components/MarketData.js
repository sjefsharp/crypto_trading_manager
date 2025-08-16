import React, { useState, useEffect } from "react";
import axios from "axios";

const MarketData = () => {
  const [markets, setMarkets] = useState([]);
  const [tickers, setTickers] = useState([]);
  const [selectedMarket, setSelectedMarket] = useState("BTC-EUR");
  const [candleData, setCandleData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMarketData();
    const interval = setInterval(fetchTickers, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedMarket) {
      fetchCandleData(selectedMarket);
    }
  }, [selectedMarket]);

  const fetchMarketData = async () => {
    try {
      setLoading(true);
      const [marketsResponse, tickersResponse] = await Promise.all([
        axios.get("/api/v1/market/markets"),
        axios.get("/api/v1/market/ticker"),
      ]);

      const activeMarkets = marketsResponse.data.filter(
        (market) => market.status === "trading"
      );
      setMarkets(activeMarkets);
      setTickers(tickersResponse.data);
    } catch (err) {
      setError("Failed to fetch market data: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchTickers = async () => {
    try {
      const response = await axios.get("/api/v1/market/ticker");
      setTickers(response.data);
    } catch (err) {
      console.error("Error updating tickers:", err);
    }
  };

  const fetchCandleData = async (market) => {
    try {
      const response = await axios.get(
        `/api/v1/market/candles/${market}?interval=1h&limit=24`
      );
      setCandleData(response.data);
    } catch (err) {
      console.error("Error fetching candle data:", err);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat("nl-NL", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 2,
      maximumFractionDigits: 6,
    }).format(price);
  };

  const formatVolume = (volume) => {
    if (volume >= 1000000) {
      return (volume / 1000000).toFixed(2) + "M";
    } else if (volume >= 1000) {
      return (volume / 1000).toFixed(2) + "K";
    }
    return volume.toFixed(2);
  };

  const calculatePriceChange = (current, high, low) => {
    const mid = (high + low) / 2;
    const change = ((current - mid) / mid) * 100;
    return change;
  };

  if (loading) return <div className="loading">Loading market data...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div>
      <h1>Market Data</h1>

      <div className="card">
        <h2>Market Overview</h2>
        <div style={{ marginBottom: "20px" }}>
          <label>Select Market for Chart: </label>
          <select
            value={selectedMarket}
            onChange={(e) => setSelectedMarket(e.target.value)}
            style={{ marginLeft: "10px", padding: "5px" }}
          >
            {markets
              .filter((m) => m.quote === "EUR")
              .map((market) => (
                <option key={market.market} value={market.market}>
                  {market.market}
                </option>
              ))}
          </select>
        </div>

        <div className="market-data">
          <table className="market-table">
            <thead>
              <tr>
                <th>Market</th>
                <th>Last Price</th>
                <th>24h Change</th>
                <th>24h High</th>
                <th>24h Low</th>
                <th>Volume</th>
                <th>Bid</th>
                <th>Ask</th>
              </tr>
            </thead>
            <tbody>
              {tickers
                .filter((ticker) => ticker.market.includes("EUR"))
                .slice(0, 20)
                .map((ticker) => {
                  const change = calculatePriceChange(
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
                          change >= 0 ? "price-positive" : "price-negative"
                        }
                      >
                        {change >= 0 ? "+" : ""}
                        {change.toFixed(2)}%
                      </td>
                      <td className="price-positive">
                        {formatPrice(ticker.high)}
                      </td>
                      <td className="price-negative">
                        {formatPrice(ticker.low)}
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
      </div>

      {candleData.length > 0 && (
        <div className="card">
          <h2>{selectedMarket} - Last 24 Hours</h2>
          <div className="candle-chart" style={{ overflowX: "auto" }}>
            <table className="market-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Open</th>
                  <th>High</th>
                  <th>Low</th>
                  <th>Close</th>
                  <th>Volume</th>
                </tr>
              </thead>
              <tbody>
                {candleData.slice(0, 12).map((candle, index) => {
                  const date = new Date(candle.timestamp);
                  const isGreen = candle.close >= candle.open;
                  return (
                    <tr key={index}>
                      <td>
                        {date.toLocaleTimeString("nl-NL", {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </td>
                      <td>{formatPrice(candle.open)}</td>
                      <td className="price-positive">
                        {formatPrice(candle.high)}
                      </td>
                      <td className="price-negative">
                        {formatPrice(candle.low)}
                      </td>
                      <td
                        className={
                          isGreen ? "price-positive" : "price-negative"
                        }
                      >
                        {formatPrice(candle.close)}
                      </td>
                      <td>{formatVolume(candle.volume)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default MarketData;
