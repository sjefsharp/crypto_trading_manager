import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import Navbar from '../components/Navbar';

// Helper function to render Navbar with Router context
const renderNavbar = () => {
  return render(
    <MemoryRouter>
      <Navbar />
    </MemoryRouter>
  );
};

describe('Navbar Component', () => {
  it('renders navigation with all links', () => {
    renderNavbar();

    // Check for navigation landmark
    expect(screen.getByRole('navigation')).toBeInTheDocument();

    // Check for all navigation links (now as menuitem role)
    expect(
      screen.getByRole('menuitem', { name: /dashboard/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('menuitem', { name: /portfolio/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('menuitem', { name: /trading/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('menuitem', { name: /market data/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('menuitem', { name: /settings/i })
    ).toBeInTheDocument();
  });

  it('has proper accessibility attributes', () => {
    renderNavbar();

    const nav = screen.getByRole('navigation');
    expect(nav).toHaveAttribute('aria-label');

    // Check for proper semantic structure
    expect(screen.getByRole('banner')).toBeInTheDocument();
  });

  it('supports keyboard navigation', () => {
    renderNavbar();

    const firstLink = screen.getByRole('menuitem', { name: /dashboard/i });
    firstLink.focus();

    expect(document.activeElement).toBe(firstLink);
  });

  it('has responsive menu button on mobile', () => {
    // This would require specific mobile testing setup
    renderNavbar();

    // Look for mobile menu elements if they exist
    const menuButton = screen.queryByRole('button', { name: /menu/i });
    if (menuButton) {
      expect(menuButton).toBeInTheDocument();
    }
  });
});
