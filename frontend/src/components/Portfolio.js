import React, { useState, useEffect } from "react";
import axios from "axios";

const Portfolio = () => {
  const [portfolios, setPortfolios] = useState([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState(null);
  const [positions, setPositions] = useState([]);
  const [trades, setTrades] = useState([]);
  const [newPortfolioName, setNewPortfolioName] = useState("");
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchPortfolios();
  }, []);

  useEffect(() => {
    if (selectedPortfolio) {
      fetchPortfolioDetails(selectedPortfolio.id);
    }
  }, [selectedPortfolio]);

  const fetchPortfolios = async () => {
    try {
      setLoading(true);
      const response = await axios.get("/api/v1/portfolio/");
      setPortfolios(response.data);
      if (response.data.length > 0 && !selectedPortfolio) {
        setSelectedPortfolio(response.data[0]);
      }
    } catch (error) {
      console.error("Error fetching portfolios:", error);
      setMessage(
        "Error fetching portfolios: " +
          (error.response?.data?.detail || error.message)
      );
    } finally {
      setLoading(false);
    }
  };

  const fetchPortfolioDetails = async (portfolioId) => {
    try {
      const [positionsResponse, tradesResponse] = await Promise.all([
        axios.get(`/api/v1/portfolio/${portfolioId}/positions`),
        axios.get(`/api/v1/portfolio/${portfolioId}/trades`),
      ]);

      setPositions(positionsResponse.data);
      setTrades(tradesResponse.data);
    } catch (error) {
      console.error("Error fetching portfolio details:", error);
    }
  };

  const createPortfolio = async (e) => {
    e.preventDefault();
    if (!newPortfolioName.trim()) return;

    try {
      const response = await axios.post("/api/v1/portfolio/", {
        name: newPortfolioName,
        description: `Portfolio created on ${new Date().toLocaleDateString()}`,
      });

      setPortfolios([...portfolios, response.data]);
      setNewPortfolioName("");
      setMessage("Portfolio created successfully!");

      // Select the new portfolio
      setSelectedPortfolio(response.data);
    } catch (error) {
      setMessage(
        "Error creating portfolio: " +
          (error.response?.data?.detail || error.message)
      );
    }
  };

  const updatePortfolioPositions = async () => {
    if (!selectedPortfolio) return;

    try {
      await axios.put(
        `/api/v1/portfolio/${selectedPortfolio.id}/update-positions`
      );
      setMessage("Portfolio positions updated with current market prices!");
      fetchPortfolioDetails(selectedPortfolio.id);
      fetchPortfolios(); // Refresh to get updated total value
    } catch (error) {
      setMessage(
        "Error updating positions: " +
          (error.response?.data?.detail || error.message)
      );
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

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString("nl-NL", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) return <div className="loading">Loading portfolios...</div>;

  return (
    <div>
      <h1>Portfolio Management</h1>

      {message && (
        <div
          className={message.includes("Error") ? "error" : "success"}
          style={{ marginBottom: "20px" }}
        >
          {message}
        </div>
      )}

      <div className="trading-dashboard">
        <div className="card">
          <h2>Portfolios</h2>

          <form onSubmit={createPortfolio} style={{ marginBottom: "20px" }}>
            <div className="form-group">
              <label>Create New Portfolio:</label>
              <input
                type="text"
                value={newPortfolioName}
                onChange={(e) => setNewPortfolioName(e.target.value)}
                placeholder="Enter portfolio name"
                style={{ marginRight: "10px" }}
              />
              <button type="submit" className="btn btn-primary">
                Create
              </button>
            </div>
          </form>

          {portfolios.length > 0 ? (
            <div>
              <div style={{ marginBottom: "15px" }}>
                <label>Select Portfolio: </label>
                <select
                  value={selectedPortfolio?.id || ""}
                  onChange={(e) => {
                    const portfolio = portfolios.find(
                      (p) => p.id === parseInt(e.target.value)
                    );
                    setSelectedPortfolio(portfolio);
                  }}
                  style={{ marginLeft: "10px", padding: "5px" }}
                >
                  {portfolios.map((portfolio) => (
                    <option key={portfolio.id} value={portfolio.id}>
                      {portfolio.name} - {formatPrice(portfolio.total_value)}
                    </option>
                  ))}
                </select>
              </div>

              <table className="market-table">
                <thead>
                  <tr>
                    <th>Portfolio</th>
                    <th>Total Value</th>
                    <th>Status</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolios.map((portfolio) => (
                    <tr
                      key={portfolio.id}
                      style={{
                        backgroundColor:
                          selectedPortfolio?.id === portfolio.id
                            ? "#404040"
                            : "transparent",
                        cursor: "pointer",
                      }}
                      onClick={() => setSelectedPortfolio(portfolio)}
                    >
                      <td>
                        <strong>{portfolio.name}</strong>
                      </td>
                      <td>{formatPrice(portfolio.total_value)}</td>
                      <td
                        className={
                          portfolio.is_active
                            ? "price-positive"
                            : "price-negative"
                        }
                      >
                        {portfolio.is_active ? "Active" : "Inactive"}
                      </td>
                      <td>{portfolio.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No portfolios found. Create your first portfolio above.</p>
          )}
        </div>

        <div className="card">
          <h2>Portfolio Summary</h2>
          {selectedPortfolio ? (
            <div>
              <h3>{selectedPortfolio.name}</h3>
              <p>
                <strong>Total Value:</strong>{" "}
                {formatPrice(selectedPortfolio.total_value)}
              </p>
              <p>
                <strong>Positions:</strong> {positions.length}
              </p>
              <p>
                <strong>Total Trades:</strong> {trades.length}
              </p>

              <button
                onClick={updatePortfolioPositions}
                className="btn btn-secondary"
                style={{ marginTop: "10px" }}
              >
                Update with Current Prices
              </button>
            </div>
          ) : (
            <p>Select a portfolio to view summary</p>
          )}
        </div>
      </div>

      {selectedPortfolio && (
        <>
          <div className="card">
            <h2>Current Positions</h2>
            {positions.length > 0 ? (
              <div className="market-data">
                <table className="market-table">
                  <thead>
                    <tr>
                      <th>Symbol</th>
                      <th>Quantity</th>
                      <th>Avg Price</th>
                      <th>Current Price</th>
                      <th>Value</th>
                      <th>P&L</th>
                      <th>P&L %</th>
                    </tr>
                  </thead>
                  <tbody>
                    {positions.map((position) => {
                      const totalValue =
                        position.current_price * position.quantity;
                      const pnlPercent =
                        ((position.current_price - position.average_price) /
                          position.average_price) *
                        100;

                      return (
                        <tr key={position.id}>
                          <td>
                            <strong>{position.symbol}</strong>
                          </td>
                          <td>{position.quantity.toFixed(6)}</td>
                          <td>{formatPrice(position.average_price)}</td>
                          <td>{formatPrice(position.current_price)}</td>
                          <td>{formatPrice(totalValue)}</td>
                          <td
                            className={
                              position.unrealized_pnl >= 0
                                ? "price-positive"
                                : "price-negative"
                            }
                          >
                            {formatPrice(position.unrealized_pnl)}
                          </td>
                          <td
                            className={
                              pnlPercent >= 0
                                ? "price-positive"
                                : "price-negative"
                            }
                          >
                            {pnlPercent >= 0 ? "+" : ""}
                            {pnlPercent.toFixed(2)}%
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <p>
                No positions in this portfolio. Start trading to see positions
                here.
              </p>
            )}
          </div>

          <div className="card">
            <h2>Trade History</h2>
            {trades.length > 0 ? (
              <div className="market-data">
                <table className="market-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Symbol</th>
                      <th>Side</th>
                      <th>Type</th>
                      <th>Quantity</th>
                      <th>Price</th>
                      <th>Value</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {trades.slice(0, 20).map((trade) => (
                      <tr key={trade.id}>
                        <td>{formatDate(trade.created_at)}</td>
                        <td>{trade.symbol}</td>
                        <td
                          className={
                            trade.side === "buy"
                              ? "price-positive"
                              : "price-negative"
                          }
                        >
                          {trade.side.toUpperCase()}
                        </td>
                        <td>{trade.order_type}</td>
                        <td>{trade.quantity.toFixed(6)}</td>
                        <td>
                          {trade.price ? formatPrice(trade.price) : "Market"}
                        </td>
                        <td>
                          {trade.price
                            ? formatPrice(trade.quantity * trade.price)
                            : "-"}
                        </td>
                        <td>{trade.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p>No trades in this portfolio yet.</p>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default Portfolio;
