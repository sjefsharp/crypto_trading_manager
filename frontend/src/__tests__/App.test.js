import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import Navbar from "../components/Navbar";
import TradingModeSettings from "../components/TradingModeSettings";
import { MemoryRouter } from "react-router-dom";
import axios from "axios";

// Mock axios for components that use it
jest.mock("axios");
const mockedAxios = axios;

describe("Navbar Component", () => {
  test("renders without crashing", () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );
    expect(screen.getByRole("navigation")).toBeInTheDocument();
  });

  test("renders navbar with title", () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );
    expect(screen.getByText("Crypto Trading Manager")).toBeInTheDocument();
  });

  test("renders main navigation links", () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );

    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Trading")).toBeInTheDocument();
    expect(screen.getByText("Market Data")).toBeInTheDocument();
    expect(screen.getByText("Portfolio")).toBeInTheDocument();
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });
});
