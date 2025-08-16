import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import Dashboard from '../components/Dashboard';

// Mock axios
vi.mock('axios');
const mockedAxios = axios as any;

describe('Dashboard Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard heading', async () => {
    // Mock successful API response
    const mockData = {
      data: {
        data: [
          { market: 'BTC-EUR', base: 'BTC', price: 45000, change24h: 2.5 },
        ],
      },
    };
    mockedAxios.get.mockResolvedValue(mockData);

    render(<Dashboard />);

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: /trading dashboard/i })
      ).toBeInTheDocument();
    });
  });

  it('shows loading state initially', () => {
    render(<Dashboard />);
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText(/loading dashboard/i)).toBeInTheDocument();
  });

  it('displays error message when API fails', async () => {
    mockedAxios.get.mockRejectedValueOnce(new Error('API Error'));

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
  });

  it('displays market data when loaded successfully', async () => {
    const mockData = {
      data: {
        data: [
          {
            market: 'BTC-EUR',
            base: 'BTC',
            price: 45000,
            change24h: 2.5,
          },
        ],
      },
    };

    mockedAxios.get
      .mockResolvedValueOnce(mockData) // markets
      .mockResolvedValueOnce({ data: { data: [] } }); // balances

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('BTC-EUR')).toBeInTheDocument();
    });
  });

  it('has proper accessibility attributes', () => {
    render(<Dashboard />);

    const main = screen.getByRole('main');
    expect(main).toHaveClass('dashboard');

    // Check for proper ARIA labels
    const loadingStatus = screen.getByRole('status');
    expect(loadingStatus).toHaveAttribute('aria-label');
  });
});
