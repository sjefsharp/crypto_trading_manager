import '@testing-library/jest-dom';
import { beforeEach } from 'vitest';

// Global test setup
beforeEach(() => {
  // Reset any mocks or cleanup between tests
});

// Mock environment variables if needed
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
});

// Mock IntersectionObserver
declare global {
  interface Window {
    IntersectionObserver: typeof IntersectionObserver;
  }
}

(globalThis as unknown as Window).IntersectionObserver = class {
  root = null;
  rootMargin = '';
  thresholds = [];

  constructor() {}
  observe() {}
  disconnect() {}
  unobserve() {}
  takeRecords() {
    return [];
  }
};
