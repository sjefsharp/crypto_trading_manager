import React, { useState, useEffect } from "react";
import axios from "axios";

const Dashboard = () => {
  const [marketData, setMarketData] = useState([]);
  const [balance, setBalance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch market data for major pairs
      const marketsResponse = await axios.get("/api/v1/market/ticker");
      const majorMarkets = marketsResponse.data.filter((market) =>
        ["BTC-EUR", "ETH-EUR", "ADA-EUR", "DOT-EUR"].includes(market.market)
      );
      setMarketData(majorMarkets);

      // Try to fetch balance (will fail if API keys not configured)
      try {
        const balanceResponse = await axios.get("/api/v1/trading/balance");
        const nonZeroBalances = balanceResponse.data.filter(
          (bal) => parseFloat(bal.available) > 0 || parseFloat(bal.in_order) > 0
        );
        setBalance(nonZeroBalances);
      } catch (balanceError) {
        console.log(
          "Balance fetch failed (likely no API keys configured):",
          balanceError
        );
        setBalance([]);
      }
    } catch (err) {
      setError("Failed to fetch dashboard data: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading dashboard...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div>
      <h1>Trading Dashboard</h1>

      <div className="trading-dashboard">
        <div className="card">
          <h2>Market Overview</h2>
          {marketData.length > 0 ? (
            <table className="market-table">
              <thead>
                <tr>
                  <th>Market</th>
                  <th>Last Price</th>
                  <th>24h High</th>
                  <th>24h Low</th>
                  <th>Volume</th>
                </tr>
              </thead>
              <tbody>
                {marketData.map((market) => (
                  <tr key={market.market}>
                    <td>{market.market}</td>
                    <td>€{market.last.toFixed(2)}</td>
                    <td className="price-positive">
                      €{market.high.toFixed(2)}
                    </td>
                    <td className="price-negative">€{market.low.toFixed(2)}</td>
                    <td>{market.volume.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No market data available</p>
          )}
        </div>

        <div className="card">
          <h2>Account Balance</h2>
          {balance.length > 0 ? (
            <table className="market-table">
              <thead>
                <tr>
                  <th>Asset</th>
                  <th>Available</th>
                  <th>In Order</th>
                </tr>
              </thead>
              <tbody>
                {balance.map((bal) => (
                  <tr key={bal.symbol}>
                    <td>{bal.symbol}</td>
                    <td>{bal.available.toFixed(6)}</td>
                    <td>{bal.in_order.toFixed(6)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>Configure your Bitvavo API keys to view balance</p>
          )}
        </div>
      </div>

      <div className="card">
        <h2>Quick Stats</h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "20px",
          }}
        >
          <div>
            <h3>Total Markets</h3>
            <p style={{ fontSize: "2em", margin: "10px 0" }}>
              {marketData.length}
            </p>
          </div>
          <div>
            <h3>Assets Held</h3>
            <p style={{ fontSize: "2em", margin: "10px 0" }}>
              {balance.length}
            </p>
          </div>
          <div>
            <h3>Status</h3>
            <p style={{ fontSize: "2em", margin: "10px 0", color: "#4CAF50" }}>
              Online
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
