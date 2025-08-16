import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  APIKey,
  APIKeyFormData,
  APIError,
  InputChangeHandler,
  FormSubmitHandler,
} from "@/types";

const APIKeySettings: React.FC = () => {
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showForm, setShowForm] = useState<boolean>(false);
  const [editingKey, setEditingKey] = useState<APIKey | null>(null);
  const [formData, setFormData] = useState<APIKeyFormData>({
    name: "",
    apiKey: "",
    apiSecret: "",
    exchange: "bitvavo",
    isActive: true,
  });

  useEffect(() => {
    fetchAPIKeys();
  }, []);

  const fetchAPIKeys = async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.get<{ data: APIKey[] }>(
        "/api/v1/settings/api-keys"
      );
      setApiKeys(response.data.data);
    } catch (err) {
      const error = err as APIError;
      setError(
        "Failed to fetch API keys: " + (error.message || "Unknown error")
      );
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange: InputChangeHandler = (e) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;

    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const validateForm = (): boolean => {
    if (!formData.name.trim()) {
      setError("Please enter a name for this API key");
      return false;
    }
    if (!formData.apiKey.trim()) {
      setError("Please enter your API key");
      return false;
    }
    if (!formData.apiSecret.trim()) {
      setError("Please enter your API secret");
      return false;
    }
    return true;
  };

  const handleSubmit: FormSubmitHandler = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      setError(null);
      setSuccess(null);

      if (editingKey) {
        const response = await axios.put<{ data: APIKey }>(
          `/api/v1/settings/api-keys/${editingKey.id}`,
          formData
        );
        setApiKeys((prev) =>
          prev.map((key) =>
            key.id === editingKey.id ? response.data.data : key
          )
        );
        setSuccess("API key updated successfully");
      } else {
        const response = await axios.post<{ data: APIKey }>(
          "/api/v1/settings/api-keys",
          formData
        );
        setApiKeys((prev) => [...prev, response.data.data]);
        setSuccess("API key added successfully");
      }

      resetForm();
    } catch (err) {
      const error = err as APIError;
      setError(
        error.response?.data?.detail ||
          error.message ||
          `Failed to ${editingKey ? "update" : "add"} API key`
      );
    }
  };

  const resetForm = (): void => {
    setFormData({
      name: "",
      apiKey: "",
      apiSecret: "",
      exchange: "bitvavo",
      isActive: true,
    });
    setEditingKey(null);
    setShowForm(false);
  };

  const handleEdit = (apiKey: APIKey): void => {
    setFormData({
      name: apiKey.name,
      apiKey: apiKey.apiKey,
      apiSecret: "", // Don't populate secret for security
      exchange: apiKey.exchange,
      isActive: apiKey.isActive,
    });
    setEditingKey(apiKey);
    setShowForm(true);
  };

  const handleDelete = async (id: string): Promise<void> => {
    if (
      !window.confirm(
        "Are you sure you want to delete this API key? This action cannot be undone."
      )
    ) {
      return;
    }

    try {
      setError(null);
      await axios.delete(`/api/v1/settings/api-keys/${id}`);
      setApiKeys((prev) => prev.filter((key) => key.id !== id));
      setSuccess("API key deleted successfully");
    } catch (err) {
      const error = err as APIError;
      setError(
        error.response?.data?.detail ||
          error.message ||
          "Failed to delete API key"
      );
    }
  };

  const toggleStatus = async (id: string, isActive: boolean): Promise<void> => {
    try {
      setError(null);
      const response = await axios.patch<{ data: APIKey }>(
        `/api/v1/settings/api-keys/${id}`,
        {
          isActive: !isActive,
        }
      );
      setApiKeys((prev) =>
        prev.map((key) => (key.id === id ? response.data.data : key))
      );
      setSuccess(
        `API key ${!isActive ? "activated" : "deactivated"} successfully`
      );
    } catch (err) {
      const error = err as APIError;
      setError(
        error.response?.data?.detail ||
          error.message ||
          "Failed to update API key status"
      );
    }
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

  const maskApiKey = (key: string): string => {
    if (key.length <= 8) return key;
    return (
      key.substring(0, 4) +
      "•".repeat(key.length - 8) +
      key.substring(key.length - 4)
    );
  };

  if (loading) {
    return (
      <main className="api-key-settings" aria-live="polite">
        <div
          className="loading-container"
          role="status"
          aria-label="Loading API key settings"
        >
          <div className="spinner" aria-hidden="true"></div>
          <span className="sr-only">Loading API key settings...</span>
        </div>
      </main>
    );
  }

  return (
    <main className="api-key-settings">
      <div className="container">
        <header className="settings-header">
          <h1>API Key Settings</h1>
          <p className="subtitle">
            Manage your cryptocurrency exchange API keys
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

        {success && (
          <div className="alert alert--success" role="alert">
            <strong>Success:</strong> {success}
            <button
              className="btn btn--secondary"
              onClick={() => setSuccess(null)}
              aria-label="Dismiss success message"
              type="button"
            >
              ×
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* API Keys List */}
          <section
            className="lg:col-span-2 card"
            aria-labelledby="api-keys-heading"
          >
            <header className="card-header">
              <h2 id="api-keys-heading">Your API Keys</h2>
              <p className="text-muted">
                Manage connections to cryptocurrency exchanges
              </p>
              <button
                className="btn btn--primary"
                onClick={() => setShowForm(true)}
                type="button"
              >
                Add New API Key
              </button>
            </header>

            {apiKeys.length === 0 ? (
              <div className="empty-state">
                <h3>No API Keys Found</h3>
                <p className="text-muted">
                  Add your first API key to start trading
                </p>
                <button
                  className="btn btn--primary"
                  onClick={() => setShowForm(true)}
                  type="button"
                >
                  Add API Key
                </button>
              </div>
            ) : (
              <div className="table-container">
                <table role="table" aria-label="API keys list">
                  <thead>
                    <tr>
                      <th scope="col">Name</th>
                      <th scope="col">Exchange</th>
                      <th scope="col">API Key</th>
                      <th scope="col">Status</th>
                      <th scope="col">Created</th>
                      <th scope="col">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {apiKeys.map((apiKey) => (
                      <tr key={apiKey.id}>
                        <td>
                          <strong>{apiKey.name}</strong>
                        </td>
                        <td>
                          <span className="exchange-badge">
                            {apiKey.exchange.charAt(0).toUpperCase() +
                              apiKey.exchange.slice(1)}
                          </span>
                        </td>
                        <td>
                          <code className="api-key-display">
                            {maskApiKey(apiKey.apiKey)}
                          </code>
                        </td>
                        <td>
                          <button
                            className={`status status--${
                              apiKey.isActive ? "active" : "inactive"
                            }`}
                            onClick={() =>
                              toggleStatus(apiKey.id, apiKey.isActive)
                            }
                            type="button"
                            aria-label={`${
                              apiKey.isActive ? "Deactivate" : "Activate"
                            } ${apiKey.name}`}
                          >
                            {apiKey.isActive ? "Active" : "Inactive"}
                          </button>
                        </td>
                        <td>
                          <time dateTime={apiKey.createdAt}>
                            {formatDate(apiKey.createdAt)}
                          </time>
                        </td>
                        <td>
                          <div className="action-buttons">
                            <button
                              className="btn btn--secondary btn--sm"
                              onClick={() => handleEdit(apiKey)}
                              type="button"
                              aria-label={`Edit ${apiKey.name}`}
                            >
                              Edit
                            </button>
                            <button
                              className="btn btn--error btn--sm"
                              onClick={() => handleDelete(apiKey.id)}
                              type="button"
                              aria-label={`Delete ${apiKey.name}`}
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {/* Add/Edit Form */}
          <section className="card" aria-labelledby="form-heading">
            <header className="card-header">
              <h2 id="form-heading">
                {editingKey ? "Edit API Key" : "Add New API Key"}
              </h2>
              <p className="text-muted">
                {editingKey
                  ? "Update your API key settings"
                  : "Connect to a cryptocurrency exchange"}
              </p>
            </header>

            {showForm ? (
              <form onSubmit={handleSubmit} noValidate>
                <div className="form-group">
                  <label htmlFor="name" className="form-label">
                    Display Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    className="form-input"
                    value={formData.name}
                    onChange={handleInputChange}
                    placeholder="e.g., Main Trading Account"
                    required
                    aria-describedby="name-help"
                  />
                  <div id="name-help" className="form-help text-muted">
                    A friendly name to identify this API key
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="exchange" className="form-label">
                    Exchange
                  </label>
                  <select
                    id="exchange"
                    name="exchange"
                    className="form-select"
                    value={formData.exchange}
                    onChange={handleInputChange}
                    required
                    aria-describedby="exchange-help"
                  >
                    <option value="bitvavo">Bitvavo</option>
                    <option value="binance">Binance</option>
                    <option value="kraken">Kraken</option>
                    <option value="coinbase">Coinbase Pro</option>
                  </select>
                  <div id="exchange-help" className="form-help text-muted">
                    Select the cryptocurrency exchange
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="apiKey" className="form-label">
                    API Key
                  </label>
                  <input
                    type="text"
                    id="apiKey"
                    name="apiKey"
                    className="form-input"
                    value={formData.apiKey}
                    onChange={handleInputChange}
                    placeholder="Enter your API key"
                    required
                    aria-describedby="api-key-help"
                  />
                  <div id="api-key-help" className="form-help text-muted">
                    Your public API key from the exchange
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="apiSecret" className="form-label">
                    API Secret
                  </label>
                  <input
                    type="password"
                    id="apiSecret"
                    name="apiSecret"
                    className="form-input"
                    value={formData.apiSecret}
                    onChange={handleInputChange}
                    placeholder={
                      editingKey
                        ? "Enter new secret to update"
                        : "Enter your API secret"
                    }
                    required={!editingKey}
                    aria-describedby="api-secret-help"
                  />
                  <div id="api-secret-help" className="form-help text-muted">
                    {editingKey
                      ? "Leave empty to keep current secret, or enter new secret to update"
                      : "Your private API secret from the exchange (encrypted when stored)"}
                  </div>
                </div>

                <div className="form-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      name="isActive"
                      checked={formData.isActive}
                      onChange={handleInputChange}
                    />
                    <span className="checkbox-text">Active</span>
                  </label>
                  <div className="form-help text-muted">
                    Only active API keys will be used for trading
                  </div>
                </div>

                <div className="form-actions">
                  <button
                    type="submit"
                    className="btn btn--primary"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner" aria-hidden="true"></span>
                        <span>{editingKey ? "Updating..." : "Adding..."}</span>
                      </>
                    ) : editingKey ? (
                      "Update API Key"
                    ) : (
                      "Add API Key"
                    )}
                  </button>
                  <button
                    type="button"
                    className="btn btn--secondary"
                    onClick={resetForm}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <div className="empty-form-state">
                <p className="text-muted">
                  Click "Add New API Key" to get started
                </p>
                <button
                  className="btn btn--primary"
                  onClick={() => setShowForm(true)}
                  type="button"
                >
                  Add API Key
                </button>
              </div>
            )}
          </section>
        </div>

        {/* Security Notice */}
        <section
          className="security-notice card card--warning"
          aria-labelledby="security-heading"
        >
          <header className="card-header">
            <h2 id="security-heading">Security Information</h2>
          </header>
          <div className="security-content">
            <ul className="security-list">
              <li>
                <strong>API Permissions:</strong> Only grant read and trade
                permissions. Never grant withdrawal permissions.
              </li>
              <li>
                <strong>IP Restrictions:</strong> Configure IP whitelisting on
                your exchange for additional security.
              </li>
              <li>
                <strong>Key Storage:</strong> API secrets are encrypted using
                industry-standard encryption before storage.
              </li>
              <li>
                <strong>Regular Rotation:</strong> Consider rotating your API
                keys regularly for optimal security.
              </li>
            </ul>
          </div>
        </section>
      </div>
    </main>
  );
};

export default APIKeySettings;
