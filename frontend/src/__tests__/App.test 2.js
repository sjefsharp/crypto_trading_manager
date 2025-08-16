import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import axios from 'axios';

import App from '../App';
import Dashboard from '../components/Dashboard';
import TradingPanel from '../components/TradingPanel';
import MarketData from '../components/MarketData';
import Portfolio from '../components/Portfolio';
import Navbar from '../components/Navbar';

// Mock axios
jest.mock('axios');
const mockedAxios = axios;

// Helper function to render components with Router
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('App Component', () => {
  test('renders without crashing', () => {
    renderWithRouter(<App />);
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });

  test('renders navbar', () => {
    renderWithRouter(<App />);
    expect(screen.getByText('Crypto Trading Manager')).toBeInTheDocument();
  });
});

describe('Navbar Component', () => {
  test('renders all navigation links', () => {
    renderWithRouter(<Navbar />);
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Trading')).toBeInTheDocument();
    expect(screen.getByText('Market Data')).toBeInTheDocument();
    expect(screen.getByText('Portfolio')).toBeInTheDocument();
  });

  test('navigation links have correct href attributes', () => {
    renderWithRouter(<Navbar />);
    
    expect(screen.getByText('Dashboard').closest('a')).toHaveAttribute('href', '/');
    expect(screen.getByText('Trading').closest('a')).toHaveAttribute('href', '/trading');
    expect(screen.getByText('Market Data').closest('a')).toHaveAttribute('href', '/market');
    expect(screen.getByText('Portfolio').closest('a')).toHaveAttribute('href', '/portfolio');
  });
});

describe('Dashboard Component', () => {
  beforeEach(() => {
    mockedAxios.get.mockClear();
  });

  test('renders loading state initially', () => {
    mockedAxios.get.mockImplementation(() => new Promise(() => {})); // Never resolves
    renderWithRouter(<Dashboard />);
    
    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();
  });

  test('fetches and displays market data', async () => {
    const mockMarketData = [
      { market: 'BTC-EUR', last: '45000.00', change24h: '2.5' },
      { market: 'ETH-EUR', last: '3000.00', change24h: '-1.2' }
    ];

    mockedAxios.get.mockImplementation((url) => {
      if (url === '/api/v1/market/ticker') {
        return Promise.resolve({ data: mockMarketData });
      }
      if (url === '/api/v1/trading/balance') {
        return Promise.reject(new Error('No API keys'));
      }
      return Promise.reject(new Error('Unknown endpoint'));
    });

    renderWithRouter(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('BTC-EUR')).toBeInTheDocument();
      expect(screen.getByText('ETH-EUR')).toBeInTheDocument();
    });
  });

  test('displays error message on fetch failure', async () => {
    mockedAxios.get.mockRejectedValue(new Error('Network error'));

    renderWithRouter(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to fetch dashboard data/)).toBeInTheDocument();
    });
  });

  test('handles balance fetch failure gracefully', async () => {
    const mockMarketData = [
      { market: 'BTC-EUR', last: '45000.00', change24h: '2.5' }
    ];

    mockedAxios.get.mockImplementation((url) => {
      if (url === '/api/v1/market/ticker') {
        return Promise.resolve({ data: mockMarketData });
      }
      if (url === '/api/v1/trading/balance') {
        return Promise.reject(new Error('No API keys configured'));
      }
      return Promise.reject(new Error('Unknown endpoint'));
    });

    renderWithRouter(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('BTC-EUR')).toBeInTheDocument();
      // Should not show error for balance failure
      expect(screen.queryByText(/Failed to fetch dashboard data/)).not.toBeInTheDocument();
    });
  });
});

describe('TradingPanel Component', () => {
  beforeEach(() => {
    mockedAxios.get.mockClear();
    mockedAxios.post.mockClear();
  });

  test('renders trading form', async () => {
    const mockMarkets = [
      { market: 'BTC-EUR', status: 'trading' },
      { market: 'ETH-EUR', status: 'trading' }
    ];

    mockedAxios.get.mockImplementation((url) => {
      if (url === '/api/v1/market/markets') {
        return Promise.resolve({ data: mockMarkets });
      }
      if (url === '/api/v1/trading/orders') {
        return Promise.resolve({ data: [] });
      }
      return Promise.reject(new Error('Unknown endpoint'));
    });

    renderWithRouter(<TradingPanel />);

    await waitFor(() => {
      expect(screen.getByText('Trading Panel')).toBeInTheDocument();
      expect(screen.getByText('Place Order')).toBeInTheDocument();
    });
  });

  test('submits order successfully', async () => {
    const mockMarkets = [
      { market: 'BTC-EUR', status: 'trading' }
    ];

    mockedAxios.get.mockImplementation((url) => {
      if (url === '/api/v1/market/markets') {
        return Promise.resolve({ data: mockMarkets });
      }
      if (url === '/api/v1/trading/orders') {
        return Promise.resolve({ data: [] });
      }
    });

    mockedAxios.post.mockResolvedValue({
      data: { order_id: 'test-order-123' }
    });

    renderWithRouter(<TradingPanel />);

    await waitFor(() => {
      expect(screen.getByDisplayValue('BTC-EUR')).toBeInTheDocument();
    });

    // Fill in order form
    const amountInput = screen.getByDisplayValue('');
    fireEvent.change(amountInput, { target: { value: '0.001' } });

    // Submit order
    const submitButton = screen.getByText('Place Order');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/trading/order', expect.any(Object));
    });
  });

  test('displays error message on order failure', async () => {
    const mockMarkets = [
      { market: 'BTC-EUR', status: 'trading' }
    ];

    mockedAxios.get.mockImplementation((url) => {
      if (url === '/api/v1/market/markets') {
        return Promise.resolve({ data: mockMarkets });
      }
      if (url === '/api/v1/trading/orders') {
        return Promise.resolve({ data: [] });
      }
    });

    mockedAxios.post.mockRejectedValue({
      response: { data: { detail: 'Insufficient funds' } }
    });

    renderWithRouter(<TradingPanel />);

    await waitFor(() => {
      expect(screen.getByDisplayValue('BTC-EUR')).toBeInTheDocument();
    });

    // Fill in order form
    const amountInput = screen.getByDisplayValue('');
    fireEvent.change(amountInput, { target: { value: '0.001' } });

    // Submit order
    const submitButton = screen.getByText('Place Order');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Error placing order: Insufficient funds/)).toBeInTheDocument();
    });
  });
});

describe('MarketData Component', () => {
  beforeEach(() => {
    mockedAxios.get.mockClear();
  });

  test('renders market data table', async () => {
    const mockMarketData = [
      { 
        market: 'BTC-EUR', 
        last: '45000.00', 
        high24h: '46000.00',
        low24h: '44000.00',
        volume24h: '100.50',
        change24h: '2.5'
      }
    ];

    mockedAxios.get.mockResolvedValue({ data: mockMarketData });

    renderWithRouter(<MarketData />);

    await waitFor(() => {
      expect(screen.getByText('Market Data')).toBeInTheDocument();
      expect(screen.getByText('BTC-EUR')).toBeInTheDocument();
      expect(screen.getByText('€45,000.00')).toBeInTheDocument();
    });
  });

  test('handles refresh functionality', async () => {
    const mockMarketData = [
      { market: 'BTC-EUR', last: '45000.00', change24h: '2.5' }
    ];

    mockedAxios.get.mockResolvedValue({ data: mockMarketData });

    renderWithRouter(<MarketData />);

    await waitFor(() => {
      expect(screen.getByText('BTC-EUR')).toBeInTheDocument();
    });

    // Click refresh button
    const refreshButton = screen.getByText('Refresh');
    fireEvent.click(refreshButton);

    // Should make another API call
    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledTimes(2);
    });
  });
});

describe('Portfolio Component', () => {
  beforeEach(() => {
    mockedAxios.get.mockClear();
  });

  test('renders portfolio data', async () => {
    const mockBalance = [
      { symbol: 'EUR', available: '1000.00', in_order: '0.00' },
      { symbol: 'BTC', available: '0.05', in_order: '0.001' }
    ];

    mockedAxios.get.mockResolvedValue({ data: mockBalance });

    renderWithRouter(<Portfolio />);

    await waitFor(() => {
      expect(screen.getByText('Portfolio')).toBeInTheDocument();
      expect(screen.getByText('EUR')).toBeInTheDocument();
      expect(screen.getByText('BTC')).toBeInTheDocument();
    });
  });

  test('handles API error gracefully', async () => {
    mockedAxios.get.mockRejectedValue(new Error('API keys not configured'));

    renderWithRouter(<Portfolio />);

    await waitFor(() => {
      expect(screen.getByText(/Error loading portfolio/)).toBeInTheDocument();
    });
  });
});
