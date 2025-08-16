import React, { useState, useEffect } from "react";
import axios from "axios";
import { Balance, PortfolioStats, APIError, Transaction } from "@/types";

const Portfolio: React.FC = () => {
  const [balances, setBalances] = useState<Balance[]>([]);
  const [stats, setStats] = useState<PortfolioStats | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedView, setSelectedView] = useState<
    "overview" | "balances" | "transactions"
  >("overview");

  useEffect(() => {
    const fetchPortfolioData = async (): Promise<void> => {
      try {
        setLoading(true);
        setError(null);

        const [balancesResponse, transactionsResponse] = await Promise.all([
          axios.get<{ data: Balance[] }>("/api/v1/balances"),
          axios.get<{ data: Transaction[] }>("/api/v1/transactions?limit=50"),
        ]);

        const balancesData = balancesResponse.data.data;
        const transactionsData = transactionsResponse.data.data;

        setBalances(balancesData);
        setTransactions(transactionsData);

        // Calculate portfolio statistics
        const totalValue = balancesData.reduce(
          (sum, balance) => sum + balance.value,
          0
        );
        const totalChange24h = balancesData.reduce(
          (sum, balance) => sum + (balance.change24h || 0),
          0
        );
        const changePercentage =
          totalValue > 0
            ? (totalChange24h / (totalValue - totalChange24h)) * 100
            : 0;

        setStats({
          totalValue,
          totalChange24h,
          changePercentage,
          totalAssets: balancesData.filter(
            (b) => parseFloat(b.available) > 0 || parseFloat(b.in_order) > 0
          ).length,
          totalInOrder: balancesData.reduce(
            (sum, balance) => sum + parseFloat(balance.in_order),
            0
          ),
        });
      } catch (err) {
        const error = err as APIError;
        setError(
          "Failed to fetch portfolio data: " +
            (error.message || "Unknown error")
        );
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolioData();
  }, []);

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat("nl-NL", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  const formatCrypto = (amount: string | number, symbol: string): string => {
    const numAmount = typeof amount === "string" ? parseFloat(amount) : amount;
    return (
      new Intl.NumberFormat("nl-NL", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 8,
      }).format(numAmount) +
      " " +
      symbol
    );
  };

  const formatPercentage = (value: number): string => {
    return new Intl.NumberFormat("nl-NL", {
      style: "percent",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
      signDisplay: "always",
    }).format(value / 100);
  };

  const formatDate = (dateString: string): string => {
    return new Intl.DateTimeFormat("nl-NL", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(dateString));
  };

  const getChangeColor = (value: number): string => {
    if (value > 0) return "text-success";
    if (value < 0) return "text-error";
    return "text-neutral";
  };

  if (loading) {
    return (
      <main className="portfolio" aria-live="polite">
        <div
          className="loading-container"
          role="status"
          aria-label="Loading portfolio"
        >
          <div className="spinner" aria-hidden="true"></div>
          <span className="sr-only">Loading portfolio data...</span>
        </div>
      </main>
    );
  }

  return (
    <main className="portfolio">
      <div className="container">
        <header className="portfolio-header">
          <h1>Portfolio Overview</h1>
          <p className="subtitle">
            Track your cryptocurrency investments and performance
          </p>
        </header>

        {error && (
          <div className="alert alert--error" role="alert">
            <strong>Error:</strong> {error}
            <button
              className="btn btn--secondary"
              onClick={() => setError(null)}
              aria-label="Dismiss error message"
              type="button"
            >
              ×
            </button>
          </div>
        )}

        {/* Portfolio Navigation */}
        <nav
          className="portfolio-nav"
          role="tablist"
          aria-label="Portfolio sections"
        >
          <button
            role="tab"
            aria-selected={selectedView === "overview"}
            aria-controls="overview-panel"
            className={`nav-tab ${
              selectedView === "overview" ? "nav-tab--active" : ""
            }`}
            onClick={() => setSelectedView("overview")}
            type="button"
          >
            Overview
          </button>
          <button
            role="tab"
            aria-selected={selectedView === "balances"}
            aria-controls="balances-panel"
            className={`nav-tab ${
              selectedView === "balances" ? "nav-tab--active" : ""
            }`}
            onClick={() => setSelectedView("balances")}
            type="button"
          >
            Balances
          </button>
          <button
            role="tab"
            aria-selected={selectedView === "transactions"}
            aria-controls="transactions-panel"
            className={`nav-tab ${
              selectedView === "transactions" ? "nav-tab--active" : ""
            }`}
            onClick={() => setSelectedView("transactions")}
            type="button"
          >
            Transactions
          </button>
        </nav>

        {/* Overview Panel */}
        {selectedView === "overview" && (
          <div
            role="tabpanel"
            id="overview-panel"
            aria-labelledby="overview-tab"
          >
            {stats && (
              <section
                className="portfolio-stats"
                aria-labelledby="stats-heading"
              >
                <h2 id="stats-heading" className="sr-only">
                  Portfolio Statistics
                </h2>
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-header">
                      <h3 className="stat-title">Total Value</h3>
                    </div>
                    <div className="stat-value">
                      {formatCurrency(stats.totalValue)}
                    </div>
                    <div
                      className={`stat-change ${getChangeColor(
                        stats.totalChange24h
                      )}`}
                    >
                      {formatCurrency(stats.totalChange24h)} (
                      {formatPercentage(stats.changePercentage)})
                    </div>
                  </div>

                  <div className="stat-card">
                    <div className="stat-header">
                      <h3 className="stat-title">Total Assets</h3>
                    </div>
                    <div className="stat-value">{stats.totalAssets}</div>
                    <div className="stat-subtitle text-muted">
                      Active holdings
                    </div>
                  </div>

                  <div className="stat-card">
                    <div className="stat-header">
                      <h3 className="stat-title">In Orders</h3>
                    </div>
                    <div className="stat-value">
                      {formatCurrency(stats.totalInOrder)}
                    </div>
                    <div className="stat-subtitle text-muted">
                      Locked in trading
                    </div>
                  </div>
                </div>
              </section>
            )}

            {/* Top Holdings */}
            <section className="card" aria-labelledby="top-holdings-heading">
              <header className="card-header">
                <h2 id="top-holdings-heading">Top Holdings</h2>
                <p className="text-muted">
                  Your largest cryptocurrency positions
                </p>
              </header>

              {balances.length === 0 ? (
                <div className="empty-state">
                  <p className="text-muted">No balances found</p>
                  <p className="text-muted">
                    Start trading to build your portfolio
                  </p>
                </div>
              ) : (
                <div className="table-container">
                  <table role="table" aria-label="Top cryptocurrency holdings">
                    <thead>
                      <tr>
                        <th scope="col">Asset</th>
                        <th scope="col">Balance</th>
                        <th scope="col">Value (EUR)</th>
                        <th scope="col">24h Change</th>
                        <th scope="col">Allocation</th>
                      </tr>
                    </thead>
                    <tbody>
                      {balances
                        .filter((balance) => balance.value > 1)
                        .sort((a, b) => b.value - a.value)
                        .slice(0, 10)
                        .map((balance) => {
                          const allocation = stats
                            ? (balance.value / stats.totalValue) * 100
                            : 0;
                          return (
                            <tr key={balance.symbol}>
                              <td>
                                <div className="asset-info">
                                  <strong>{balance.symbol}</strong>
                                  <div className="text-muted text-sm">
                                    {balance.name}
                                  </div>
                                </div>
                              </td>
                              <td>
                                {formatCrypto(
                                  balance.available,
                                  balance.symbol
                                )}
                              </td>
                              <td>
                                <strong>{formatCurrency(balance.value)}</strong>
                              </td>
                              <td>
                                <span
                                  className={getChangeColor(
                                    balance.change24h || 0
                                  )}
                                >
                                  {formatPercentage(balance.change24h || 0)}
                                </span>
                              </td>
                              <td>
                                <div className="allocation">
                                  <span>{allocation.toFixed(1)}%</span>
                                  <div className="allocation-bar">
                                    <div
                                      className="allocation-fill"
                                      style={{
                                        width: `${Math.min(allocation, 100)}%`,
                                      }}
                                      aria-hidden="true"
                                    ></div>
                                  </div>
                                </div>
                              </td>
                            </tr>
                          );
                        })}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </div>
        )}

        {/* Balances Panel */}
        {selectedView === "balances" && (
          <div
            role="tabpanel"
            id="balances-panel"
            aria-labelledby="balances-tab"
          >
            <section className="card" aria-labelledby="all-balances-heading">
              <header className="card-header">
                <h2 id="all-balances-heading">All Balances</h2>
                <p className="text-muted">
                  Complete overview of your cryptocurrency holdings
                </p>
              </header>

              {balances.length === 0 ? (
                <div className="empty-state">
                  <p className="text-muted">No balances found</p>
                </div>
              ) : (
                <div className="table-container">
                  <table role="table" aria-label="All cryptocurrency balances">
                    <thead>
                      <tr>
                        <th scope="col">Asset</th>
                        <th scope="col">Available</th>
                        <th scope="col">In Order</th>
                        <th scope="col">Total</th>
                        <th scope="col">Value (EUR)</th>
                        <th scope="col">24h Change</th>
                      </tr>
                    </thead>
                    <tbody>
                      {balances
                        .filter(
                          (balance) =>
                            parseFloat(balance.available) > 0 ||
                            parseFloat(balance.in_order) > 0 ||
                            balance.value > 0
                        )
                        .sort((a, b) => b.value - a.value)
                        .map((balance) => {
                          const total =
                            parseFloat(balance.available) +
                            parseFloat(balance.in_order);
                          return (
                            <tr key={balance.symbol}>
                              <td>
                                <div className="asset-info">
                                  <strong>{balance.symbol}</strong>
                                  <div className="text-muted text-sm">
                                    {balance.name}
                                  </div>
                                </div>
                              </td>
                              <td>
                                {formatCrypto(
                                  balance.available,
                                  balance.symbol
                                )}
                              </td>
                              <td>
                                {formatCrypto(balance.in_order, balance.symbol)}
                              </td>
                              <td>
                                <strong>
                                  {formatCrypto(total, balance.symbol)}
                                </strong>
                              </td>
                              <td>
                                <strong>{formatCurrency(balance.value)}</strong>
                              </td>
                              <td>
                                <span
                                  className={getChangeColor(
                                    balance.change24h || 0
                                  )}
                                >
                                  {formatPercentage(balance.change24h || 0)}
                                </span>
                              </td>
                            </tr>
                          );
                        })}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </div>
        )}

        {/* Transactions Panel */}
        {selectedView === "transactions" && (
          <div
            role="tabpanel"
            id="transactions-panel"
            aria-labelledby="transactions-tab"
          >
            <section className="card" aria-labelledby="transactions-heading">
              <header className="card-header">
                <h2 id="transactions-heading">Recent Transactions</h2>
                <p className="text-muted">
                  Your latest trading activity and transfers
                </p>
              </header>

              {transactions.length === 0 ? (
                <div className="empty-state">
                  <p className="text-muted">No transactions found</p>
                  <p className="text-muted">
                    Your trading history will appear here
                  </p>
                </div>
              ) : (
                <div className="table-container">
                  <table role="table" aria-label="Recent transactions">
                    <thead>
                      <tr>
                        <th scope="col">Date</th>
                        <th scope="col">Type</th>
                        <th scope="col">Market</th>
                        <th scope="col">Amount</th>
                        <th scope="col">Price</th>
                        <th scope="col">Total</th>
                        <th scope="col">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {transactions.map((transaction) => (
                        <tr key={transaction.id}>
                          <td>
                            <time dateTime={transaction.createdAt}>
                              {formatDate(transaction.createdAt)}
                            </time>
                          </td>
                          <td>
                            <span
                              className={
                                transaction.side === "buy"
                                  ? "text-success"
                                  : "text-error"
                              }
                            >
                              {transaction.side.toUpperCase()}
                            </span>
                          </td>
                          <td>
                            <strong>{transaction.market}</strong>
                          </td>
                          <td>
                            {formatCrypto(
                              transaction.amount,
                              transaction.market.split("-")[0]
                            )}
                          </td>
                          <td>
                            {formatCurrency(parseFloat(transaction.price))}
                          </td>
                          <td>
                            <strong>
                              {formatCurrency(
                                parseFloat(transaction.amount) *
                                  parseFloat(transaction.price)
                              )}
                            </strong>
                          </td>
                          <td>
                            <span
                              className={`status status--${transaction.status.toLowerCase()}`}
                            >
                              {transaction.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </div>
        )}
      </div>
    </main>
  );
};

export default Portfolio;
