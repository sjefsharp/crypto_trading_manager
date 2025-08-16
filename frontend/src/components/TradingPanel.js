import React, { useState, useEffect } from "react";
import axios from "axios";

const TradingPanel = () => {
  const [markets, setMarkets] = useState([]);
  const [selectedMarket, setSelectedMarket] = useState("BTC-EUR");
  const [orderData, setOrderData] = useState({
    market: "BTC-EUR",
    side: "buy",
    order_type: "market",
    amount: "",
    price: "",
    stop_loss_price: "",
    take_profit_price: "",
  });
  const [openOrders, setOpenOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchMarkets();
    fetchOpenOrders();
  }, []);

  const fetchMarkets = async () => {
    try {
      const response = await axios.get("/api/v1/market/markets");
      const activeMarkets = response.data
        .filter((market) => market.status === "trading")
        .slice(0, 20); // Limit to first 20 for UI simplicity
      setMarkets(activeMarkets);
    } catch (error) {
      console.error("Error fetching markets:", error);
    }
  };

  const fetchOpenOrders = async () => {
    try {
      const response = await axios.get("/api/v1/trading/orders");
      setOpenOrders(response.data);
    } catch (error) {
      console.error("Error fetching orders:", error);
      // Don't show error for orders if API keys not configured
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setOrderData((prev) => ({
      ...prev,
      [name]: value,
      market: name === "market" ? value : prev.market,
    }));

    if (name === "market") {
      setSelectedMarket(value);
    }
  };

  const handleSubmitOrder = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      const response = await axios.post("/api/v1/trading/order", {
        ...orderData,
        amount: parseFloat(orderData.amount),
        price: orderData.price ? parseFloat(orderData.price) : null,
        stop_loss_price: orderData.stop_loss_price
          ? parseFloat(orderData.stop_loss_price)
          : null,
        take_profit_price: orderData.take_profit_price
          ? parseFloat(orderData.take_profit_price)
          : null,
      });

      setMessage(
        `Order placed successfully! Order ID: ${response.data.order_id}`
      );
      setOrderData({
        ...orderData,
        amount: "",
        price: "",
        stop_loss_price: "",
        take_profit_price: "",
      });

      // Refresh open orders
      fetchOpenOrders();
    } catch (error) {
      setMessage(
        `Error placing order: ${error.response?.data?.detail || error.message}`
      );
    } finally {
      setLoading(false);
    }
  };

  const cancelOrder = async (orderId) => {
    try {
      await axios.delete(`/api/v1/trading/order/${orderId}`);
      setMessage("Order cancelled successfully");
      fetchOpenOrders();
    } catch (error) {
      setMessage(
        `Error cancelling order: ${
          error.response?.data?.detail || error.message
        }`
      );
    }
  };

  return (
    <div>
      <h1>Trading Panel</h1>

      <div className="trading-dashboard">
        <div className="card">
          <h2>Place Order</h2>
          <form onSubmit={handleSubmitOrder} className="trading-form">
            <div className="form-group">
              <label>Market:</label>
              <select
                name="market"
                value={orderData.market}
                onChange={handleInputChange}
                required
              >
                {markets.map((market) => (
                  <option key={market.market} value={market.market}>
                    {market.market}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Side:</label>
              <select
                name="side"
                value={orderData.side}
                onChange={handleInputChange}
                required
              >
                <option value="buy">Buy</option>
                <option value="sell">Sell</option>
              </select>
            </div>

            <div className="form-group">
              <label>Order Type:</label>
              <select
                name="order_type"
                value={orderData.order_type}
                onChange={handleInputChange}
                required
              >
                <option value="market">Market</option>
                <option value="limit">Limit</option>
              </select>
            </div>

            <div className="form-group">
              <label>Amount:</label>
              <input
                type="number"
                name="amount"
                value={orderData.amount}
                onChange={handleInputChange}
                step="0.00000001"
                required
                placeholder="Enter amount"
              />
            </div>

            {orderData.order_type === "limit" && (
              <div className="form-group">
                <label>Price:</label>
                <input
                  type="number"
                  name="price"
                  value={orderData.price}
                  onChange={handleInputChange}
                  step="0.01"
                  placeholder="Enter limit price"
                />
              </div>
            )}

            <div className="form-group">
              <label>Stop Loss Price (Optional):</label>
              <input
                type="number"
                name="stop_loss_price"
                value={orderData.stop_loss_price}
                onChange={handleInputChange}
                step="0.01"
                placeholder="Enter stop loss price"
              />
            </div>

            <div className="form-group">
              <label>Take Profit Price (Optional):</label>
              <input
                type="number"
                name="take_profit_price"
                value={orderData.take_profit_price}
                onChange={handleInputChange}
                step="0.01"
                placeholder="Enter take profit price"
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? "Placing Order..." : "Place Order"}
            </button>
          </form>

          {message && (
            <div
              className={message.includes("Error") ? "error" : "success"}
              style={{ marginTop: "15px" }}
            >
              {message}
            </div>
          )}
        </div>

        <div className="card">
          <h2>Open Orders</h2>
          {openOrders.length > 0 ? (
            <div className="market-data">
              <table className="market-table">
                <thead>
                  <tr>
                    <th>Market</th>
                    <th>Side</th>
                    <th>Type</th>
                    <th>Amount</th>
                    <th>Price</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {openOrders.map((order) => (
                    <tr key={order.orderId}>
                      <td>{order.market}</td>
                      <td
                        className={
                          order.side === "buy"
                            ? "price-positive"
                            : "price-negative"
                        }
                      >
                        {order.side.toUpperCase()}
                      </td>
                      <td>{order.orderType}</td>
                      <td>{parseFloat(order.amount).toFixed(6)}</td>
                      <td>
                        {order.price
                          ? `€${parseFloat(order.price).toFixed(2)}`
                          : "Market"}
                      </td>
                      <td>{order.status}</td>
                      <td>
                        <button
                          className="btn btn-secondary"
                          onClick={() => cancelOrder(order.orderId)}
                          style={{ fontSize: "12px", padding: "5px 10px" }}
                        >
                          Cancel
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>
              No open orders. Configure your API keys to view and place orders.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default TradingPanel;
