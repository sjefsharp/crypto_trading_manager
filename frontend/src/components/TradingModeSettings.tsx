import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  TradingMode,
  APIError,
  InputChangeHandler,
  FormSubmitHandler,
} from '@/types';

interface TradingModeFormData {
  name: string;
  description: string;
  is_active: boolean;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  parameters: {
    max_trade_amount: string;
    stop_loss_percentage: string;
    take_profit_percentage: string;
    max_open_orders: string;
    min_profit_threshold: string;
  };
}

const TradingModeSettings: React.FC = () => {
  const [tradingModes, setTradingModes] = useState<TradingMode[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showForm, setShowForm] = useState<boolean>(false);
  const [editingMode, setEditingMode] = useState<TradingMode | null>(null);
  const [formData, setFormData] = useState<TradingModeFormData>({
    name: '',
    description: '',
    is_active: true,
    risk_level: 'MEDIUM',
    parameters: {
      max_trade_amount: '100',
      stop_loss_percentage: '5',
      take_profit_percentage: '10',
      max_open_orders: '3',
      min_profit_threshold: '1',
    },
  });

  useEffect(() => {
    fetchTradingModes();
  }, []);

  const fetchTradingModes = async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.get<{ data: TradingMode[] }>(
        '/api/v1/settings/trading-modes'
      );
      setTradingModes(response.data.data);
    } catch (err) {
      const error = err as APIError;
      setError(
        'Failed to fetch trading modes: ' + (error.message || 'Unknown error')
      );
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange: InputChangeHandler = e => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;

    if (name.startsWith('parameters.')) {
      const paramName = name.split('.')[1];
      setFormData(prev => ({
        ...prev,
        parameters: {
          ...prev.parameters,
          [paramName]: value,
        },
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value,
      }));
    }
  };

  const validateForm = (): boolean => {
    if (!formData.name.trim()) {
      setError('Please enter a name for this trading mode');
      return false;
    }
    if (!formData.description.trim()) {
      setError('Please enter a description');
      return false;
    }

    // Validate parameters
    const { parameters } = formData;
    if (parseFloat(parameters.max_trade_amount) <= 0) {
      setError('Maximum trade amount must be greater than 0');
      return false;
    }
    if (
      parseFloat(parameters.stop_loss_percentage) <= 0 ||
      parseFloat(parameters.stop_loss_percentage) >= 100
    ) {
      setError('Stop loss percentage must be between 0 and 100');
      return false;
    }
    if (parseFloat(parameters.take_profit_percentage) <= 0) {
      setError('Take profit percentage must be greater than 0');
      return false;
    }
    if (parseInt(parameters.max_open_orders) <= 0) {
      setError('Maximum open orders must be greater than 0');
      return false;
    }

    return true;
  };

  const handleSubmit: FormSubmitHandler = async e => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      setError(null);
      setSuccess(null);

      const submitData = {
        ...formData,
        parameters: {
          ...formData.parameters,
          max_trade_amount: parseFloat(formData.parameters.max_trade_amount),
          stop_loss_percentage: parseFloat(
            formData.parameters.stop_loss_percentage
          ),
          take_profit_percentage: parseFloat(
            formData.parameters.take_profit_percentage
          ),
          max_open_orders: parseInt(formData.parameters.max_open_orders),
          min_profit_threshold: parseFloat(
            formData.parameters.min_profit_threshold
          ),
        },
      };

      if (editingMode) {
        const response = await axios.put<{ data: TradingMode }>(
          `/api/v1/settings/trading-modes/${editingMode.id}`,
          submitData
        );
        setTradingModes(prev =>
          prev.map(mode =>
            mode.id === editingMode.id ? response.data.data : mode
          )
        );
        setSuccess('Trading mode updated successfully');
      } else {
        const response = await axios.post<{ data: TradingMode }>(
          '/api/v1/settings/trading-modes',
          submitData
        );
        setTradingModes(prev => [...prev, response.data.data]);
        setSuccess('Trading mode created successfully');
      }

      resetForm();
    } catch (err) {
      const error = err as APIError;
      setError(
        error.response?.data?.detail ||
          error.message ||
          `Failed to ${editingMode ? 'update' : 'create'} trading mode`
      );
    }
  };

  const resetForm = (): void => {
    setFormData({
      name: '',
      description: '',
      is_active: true,
      risk_level: 'MEDIUM',
      parameters: {
        max_trade_amount: '100',
        stop_loss_percentage: '5',
        take_profit_percentage: '10',
        max_open_orders: '3',
        min_profit_threshold: '1',
      },
    });
    setEditingMode(null);
    setShowForm(false);
  };

  const handleEdit = (mode: TradingMode): void => {
    setFormData({
      name: mode.name,
      description: mode.description,
      is_active: mode.is_active,
      risk_level: mode.risk_level,
      parameters: {
        max_trade_amount: mode.parameters.max_trade_amount?.toString() || '100',
        stop_loss_percentage:
          mode.parameters.stop_loss_percentage?.toString() || '5',
        take_profit_percentage:
          mode.parameters.take_profit_percentage?.toString() || '10',
        max_open_orders: mode.parameters.max_open_orders?.toString() || '3',
        min_profit_threshold:
          mode.parameters.min_profit_threshold?.toString() || '1',
      },
    });
    setEditingMode(mode);
    setShowForm(true);
  };

  const handleDelete = async (id: number): Promise<void> => {
    if (
      !window.confirm(
        'Are you sure you want to delete this trading mode? This action cannot be undone.'
      )
    ) {
      return;
    }

    try {
      setError(null);
      await axios.delete(`/api/v1/settings/trading-modes/${id}`);
      setTradingModes(prev => prev.filter(mode => mode.id !== id));
      setSuccess('Trading mode deleted successfully');
    } catch (err) {
      const error = err as APIError;
      setError(
        error.response?.data?.detail ||
          error.message ||
          'Failed to delete trading mode'
      );
    }
  };

  const toggleStatus = async (id: number, isActive: boolean): Promise<void> => {
    try {
      setError(null);
      const response = await axios.patch<{ data: TradingMode }>(
        `/api/v1/settings/trading-modes/${id}`,
        {
          is_active: !isActive,
        }
      );
      setTradingModes(prev =>
        prev.map(mode => (mode.id === id ? response.data.data : mode))
      );
      setSuccess(
        `Trading mode ${!isActive ? 'activated' : 'deactivated'} successfully`
      );
    } catch (err) {
      const error = err as APIError;
      setError(
        error.response?.data?.detail ||
          error.message ||
          'Failed to update trading mode status'
      );
    }
  };

  const getRiskLevelBadge = (level: string): string => {
    switch (level) {
      case 'LOW':
        return 'badge badge--success';
      case 'MEDIUM':
        return 'badge badge--warning';
      case 'HIGH':
        return 'badge badge--error';
      default:
        return 'badge badge--neutral';
    }
  };

  if (loading) {
    return (
      <main className='trading-mode-settings' aria-live='polite'>
        <div
          className='loading-container'
          role='status'
          aria-label='Loading trading mode settings'
        >
          <div className='spinner' aria-hidden='true'></div>
          <span className='sr-only'>Loading trading mode settings...</span>
        </div>
      </main>
    );
  }

  return (
    <main className='trading-mode-settings'>
      <div className='container'>
        <header className='settings-header'>
          <h1>Trading Mode Settings</h1>
          <p className='subtitle'>
            Configure automated trading strategies and risk parameters
          </p>
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

        {success && (
          <div className='alert alert--success' role='alert'>
            <strong>Success:</strong> {success}
            <button
              className='btn btn--secondary'
              onClick={() => setSuccess(null)}
              aria-label='Dismiss success message'
              type='button'
            >
              ×
            </button>
          </div>
        )}

        <div className='grid grid-cols-1 lg:grid-cols-3 gap-6'>
          {/* Trading Modes List */}
          <section
            className='lg:col-span-2 card'
            aria-labelledby='trading-modes-heading'
          >
            <header className='card-header'>
              <h2 id='trading-modes-heading'>Trading Modes</h2>
              <p className='text-muted'>
                Manage your automated trading strategies
              </p>
              <button
                className='btn btn--primary'
                onClick={() => setShowForm(true)}
                type='button'
              >
                Create New Mode
              </button>
            </header>

            {tradingModes.length === 0 ? (
              <div className='empty-state'>
                <h3>No Trading Modes Found</h3>
                <p className='text-muted'>
                  Create your first trading mode to start automated trading
                </p>
                <button
                  className='btn btn--primary'
                  onClick={() => setShowForm(true)}
                  type='button'
                >
                  Create Trading Mode
                </button>
              </div>
            ) : (
              <div className='trading-modes-grid'>
                {tradingModes.map(mode => (
                  <article key={mode.id} className='trading-mode-card'>
                    <header className='mode-header'>
                      <h3 className='mode-name'>{mode.name}</h3>
                      <div className='mode-badges'>
                        <span className={getRiskLevelBadge(mode.risk_level)}>
                          {mode.risk_level}
                        </span>
                        <button
                          className={`status status--${
                            mode.is_active ? 'active' : 'inactive'
                          }`}
                          onClick={() => toggleStatus(mode.id, mode.is_active)}
                          type='button'
                          aria-label={`${
                            mode.is_active ? 'Deactivate' : 'Activate'
                          } ${mode.name}`}
                        >
                          {mode.is_active ? 'Active' : 'Inactive'}
                        </button>
                      </div>
                    </header>

                    <div className='mode-description'>
                      <p>{mode.description}</p>
                    </div>

                    <div className='mode-parameters'>
                      <h4 className='parameters-title'>Parameters</h4>
                      <dl className='parameter-list'>
                        <div className='parameter-item'>
                          <dt>Max Trade Amount</dt>
                          <dd>€{mode.parameters.max_trade_amount}</dd>
                        </div>
                        <div className='parameter-item'>
                          <dt>Stop Loss</dt>
                          <dd>{mode.parameters.stop_loss_percentage}%</dd>
                        </div>
                        <div className='parameter-item'>
                          <dt>Take Profit</dt>
                          <dd>{mode.parameters.take_profit_percentage}%</dd>
                        </div>
                        <div className='parameter-item'>
                          <dt>Max Open Orders</dt>
                          <dd>{mode.parameters.max_open_orders}</dd>
                        </div>
                      </dl>
                    </div>

                    <footer className='mode-actions'>
                      <button
                        className='btn btn--secondary btn--sm'
                        onClick={() => handleEdit(mode)}
                        type='button'
                        aria-label={`Edit ${mode.name}`}
                      >
                        Edit
                      </button>
                      <button
                        className='btn btn--error btn--sm'
                        onClick={() => handleDelete(mode.id)}
                        type='button'
                        aria-label={`Delete ${mode.name}`}
                      >
                        Delete
                      </button>
                    </footer>
                  </article>
                ))}
              </div>
            )}
          </section>

          {/* Create/Edit Form */}
          <section className='card' aria-labelledby='form-heading'>
            <header className='card-header'>
              <h2 id='form-heading'>
                {editingMode ? 'Edit Trading Mode' : 'Create Trading Mode'}
              </h2>
              <p className='text-muted'>
                {editingMode
                  ? 'Update trading strategy settings'
                  : 'Configure a new automated trading strategy'}
              </p>
            </header>

            {showForm ? (
              <form onSubmit={handleSubmit} noValidate>
                <div className='form-group'>
                  <label htmlFor='name' className='form-label'>
                    Mode Name
                  </label>
                  <input
                    type='text'
                    id='name'
                    name='name'
                    className='form-input'
                    value={formData.name}
                    onChange={handleInputChange}
                    placeholder='e.g., Conservative DCA'
                    required
                    aria-describedby='name-help'
                  />
                  <div id='name-help' className='form-help text-muted'>
                    A descriptive name for this trading strategy
                  </div>
                </div>

                <div className='form-group'>
                  <label htmlFor='description' className='form-label'>
                    Description
                  </label>
                  <textarea
                    id='description'
                    name='description'
                    className='form-textarea'
                    value={formData.description}
                    onChange={handleInputChange}
                    placeholder='Describe this trading strategy...'
                    rows={3}
                    required
                    aria-describedby='description-help'
                  />
                  <div id='description-help' className='form-help text-muted'>
                    Explain what this trading mode does and when to use it
                  </div>
                </div>

                <div className='form-group'>
                  <label htmlFor='risk_level' className='form-label'>
                    Risk Level
                  </label>
                  <select
                    id='risk_level'
                    name='risk_level'
                    className='form-select'
                    value={formData.risk_level}
                    onChange={handleInputChange}
                    required
                    aria-describedby='risk-help'
                  >
                    <option value='LOW'>Low Risk</option>
                    <option value='MEDIUM'>Medium Risk</option>
                    <option value='HIGH'>High Risk</option>
                  </select>
                  <div id='risk-help' className='form-help text-muted'>
                    Select the risk level for this trading strategy
                  </div>
                </div>

                <fieldset className='form-fieldset'>
                  <legend className='form-legend'>Trading Parameters</legend>

                  <div className='form-group'>
                    <label htmlFor='max_trade_amount' className='form-label'>
                      Maximum Trade Amount (EUR)
                    </label>
                    <input
                      type='number'
                      id='max_trade_amount'
                      name='parameters.max_trade_amount'
                      className='form-input'
                      value={formData.parameters.max_trade_amount}
                      onChange={handleInputChange}
                      min='1'
                      step='0.01'
                      required
                      aria-describedby='max-trade-help'
                    />
                    <div id='max-trade-help' className='form-help text-muted'>
                      Maximum amount to use in a single trade
                    </div>
                  </div>

                  <div className='form-group'>
                    <label
                      htmlFor='stop_loss_percentage'
                      className='form-label'
                    >
                      Stop Loss Percentage (%)
                    </label>
                    <input
                      type='number'
                      id='stop_loss_percentage'
                      name='parameters.stop_loss_percentage'
                      className='form-input'
                      value={formData.parameters.stop_loss_percentage}
                      onChange={handleInputChange}
                      min='0.1'
                      max='50'
                      step='0.1'
                      required
                      aria-describedby='stop-loss-help'
                    />
                    <div id='stop-loss-help' className='form-help text-muted'>
                      Automatically sell when loss reaches this percentage
                    </div>
                  </div>

                  <div className='form-group'>
                    <label
                      htmlFor='take_profit_percentage'
                      className='form-label'
                    >
                      Take Profit Percentage (%)
                    </label>
                    <input
                      type='number'
                      id='take_profit_percentage'
                      name='parameters.take_profit_percentage'
                      className='form-input'
                      value={formData.parameters.take_profit_percentage}
                      onChange={handleInputChange}
                      min='0.1'
                      step='0.1'
                      required
                      aria-describedby='take-profit-help'
                    />
                    <div id='take-profit-help' className='form-help text-muted'>
                      Automatically sell when profit reaches this percentage
                    </div>
                  </div>

                  <div className='form-group'>
                    <label htmlFor='max_open_orders' className='form-label'>
                      Maximum Open Orders
                    </label>
                    <input
                      type='number'
                      id='max_open_orders'
                      name='parameters.max_open_orders'
                      className='form-input'
                      value={formData.parameters.max_open_orders}
                      onChange={handleInputChange}
                      min='1'
                      max='20'
                      step='1'
                      required
                      aria-describedby='max-orders-help'
                    />
                    <div id='max-orders-help' className='form-help text-muted'>
                      Maximum number of concurrent open orders
                    </div>
                  </div>

                  <div className='form-group'>
                    <label
                      htmlFor='min_profit_threshold'
                      className='form-label'
                    >
                      Minimum Profit Threshold (EUR)
                    </label>
                    <input
                      type='number'
                      id='min_profit_threshold'
                      name='parameters.min_profit_threshold'
                      className='form-input'
                      value={formData.parameters.min_profit_threshold}
                      onChange={handleInputChange}
                      min='0.01'
                      step='0.01'
                      required
                      aria-describedby='min-profit-help'
                    />
                    <div id='min-profit-help' className='form-help text-muted'>
                      Only execute trades with potential profit above this
                      amount
                    </div>
                  </div>
                </fieldset>

                <div className='form-group'>
                  <label className='checkbox-label'>
                    <input
                      type='checkbox'
                      name='is_active'
                      checked={formData.is_active}
                      onChange={handleInputChange}
                    />
                    <span className='checkbox-text'>Active</span>
                  </label>
                  <div className='form-help text-muted'>
                    Only active trading modes will be used for automated trading
                  </div>
                </div>

                <div className='form-actions'>
                  <button
                    type='submit'
                    className='btn btn--primary'
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className='spinner' aria-hidden='true'></span>
                        <span>
                          {editingMode ? 'Updating...' : 'Creating...'}
                        </span>
                      </>
                    ) : editingMode ? (
                      'Update Trading Mode'
                    ) : (
                      'Create Trading Mode'
                    )}
                  </button>
                  <button
                    type='button'
                    className='btn btn--secondary'
                    onClick={resetForm}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <div className='empty-form-state'>
                <p className='text-muted'>
                  Click "Create New Mode" to get started
                </p>
                <button
                  className='btn btn--primary'
                  onClick={() => setShowForm(true)}
                  type='button'
                >
                  Create Trading Mode
                </button>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
};

export default TradingModeSettings;
