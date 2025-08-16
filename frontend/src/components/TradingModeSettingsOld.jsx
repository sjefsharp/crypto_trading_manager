import React, { useState, useEffect } from "react";
import axios from "axios";
import "./TradingModeSettings.css";

const TradingModeSettings = () => {
  const [tradingMode, setTradingMode] = useState({
    current_mode: "dry_run",
    dry_run_enabled: true,
    is_live_trading: false,
    warning_message: "",
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [pendingMode, setPendingMode] = useState("");

  useEffect(() => {
    fetchTradingModeStatus();
  }, []);

  const fetchTradingModeStatus = async () => {
    try {
      const response = await axios.get("/api/v1/trading-mode/status");
      setTradingMode(response.data);
    } catch (error) {
      console.error("Error fetching trading mode status:", error);
      setMessage("Error fetching trading mode status");
    }
  };

  const handleModeChange = async (newMode, forceDryRun = false) => {
    if (newMode === "live" && !forceDryRun) {
      // Show confirmation dialog for live mode
      setPendingMode(newMode);
      setShowConfirmDialog(true);
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await axios.post("/api/v1/trading-mode/set", {
        mode: newMode,
        force_dry_run: forceDryRun,
      });

      setTradingMode(response.data);
      setMessage(`Trading mode switched to ${newMode.toUpperCase()}`);
      setShowConfirmDialog(false);
      setPendingMode("");
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.message;
      setMessage(`Error switching mode: ${errorMessage}`);
      setShowConfirmDialog(false);
      setPendingMode("");
    } finally {
      setLoading(false);
    }
  };

  const handleEmergencyDryRun = async () => {
    setLoading(true);
    try {
      const response = await axios.post("/api/v1/trading-mode/enable-dry-run");
      setTradingMode((prev) => ({
        ...prev,
        dry_run_enabled: true,
        is_live_trading: false,
      }));
      setMessage("Emergency dry-run enabled for safety!");
      await fetchTradingModeStatus(); // Refresh status
    } catch (error) {
      setMessage("Error enabling emergency dry-run");
    } finally {
      setLoading(false);
    }
  };

  const getModeColor = (mode) => {
    switch (mode) {
      case "dry_run":
        return "#28a745"; // Green
      case "demo":
        return "#ffc107"; // Yellow
      case "live":
        return "#dc3545"; // Red
      default:
        return "#6c757d"; // Gray
    }
  };

  const getModeIcon = (mode) => {
    switch (mode) {
      case "dry_run":
        return "🧪";
      case "demo":
        return "🎮";
      case "live":
        return "⚡";
      default:
        return "❓";
    }
  };

  return (
    <div className="trading-mode-settings">
      <div className="mode-header">
        <h3>Trading Mode Settings</h3>
        <div
          className="current-mode-badge"
          style={{ backgroundColor: getModeColor(tradingMode.current_mode) }}
        >
          {getModeIcon(tradingMode.current_mode)}{" "}
          {tradingMode.current_mode.toUpperCase()}
        </div>
      </div>

      {tradingMode.warning_message && (
        <div className="warning-message">⚠️ {tradingMode.warning_message}</div>
      )}

      <div className="mode-controls">
        <div className="mode-buttons">
          <button
            className={`mode-button ${
              tradingMode.current_mode === "dry_run" ? "active" : ""
            }`}
            onClick={() => handleModeChange("dry_run")}
            disabled={loading}
          >
            🧪 Dry Run
            <span className="mode-description">Safe testing mode</span>
          </button>

          <button
            className={`mode-button ${
              tradingMode.current_mode === "demo" ? "active" : ""
            }`}
            onClick={() => handleModeChange("demo")}
            disabled={loading}
          >
            🎮 Demo
            <span className="mode-description">Realistic simulation</span>
          </button>

          <button
            className={`mode-button ${
              tradingMode.current_mode === "live" ? "active" : ""
            } live-mode`}
            onClick={() => handleModeChange("live")}
            disabled={loading}
          >
            ⚡ Live Trading
            <span className="mode-description">Real money trades</span>
          </button>
        </div>

        <div className="safety-controls">
          <button
            className="emergency-button"
            onClick={handleEmergencyDryRun}
            disabled={loading}
          >
            🚨 Emergency Dry-Run
          </button>
        </div>
      </div>

      <div className="mode-info">
        <div className="info-item">
          <strong>Dry Run Enabled:</strong>{" "}
          {tradingMode.dry_run_enabled ? "Yes" : "No"}
        </div>
        <div className="info-item">
          <strong>Live Trading:</strong>{" "}
          {tradingMode.is_live_trading ? "Active" : "Disabled"}
        </div>
      </div>

      {message && (
        <div
          className={`message ${
            message.includes("Error") ? "error" : "success"
          }`}
        >
          {message}
        </div>
      )}

      {loading && <div className="loading">Updating trading mode...</div>}

      {/* Confirmation Dialog for Live Mode */}
      {showConfirmDialog && (
        <div className="confirm-dialog-overlay">
          <div className="confirm-dialog">
            <h4>⚠️ Enable Live Trading?</h4>
            <p>
              You are about to enable LIVE TRADING mode. This will use real
              money and execute actual trades on the exchange.
            </p>
            <p>
              <strong>Are you absolutely sure you want to proceed?</strong>
            </p>
            <div className="dialog-buttons">
              <button
                className="confirm-live"
                onClick={() => handleModeChange(pendingMode, false)}
              >
                Yes, Enable Live Trading
              </button>
              <button
                className="confirm-safe"
                onClick={() => handleModeChange(pendingMode, true)}
              >
                Use Live Mode with Dry-Run Safety
              </button>
              <button
                className="cancel"
                onClick={() => {
                  setShowConfirmDialog(false);
                  setPendingMode("");
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TradingModeSettings;
