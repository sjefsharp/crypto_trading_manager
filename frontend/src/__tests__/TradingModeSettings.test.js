import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import axios from "axios";
import TradingModeSettings from "../components/TradingModeSettings";

// Mock axios
jest.mock("axios");
const mockedAxios = axios;

describe("TradingModeSettings Component", () => {
  beforeEach(() => {
    mockedAxios.get.mockClear();
    mockedAxios.post.mockClear();
  });

  const mockTradingModeStatus = {
    current_mode: "dry_run",
    dry_run_enabled: true,
    is_live_trading: false,
    warning_message: "⚠️ DRY RUN MODE ACTIEF - Geen echte trades!",
    can_trade_live: false,
    validation_message: "API credentials required",
  };

  test("renders trading mode settings component", async () => {
    mockedAxios.get.mockResolvedValue({ data: mockTradingModeStatus });

    render(<TradingModeSettings />);

    expect(screen.getByText("Trading Mode Settings")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("🧪 Dry Run")).toBeInTheDocument();
    });

    expect(screen.getByText("🎮 Demo")).toBeInTheDocument();
    expect(screen.getByText("⚡ Live Trading")).toBeInTheDocument();
    expect(screen.getByText("🚨 Emergency Dry-Run")).toBeInTheDocument();
  });

  test("switches to demo mode successfully", async () => {
    mockedAxios.get.mockResolvedValue({ data: mockTradingModeStatus });

    const demoModeResponse = {
      ...mockTradingModeStatus,
      current_mode: "demo",
      warning_message: "⚠️ DEMO MODE - Simulatie met realistische data",
      message: "Trading mode switched to DEMO",
    };
    mockedAxios.post.mockResolvedValue({ data: demoModeResponse });

    render(<TradingModeSettings />);

    await waitFor(() => {
      expect(screen.getByText("🎮 Demo")).toBeInTheDocument();
    });

    // Click demo mode button
    fireEvent.click(screen.getByText("🎮 Demo"));

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        "/api/v1/trading-mode/set",
        {
          mode: "demo",
          force_dry_run: false,
        }
      );
    });
  });

  test("activates emergency dry-run", async () => {
    mockedAxios.get.mockResolvedValue({ data: mockTradingModeStatus });
    mockedAxios.post.mockResolvedValue({
      data: {
        dry_run_enabled: true,
        message: "Emergency dry-run enabled for safety!",
      },
    });

    render(<TradingModeSettings />);

    await waitFor(() => {
      expect(screen.getByText("🚨 Emergency Dry-Run")).toBeInTheDocument();
    });

    // Click emergency button
    fireEvent.click(screen.getByText("🚨 Emergency Dry-Run"));

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        "/api/v1/trading-mode/enable-dry-run"
      );
    });
  });

  test("displays current mode correctly", async () => {
    mockedAxios.get.mockResolvedValue({ data: mockTradingModeStatus });

    render(<TradingModeSettings />);

    await waitFor(() => {
      // Check for the mode badge text using a more flexible approach
      expect(screen.getByText(/DRY_RUN/i)).toBeInTheDocument();
    });
  });

  test("shows warning message when in dry run mode", async () => {
    mockedAxios.get.mockResolvedValue({ data: mockTradingModeStatus });

    render(<TradingModeSettings />);

    await waitFor(() => {
      expect(screen.getByText(/DRY RUN MODE ACTIEF/)).toBeInTheDocument();
    });
  });
});
