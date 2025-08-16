import { render } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Dashboard from '../components/Dashboard';

// Mock axios completely
vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { data: [] } })),
  },
}));

describe('Dashboard Component', () => {
  it('renders without crashing', () => {
    const { container } = render(<Dashboard />);
    expect(container).toBeTruthy();
  });

  it('renders with className prop', () => {
    const { container } = render(<Dashboard className='test-class' />);
    expect(container.firstChild).toHaveClass('dashboard', 'test-class');
  });
});
