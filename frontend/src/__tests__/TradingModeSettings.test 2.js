import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import TradingModeSettings from '../components/TradingModeSettings';

// Mock axios
jest.mock('axios');
const mockedAxios = axios;

describe('TradingModeSettings Component', () => {
  beforeEach(() => {
    mockedAxios.get.mockClear();
    mockedAxios.post.mockClear();
  });

  const mockTradingModeStatus = {
    current_mode: 'dry_run',
    dry_run_enabled: true,
    is_live_trading: false,
    warning_message: '⚠️ DRY RUN MODE ACTIEF - Geen echte trades!'
  };

  test('renders trading mode settings component', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockTradingModeStatus });

    render(<TradingModeSettings />);

    expect(screen.getByText('Trading Mode Settings')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('DRY_RUN')).toBeInTheDocument();
      expect(screen.getByText('🧪 Dry Run')).toBeInTheDocument();
      expect(screen.getByText('🎮 Demo')).toBeInTheDocument();
      expect(screen.getByText('⚡ Live Trading')).toBeInTheDocument();
    });
  });

  test('displays warning message', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockTradingModeStatus });

    render(<TradingModeSettings />);

    await waitFor(() => {
      expect(screen.getByText(/DRY RUN MODE ACTIEF/)).toBeInTheDocument();
    });
  });

  test('displays current mode information', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockTradingModeStatus });

    render(<TradingModeSettings />);

    await waitFor(() => {
      expect(screen.getByText('Dry Run Enabled:')).toBeInTheDocument();
      expect(screen.getByText('Yes')).toBeInTheDocument();
      expect(screen.getByText('Live Trading:')).toBeInTheDocument();
      expect(screen.getByText('Disabled')).toBeInTheDocument();
    });
  });

  test('switches to demo mode successfully', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockTradingModeStatus });
    
    const demoModeResponse = {
      current_mode: 'demo',
      dry_run_enabled: true,
      is_live_trading: false,
      warning_message: '⚠️ DEMO MODE - Simulatie met realistische data'
    };
    mockedAxios.post.mockResolvedValue({ data: demoModeResponse });

    render(<TradingModeSettings />);

    await waitFor(() => {
      expect(screen.getByText('🎮 Demo')).toBeInTheDocument();
    });

    // Click demo mode button
    fireEvent.click(screen.getByText('🎮 Demo'));

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/trading-mode/set', {
        mode: 'demo',
        force_dry_run: false
      });
    });
  });

  test('shows confirmation dialog for live mode', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockTradingModeStatus });

    render(<TradingModeSettings />);

    await waitFor(() => {
      expect(screen.getByText('⚡ Live Trading')).toBeInTheDocument();
    });

    // Click live trading button
    fireEvent.click(screen.getByText('⚡ Live Trading'));

    // Should show confirmation dialog
    await waitFor(() => {
      expect(screen.getByText('⚠️ Enable Live Trading?')).toBeInTheDocument();
      expect(screen.getByText('Yes, Enable Live Trading')).toBeInTheDocument();
      expect(screen.getByText('Use Live Mode with Dry-Run Safety')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });
  });

  test('confirms live trading mode', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockTradingModeStatus });
    
    const liveModeResponse = {
      current_mode: 'live',
      dry_run_enabled: false,
      is_live_trading: true,
      warning_message: '🚨 LIVE TRADING ACTIVE - Real money trades!'
    };
    mockedAxios.post.mockResolvedValue({ data: liveModeResponse });

    render(<TradingModeSettings />);

    await waitFor(() => {
      expect(screen.getByText('⚡ Live Trading')).toBeInTheDocument();
    });

    // Click live trading button
    fireEvent.click(screen.getByText('⚡ Live Trading'));

    // Confirm live trading
    await waitFor(() => {
      expect(screen.getByText('Yes, Enable Live Trading')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('Yes, Enable Live Trading'));

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/trading-mode/set', {
        mode: 'live',
        force_dry_run: false
      });
    });
  });

  test('confirms live trading with dry-run safety', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockTradingModeStatus });
    
    const safeLiveModeResponse = {
      current_mode: 'live',
      dry_run_enabled: true,
      is_live_trading: false,
      warning_message: '⚠️ LIVE MODE with DRY RUN safety enabled'
    };
    mockedAxios.post.mockResolvedValue({ data: safeLiveModeResponse });

    render(<TradingModeSettings />);

    await waitFor(() => {
      expect(screen.getByText('⚡ Live Trading')).toBeInTheDocument();
    });

    // Click live trading button
    fireEvent.click(screen.getByText('⚡ Live Trading'));

    // Use safe mode
    await waitFor(() => {
      expect(screen.getByText('Use Live Mode with Dry-Run Safety')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('Use Live Mode with Dry-Run Safety'));

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/trading-mode/set', {
        mode: 'live',
        force_dry_run: true
      });
    });
  });

  test('cancels live trading confirmation', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockTradingModeStatus });

    render(<TradingModeSettings />);

    await waitFor(() => {
      expect(screen.getByText('⚡ Live Trading')).toBeInTheDocument();
    });

    // Click live trading button
    fireEvent.click(screen.getByText('⚡ Live Trading'));

    // Cancel
    await waitFor(() => {
      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('Cancel'));

    // Dialog should be closed
    await waitFor(() => {
      expect(screen.queryByText('⚠️ Enable Live Trading?')).not.toBeInTheDocument();
    });

    // No API call should be made
    expect(mockedAxios.post).not.toHaveBeenCalled();
  });

  test('activates emergency dry-run', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockTradingModeStatus });
    mockedAxios.post.mockResolvedValue({ 
      data: { 
        dry_run_enabled: true, 
        message: 'Emergency dry-run enabled for safety!' 
      } 
    });

    render(<TradingModeSettings />);

    await waitFor(() => {
      expect(screen.getByText('🚨 Emergency Dry-Run')).toBeInTheDocument();
    });

    // Click emergency button
    fireEvent.click(screen.getByText('🚨 Emergency Dry-Run'));

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/trading-mode/enable-dry-run');
      expect(screen.getByText('Emergency dry-run enabled for safety!')).toBeInTheDocument();
    });
  });

  test('handles API error when fetching status', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    mockedAxios.get.mockRejectedValue(new Error('Network error'));

    render(<TradingModeSettings />);

    await waitFor(() => {
      expect(screen.getByText('Error fetching trading mode status')).toBeInTheDocument();
    });

    consoleSpy.mockRestore();
  });

  test('handles API error when switching modes', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockTradingModeStatus });
    mockedAxios.post.mockRejectedValue({
      response: { data: { detail: 'API credentials required' } }
    });

    render(<TradingModeSettings />);

    await waitFor(() => {
      expect(screen.getByText('🎮 Demo')).toBeInTheDocument();
    });

    // Try to switch to demo mode
    fireEvent.click(screen.getByText('🎮 Demo'));

    await waitFor(() => {
      expect(screen.getByText(/Error switching mode: API credentials required/)).toBeInTheDocument();
    });
  });

  test('displays loading state during mode switch', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockTradingModeStatus });
    mockedAxios.post.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<TradingModeSettings />);

    await waitFor(() => {
      expect(screen.getByText('🎮 Demo')).toBeInTheDocument();
    });

    // Click demo mode button
    fireEvent.click(screen.getByText('🎮 Demo'));

    // Should show loading state
    await waitFor(() => {
      expect(screen.getByText('Updating trading mode...')).toBeInTheDocument();
    });
  });

  test('shows correct mode indicators and colors', async () => {
    // Test different modes
    const modes = [
      { mode: 'dry_run', icon: '🧪', color: '#28a745' },
      { mode: 'demo', icon: '🎮', color: '#ffc107' },
      { mode: 'live', icon: '⚡', color: '#dc3545' }
    ];

    for (const { mode, icon } of modes) {
      const modeStatus = {
        ...mockTradingModeStatus,
        current_mode: mode
      };
      
      mockedAxios.get.mockResolvedValue({ data: modeStatus });

      const { rerender } = render(<TradingModeSettings />);

      await waitFor(() => {
        expect(screen.getByText(mode.toUpperCase())).toBeInTheDocument();
        expect(screen.getByText(icon)).toBeInTheDocument();
      });

      rerender(<TradingModeSettings />);
    }
  });
});
