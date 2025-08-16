import React from "react";
import { Link, useLocation } from "react-router-dom";
import { NavbarProps } from "@/types";

const Navbar: React.FC<NavbarProps> = () => {
  const location = useLocation();

  const isActive = (path: string): boolean => {
    return location.pathname === path;
  };

  const navigationItems = [
    { path: "/", label: "Dashboard", icon: "📊" },
    { path: "/trading", label: "Trading", icon: "📈" },
    { path: "/market", label: "Market Data", icon: "📋" },
    { path: "/portfolio", label: "Portfolio", icon: "💼" },
    { path: "/api-keys", label: "API Keys", icon: "🔑" },
    { path: "/settings", label: "Settings", icon: "⚙️" },
  ];

  return (
    <header className="navbar" role="banner">
      <div className="navbar-content">
        <div className="navbar-brand">
          <h1 className="brand-title">
            <span className="brand-icon" aria-hidden="true">
              ₿
            </span>
            <span>Crypto Trading Manager</span>
          </h1>
        </div>

        <nav
          className="navbar-nav"
          role="navigation"
          aria-label="Main navigation"
        >
          <ul className="nav-list" role="menubar">
            {navigationItems.map(({ path, label, icon }) => (
              <li key={path} role="none">
                <Link
                  to={path}
                  className={`nav-link ${
                    isActive(path) ? "nav-link--active" : ""
                  }`}
                  role="menuitem"
                  aria-current={isActive(path) ? "page" : undefined}
                >
                  <span className="nav-icon" aria-hidden="true">
                    {icon}
                  </span>
                  <span className="nav-label">{label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <div className="navbar-actions">
          <button
            className="btn btn--secondary theme-toggle"
            aria-label="Toggle dark mode"
            type="button"
          >
            <span aria-hidden="true">🌙</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
