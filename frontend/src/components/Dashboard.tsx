import React, { useState, useEffect } from "react";
import axios from "axios";
import { DashboardProps, Market, Balance, APIError } from "@/types";

const Dashboard: React.FC<DashboardProps> = ({ className }) => {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [balances, setBalances] = useState<Balance[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async (): Promise<void> => {
      try {
        setLoading(true);
        setError(null);

        const [marketsResponse, balancesResponse] = await Promise.all([
          axios.get<{ data: Market[] }>("/api/v1/markets"),
          axios.get<{ data: Balance[] }>("/api/v1/balance"),
        ]);

        const majorMarkets = marketsResponse.data.data.filter(
          (market: Market) =>
            ["BTC", "ETH", "ADA", "DOT", "LINK"].includes(market.base)
        );

        setMarkets(majorMarkets);

        const activeBalances = balancesResponse.data.data.filter(
          (bal: Balance) =>
            parseFloat(bal.available) > 0 || parseFloat(bal.in_order) > 0
        );

        setBalances(activeBalances);
      } catch (err) {
        const error = err as APIError;
        setError(
          "Failed to fetch dashboard data: " +
            (error.message || "Unknown error")
        );
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat("nl-NL", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  };

  const formatBalance = (balance: string): string => {
    return parseFloat(balance).toFixed(6);
  };

  if (loading) {
    return (
      <main className={`dashboard ${className || ""}`} aria-live="polite">
        <div
          className="loading-container"
          role="status"
          aria-label="Loading dashboard data"
        >
          <div className="spinner" aria-hidden="true"></div>
          <span className="sr-only">Loading dashboard data...</span>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className={`dashboard ${className || ""}`}>
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
    <main className={`dashboard ${className || ""}`}>
      <div className="container">
        <header className="dashboard-header">
          <h1>Trading Dashboard</h1>
          <p className="dashboard-subtitle">
            Monitor your crypto trading portfolio and market data
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Major Markets Section */}
          <section className="card" aria-labelledby="markets-heading">
            <header className="card-header">
              <h2 id="markets-heading">Major Markets</h2>
              <p className="text-muted">Top cryptocurrency trading pairs</p>
            </header>

            <div className="table-container">
              <table role="table" aria-label="Major cryptocurrency markets">
                <thead>
                  <tr>
                    <th scope="col">Market</th>
                    <th scope="col">Price</th>
                    <th scope="col">24h High</th>
                    <th scope="col">24h Low</th>
                    <th scope="col">Volume</th>
                  </tr>
                </thead>
                <tbody>
                  {markets.map((market) => (
                    <tr key={market.market}>
                      <td>
                        <strong>{market.market}</strong>
                      </td>
                      <td>{formatPrice(parseFloat(market.base))}</td>
                      <td className="text-success">
                        {formatPrice(parseFloat(market.quote))}
                      </td>
                      <td className="text-error">
                        {formatPrice(parseFloat(market.base))}
                      </td>
                      <td>
                        {parseFloat(market.minOrderInBaseAsset).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* Account Balances Section */}
          <section className="card" aria-labelledby="balances-heading">
            <header className="card-header">
              <h2 id="balances-heading">Account Balances</h2>
              <p className="text-muted">Your current cryptocurrency holdings</p>
            </header>

            <div className="table-container">
              <table role="table" aria-label="Account cryptocurrency balances">
                <thead>
                  <tr>
                    <th scope="col">Asset</th>
                    <th scope="col">Available</th>
                    <th scope="col">In Order</th>
                  </tr>
                </thead>
                <tbody>
                  {balances.map((bal) => (
                    <tr key={bal.symbol}>
                      <td>
                        <strong>{bal.symbol}</strong>
                      </td>
                      <td>{formatBalance(bal.available)}</td>
                      <td>{formatBalance(bal.in_order)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
};

export default Dashboard;
