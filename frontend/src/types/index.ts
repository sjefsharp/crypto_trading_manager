import { ChangeEvent, FormEvent } from 'react';

// API Key related types
export interface APIKeyData {
  id: number;
  name: string;
  exchange: string;
  is_active: boolean;
  created_at: string;
  last_used?: string;
}

export interface ExchangeStatus {
  [key: string]: {
    configured: boolean;
    testing: boolean;
  };
}

export interface ExchangeInfo {
  [key: string]: {
    name: string;
    url: string;
    apiUrl: string;
    description: string;
    implemented: boolean;
  };
}

// Market Data types
export interface MarketDataPoint {
  timestamp: string;
  price: number;
  volume: number;
  symbol: string;
}

export interface CryptoPair {
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  price: number;
  change24h: number;
  volume24h: number;
}

export interface Market {
  market: string;
  base: string;
  quote: string;
  status: string;
  minOrderInQuoteAsset: string;
  minOrderInBaseAsset: string;
  maxOrderInQuoteAsset?: string;
  maxOrderInBaseAsset?: string;
  orderTypes: string[];
}

export interface TickerData {
  market: string;
  price: string;
  last: number;
  high: number;
  low: number;
  volume: number;
  bid: number;
  ask: number;
  timestamp: number;
}

export interface CandleData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// Portfolio types
export interface PortfolioHolding {
  symbol: string;
  amount: number;
  value: number;
  allocation: number;
}

export interface PortfolioPosition {
  id: number;
  symbol: string;
  quantity: number;
  average_price: number;
  current_price: number;
  unrealized_pnl: number;
}

export interface Portfolio {
  id: number;
  name: string;
  total_value: number;
  holdings: PortfolioHolding[];
  positions?: PortfolioPosition[];
  trades?: Trade[];
  last_updated: string;
  is_active: boolean;
  description: string;
}

export interface Balance {
  symbol: string;
  name: string;
  available: string;
  in_order: string;
  inOrder: string; // Alias for in_order
  value: number;
  change24h: number;
}

export interface Trade {
  id: string;
  orderId: string;
  market: string;
  side: 'buy' | 'sell';
  order_type: string;
  orderType: string;
  quantity: number;
  amount: string;
  price: number | null;
  status: string;
  created_at: string;
}

export interface Transaction {
  id: string;
  market: string;
  side: 'buy' | 'sell';
  amount: string;
  price: string;
  status: string;
  createdAt: string;
}

// Trading types
export interface TradingMode {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  parameters: Record<string, any>;
}

export interface OrderFormData {
  market: string;
  side: 'buy' | 'sell';
  orderType: 'market' | 'limit';
  amount: string;
  price: string;
}

// API Key interfaces
export interface APIKey {
  id: string;
  name: string;
  apiKey: string;
  exchange: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface APIKeyFormData {
  name: string;
  apiKey: string;
  apiSecret: string;
  exchange: string;
  isActive: boolean;
}

// Portfolio interfaces
export interface Portfolio {
  userId: string;
  totalValue: number;
  lastUpdated: string;
}

export interface PortfolioItem {
  symbol: string;
  name: string;
  amount: number;
  value: number;
  allocation: number;
}

export interface PortfolioStats {
  totalValue: number;
  totalChange24h: number;
  changePercentage: number;
  totalAssets: number;
  totalInOrder: number;
}

// Component Props types
export interface DashboardProps {
  className?: string;
}

export interface NavbarProps {
  onNavigate?: (page: string) => void;
}

// Event Handler types
export type InputChangeHandler = (
  e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
) => void;
export type CheckboxChangeHandler = (e: ChangeEvent<HTMLInputElement>) => void;
export type FormSubmitHandler = (e: FormEvent<HTMLFormElement>) => void;

// API Response types
export interface APIResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Error types
export interface APIError {
  message: string;
  code?: string;
  details?: Record<string, any>;
  response?: {
    data?: {
      detail?: string;
    };
  };
}
