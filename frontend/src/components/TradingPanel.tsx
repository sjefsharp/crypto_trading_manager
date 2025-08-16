import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Market,
  Trade,
  OrderFormData,
  APIError,
  InputChangeHandler,
  FormSubmitHandler,
} from '@/types';

const TradingPanel: React.FC = () => {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [orders, setOrders] = useState<Trade[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [orderForm, setOrderForm] = useState<OrderFormData>({
    market: 'BTC-EUR',
    side: 'buy',
    orderType: 'limit',
    amount: '',
    price: '',
  });

  useEffect(() => {
    const fetchInitialData = async (): Promise<void> => {
      try {
        setLoading(true);
        setError(null);

        const [marketsResponse, ordersResponse] = await Promise.all([
          axios.get<{ data: Market[] }>('/api/v1/markets'),
          axios.get<{ data: Trade[] }>('/api/v1/orders'),
        ]);

        const activeMarkets = marketsResponse.data.data.filter(
          (market: Market) => market.status === 'trading'
        );
        setMarkets(activeMarkets);
        setOrders(ordersResponse.data.data);
      } catch (err) {
        const error = err as APIError;
        setError(
          'Failed to fetch trading data: ' + (error.message || 'Unknown error')
        );
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, []);

  const handleInputChange: InputChangeHandler = e => {
    const { name, value } = e.target;
    setOrderForm(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const validateForm = (): boolean => {
    if (!orderForm.amount || parseFloat(orderForm.amount) <= 0) {
      setError('Please enter a valid amount');
      return false;
    }
    if (
      orderForm.orderType === 'limit' &&
      (!orderForm.price || parseFloat(orderForm.price) <= 0)
    ) {
      setError('Please enter a valid price for limit orders');
      return false;
    }
    return true;
  };

  const handleSubmitOrder: FormSubmitHandler = async e => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      setError(null);
      const response = await axios.post<{ data: Trade }>(
        '/api/v1/orders',
        orderForm
      );

      setOrders(prev => [response.data.data, ...prev]);
      setOrderForm({
        market: orderForm.market,
        side: 'buy',
        orderType: 'limit',
        amount: '',
        price: '',
      });

      // Success feedback could be added here
    } catch (err) {
      const error = err as APIError;
      setError(
        `Error placing order: ${error.response?.data?.detail || error.message || 'Unknown error'}`
      );
    }
  };

  const cancelOrder = async (orderId: string): Promise<void> => {
    try {
      await axios.delete(`/api/v1/orders/${orderId}`);
      setOrders(prev => prev.filter(order => order.orderId !== orderId));
    } catch (err) {
      const error = err as APIError;
      setError(
        error.response?.data?.detail ||
          error.message ||
          'Failed to cancel order'
      );
    }
  };

  const formatPrice = (price: number | null): string => {
    if (price === null) return 'Market';
    return new Intl.NumberFormat('nl-NL', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 8,
    }).format(price);
  };

  if (loading) {
    return (
      <main className='trading-panel' aria-live='polite'>
        <div
          className='loading-container'
          role='status'
          aria-label='Loading trading panel'
        >
          <div className='spinner' aria-hidden='true'></div>
          <span className='sr-only'>Loading trading panel...</span>
        </div>
      </main>
    );
  }

  return (
    <main className='trading-panel'>
      <div className='container'>
        <header className='trading-panel-header'>
          <h1>Trading Panel</h1>
          <p className='subtitle'>Place orders and manage your trades</p>
        </header>

        {error && (
          <div className='alert alert--error' role='alert'>
            <strong>Error:</strong> {error}
            <button
              className='btn btn--secondary'
              onClick={() => setError(null)}
              aria-label='Dismiss error message'
              type='button'
            >
              ×
            </button>
          </div>
        )}

        <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
          {/* Order Form */}
          <section
            className='order-form card'
            aria-labelledby='order-form-heading'
          >
            <header className='card-header'>
              <h2 id='order-form-heading'>Place New Order</h2>
              <p className='text-muted'>
                Create buy or sell orders for cryptocurrency trading
              </p>
            </header>

            <form onSubmit={handleSubmitOrder} noValidate>
              <div className='form-group'>
                <label htmlFor='market' className='form-label'>
                  Trading Pair
                </label>
                <select
                  id='market'
                  name='market'
                  className='form-select'
                  value={orderForm.market}
                  onChange={handleInputChange}
                  required
                  aria-describedby='market-help'
                >
                  {markets.map(market => (
                    <option key={market.market} value={market.market}>
                      {market.market}
                    </option>
                  ))}
                </select>
                <div id='market-help' className='form-help text-muted'>
                  Select the cryptocurrency pair you want to trade
                </div>
              </div>

              <div className='form-group'>
                <fieldset>
                  <legend className='form-label'>Order Side</legend>
                  <div className='radio-group'>
                    <label className='radio-label'>
                      <input
                        type='radio'
                        name='side'
                        value='buy'
                        checked={orderForm.side === 'buy'}
                        onChange={handleInputChange}
                        required
                      />
                      <span className='radio-text text-success'>Buy</span>
                    </label>
                    <label className='radio-label'>
                      <input
                        type='radio'
                        name='side'
                        value='sell'
                        checked={orderForm.side === 'sell'}
                        onChange={handleInputChange}
                        required
                      />
                      <span className='radio-text text-error'>Sell</span>
                    </label>
                  </div>
                </fieldset>
              </div>

              <div className='form-group'>
                <fieldset>
                  <legend className='form-label'>Order Type</legend>
                  <div className='radio-group'>
                    <label className='radio-label'>
                      <input
                        type='radio'
                        name='orderType'
                        value='market'
                        checked={orderForm.orderType === 'market'}
                        onChange={handleInputChange}
                        required
                      />
                      <span className='radio-text'>Market</span>
                    </label>
                    <label className='radio-label'>
                      <input
                        type='radio'
                        name='orderType'
                        value='limit'
                        checked={orderForm.orderType === 'limit'}
                        onChange={handleInputChange}
                        required
                      />
                      <span className='radio-text'>Limit</span>
                    </label>
                  </div>
                </fieldset>
              </div>

              <div className='form-group'>
                <label htmlFor='amount' className='form-label'>
                  Amount
                </label>
                <input
                  type='number'
                  id='amount'
                  name='amount'
                  className='form-input'
                  value={orderForm.amount}
                  onChange={handleInputChange}
                  placeholder='0.00'
                  step='0.000001'
                  min='0'
                  required
                  aria-describedby='amount-help'
                />
                <div id='amount-help' className='form-help text-muted'>
                  Enter the amount of cryptocurrency to trade
                </div>
              </div>

              {orderForm.orderType === 'limit' && (
                <div className='form-group'>
                  <label htmlFor='price' className='form-label'>
                    Price (EUR)
                  </label>
                  <input
                    type='number'
                    id='price'
                    name='price'
                    className='form-input'
                    value={orderForm.price}
                    onChange={handleInputChange}
                    placeholder='0.00'
                    step='0.01'
                    min='0'
                    required={orderForm.orderType === 'limit'}
                    aria-describedby='price-help'
                  />
                  <div id='price-help' className='form-help text-muted'>
                    Set the maximum price you&apos;re willing to pay (buy) or
                    minimum price to receive (sell)
                  </div>
                </div>
              )}

              <button
                type='submit'
                className={`btn btn--primary ${orderForm.side === 'buy' ? 'btn--success' : 'btn--error'}`}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className='spinner' aria-hidden='true'></span>
                    <span>Placing Order...</span>
                  </>
                ) : (
                  `${orderForm.side.toUpperCase()} ${orderForm.market.split('-')[0]}`
                )}
              </button>
            </form>
          </section>

          {/* Open Orders */}
          <section className='card' aria-labelledby='orders-heading'>
            <header className='card-header'>
              <h2 id='orders-heading'>Open Orders</h2>
              <p className='text-muted'>Your active trading orders</p>
            </header>

            {orders.length === 0 ? (
              <div className='empty-state'>
                <p className='text-muted'>No open orders</p>
                <p className='text-muted'>
                  Place your first order using the form above
                </p>
              </div>
            ) : (
              <div className='table-container'>
                <table role='table' aria-label='Open trading orders'>
                  <thead>
                    <tr>
                      <th scope='col'>Market</th>
                      <th scope='col'>Side</th>
                      <th scope='col'>Type</th>
                      <th scope='col'>Amount</th>
                      <th scope='col'>Price</th>
                      <th scope='col'>Status</th>
                      <th scope='col'>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {orders.map(order => (
                      <tr key={order.orderId}>
                        <td>
                          <strong>{order.market}</strong>
                        </td>
                        <td>
                          <span
                            className={
                              order.side === 'buy'
                                ? 'text-success'
                                : 'text-error'
                            }
                          >
                            {order.side.toUpperCase()}
                          </span>
                        </td>
                        <td>{order.orderType}</td>
                        <td>{parseFloat(order.amount).toFixed(6)}</td>
                        <td>{formatPrice(order.price)}</td>
                        <td>
                          <span
                            className={`status status--${order.status.toLowerCase()}`}
                          >
                            {order.status}
                          </span>
                        </td>
                        <td>
                          <button
                            className='btn btn--secondary btn--sm'
                            onClick={() => cancelOrder(order.orderId)}
                            type='button'
                            aria-label={`Cancel ${order.side} order for ${order.market}`}
                          >
                            Cancel
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
};

export default TradingPanel;
