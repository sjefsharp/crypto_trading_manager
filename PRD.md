# Enterprise Crypto Trading Manager - LLM Agent Ready Architecture

## 🎯 Project Overview

**Goal**: Enterprise-grade crypto trading manager with runtime exchange switching, dry-run capabilities, and comprehensive testing.

**Target Environment**: macOS Monterey (Late 2013 iMac) - No Docker/Brew dependencies

**Architecture Pattern**: Modular Python monolith with microservices patterns

---

## 📋 LLM Agent Instructions

### Phase 1: Environment Setup
1. Install Python 3.13 LTS + Poetry + Node.js 20 LTS + Redis
2. Initialize repository structure with GitHub integration
3. Configure development tooling and pre-commit hooks

### Phase 2: Core Infrastructure  
1. Setup FastAPI application with async SQLAlchemy
2. Implement exchange abstraction layer with CCXT
3. Create dry-run/simulation architecture

### Phase 3: Business Logic
1. Trading services with paper trading support
2. Portfolio management and risk engine
3. Real-time WebSocket integration

### Phase 4: Frontend & Testing
1. React 18 + TypeScript frontend with Mantine UI
2. Comprehensive testing setup (pytest + Vitest + Playwright)
3. CI/CD pipeline with GitHub Actions

---

## 🛠️ Tech Stack Specifications (Latest LTS Versions)

### Backend Stack
```yaml
Runtime: Python 3.13.3 (latest stable)
Web Framework: FastAPI 0.115.6
ASGI Server: Uvicorn 0.32.1
Database ORM: SQLAlchemy 2.0.36 (async)
Database: SQLite 3.47 + aiosqlite 0.20.0
Caching: Redis 7.4 LTS + aioredis 2.0.1
Message Queue: Celery 5.4.0 + Redis broker
HTTP Client: aiohttp 3.11.10
WebSocket: websockets 13.1
Exchange Integration: CCXT 4.4.38
Data Processing: pandas 2.2.3 + numpy 2.2.0
Validation: Pydantic 2.10.3
Migrations: Alembic 1.14.0
```

### Frontend Stack  
```yaml
Runtime: Node.js 22.12.0 LTS (Iron)
Framework: React 18.3.1
Build Tool: Vite 6.0.3
State Management: TanStack Query 5.62.2
UI Library: Mantine 7.15.1
TypeScript: 5.7.2
WebSocket: Native WebSocket API
Charting: Lightweight Charts 4.2.0
```

### Development & Testing
```yaml
Package Management: Poetry 1.8.5
Code Formatting: Black 24.10.0 + isort 5.13.2
Linting: Ruff 0.8.4 (replaces flake8)
Type Checking: MyPy 1.13.0
Testing Backend: pytest 8.3.4 + pytest-asyncio 0.24.0
Testing Frontend: Vitest 2.1.8 + Testing Library
E2E Testing: Playwright 1.49.1
Git Hooks: pre-commit 4.0.1
```

---

## 📁 Repository Structure (GitHub Ready)

```
crypto-trading-manager/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                 # Main CI pipeline
│   │   ├── security.yml           # Security scanning
│   │   └── release.yml            # Release automation
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── dependabot.yml
├── .pre-commit-config.yaml
├── pyproject.toml                 # Poetry dependencies & config
├── README.md                      # LLM Agent setup instructions
├── src/
│   └── trading_manager/
│       ├── __init__.py
│       ├── main.py               # FastAPI entry point
│       ├── core/                 # Shared infrastructure
│       │   ├── config.py         # Pydantic settings
│       │   ├── database.py       # SQLAlchemy setup
│       │   ├── redis_client.py   # Redis connection
│       │   ├── security.py       # Authentication
│       │   └── exceptions.py     # Custom exceptions
│       ├── models/               # SQLAlchemy models
│       │   ├── base.py
│       │   ├── trading.py
│       │   ├── portfolio.py
│       │   └── users.py
│       ├── schemas/              # Pydantic schemas
│       │   ├── trading.py        # API request/response
│       │   ├── portfolio.py
│       │   └── auth.py
│       ├── services/             # Business logic layer
│       │   ├── trading_service.py
│       │   ├── portfolio_service.py
│       │   ├── risk_service.py
│       │   ├── market_data_service.py
│       │   └── simulation/       # Dry-run services
│       │       ├── mock_exchange.py
│       │       ├── paper_trading.py
│       │       └── backtesting.py
│       ├── exchanges/            # Exchange integrations
│       │   ├── base.py          # Abstract base exchange
│       │   ├── factory.py       # Exchange factory pattern
│       │   ├── bitvavo/
│       │   │   ├── client.py    # CCXT wrapper
│       │   │   ├── websocket.py # Real-time data
│       │   │   └── config.py    # Exchange config
│       │   └── simulation/
│       │       └── mock_client.py
│       ├── api/                 # FastAPI routes
│       │   ├── deps.py         # Dependencies
│       │   ├── auth.py         # Authentication endpoints
│       │   ├── trading.py      # Trading endpoints
│       │   ├── portfolio.py    # Portfolio endpoints
│       │   ├── market_data.py  # Market data endpoints
│       │   └── admin.py        # Configuration endpoints
│       ├── websocket/          # Real-time communication
│       │   ├── manager.py      # Connection manager
│       │   └── handlers.py     # Message handlers
│       ├── tasks/              # Background tasks
│       │   ├── celery_app.py   # Celery configuration
│       │   ├── market_data.py  # Data collection tasks
│       │   └── portfolio.py    # Portfolio update tasks
│       └── utils/              # Utilities
│           ├── logging.py
│           ├── monitoring.py
│           └── helpers.py
├── frontend/                   # React application
│   ├── package.json
│   ├── vite.config.ts
│   ├── vitest.config.ts
│   ├── playwright.config.ts
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── components/
│   │   │   ├── trading/
│   │   │   ├── portfolio/
│   │   │   ├── charts/
│   │   │   └── common/
│   │   ├── pages/
│   │   │   ├── TradingPage.tsx
│   │   │   ├── PortfolioPage.tsx
│   │   │   └── SettingsPage.tsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useTrading.ts
│   │   │   └── usePortfolio.ts
│   │   ├── services/
│   │   │   ├── api.ts          # API client
│   │   │   ├── websocket.ts    # WebSocket client
│   │   │   └── types.ts        # TypeScript definitions
│   │   └── stores/
│   │       ├── tradingStore.ts
│   │       └── portfolioStore.ts
│   ├── tests/
│   │   ├── unit/              # Vitest unit tests
│   │   ├── components/        # Component tests
│   │   └── e2e/              # Playwright E2E tests
│   └── public/
├── tests/                     # Backend tests
│   ├── conftest.py           # Pytest configuration
│   ├── unit/
│   │   ├── test_services/
│   │   ├── test_exchanges/
│   │   ├── test_models/
│   │   └── test_simulation/
│   ├── integration/
│   │   ├── test_api/
│   │   ├── test_database/
│   │   └── test_websocket/
│   ├── e2e/
│   │   └── test_trading_flows/
│   └── fixtures/             # Test data & mocks
├── scripts/                  # Development scripts
│   ├── setup.py             # Environment setup
│   ├── migrate.py           # Database migrations
│   ├── seed_data.py         # Test data seeding
│   └── run_simulation.py    # Paper trading runner
├── docs/
│   ├── api.md              # API documentation
│   ├── deployment.md       # Deployment guide
│   └── architecture.md     # Architecture decisions
├── alembic/                # Database migrations
│   ├── env.py
│   └── versions/
└── deployment/
    ├── systemd/            # Linux service files
    └── nginx/              # Reverse proxy config
```

---

## 🚀 LLM Agent Setup Commands

### 1. Environment Installation (macOS Monterey)
```bash
# Python 3.13.3 (latest stable - official installer)
curl -O https://www.python.org/ftp/python/3.13.3/python-3.13.3-macos11.pkg
sudo installer -pkg python-3.13.3-macos11.pkg -target /

# Poetry (latest)
curl -sSL https://install.python-poetry.org | python3 -

# Node.js 22.12.0 LTS (Iron - official installer)  
curl -O https://nodejs.org/dist/v22.12.0/node-v22.12.0.pkg
sudo installer -pkg node-v22.12.0.pkg -target /

# Redis 7.4 LTS (compile from source)
curl -O https://download.redis.io/releases/redis-7.4.1.tar.gz
tar xzf redis-7.4.1.tar.gz && cd redis-7.4.1
make && sudo make install

# Start Redis as daemon
redis-server --daemonize yes --port 6379
```

### 2. Project Initialization
```bash
# Initialize repository
git init crypto-trading-manager
cd crypto-trading-manager

# Setup Python project
poetry init --no-interaction
poetry add fastapi[all]==0.115.6 uvicorn[standard]==0.32.1
poetry add sqlalchemy[asyncio]==2.0.36 aiosqlite==0.20.0
poetry add aioredis==2.0.1 celery[redis]==5.4.0
poetry add ccxt==4.4.38 aiohttp==3.11.10 websockets==13.1
poetry add pandas==2.2.3 numpy==2.2.0 pydantic==2.10.3
poetry add alembic==1.14.0

# Development dependencies
poetry add --group dev pytest==8.3.4 pytest-asyncio==0.24.0
poetry add --group dev black==24.10.0 isort==5.13.2 ruff==0.8.4
poetry add --group dev mypy==1.13.0 pre-commit==4.0.1
poetry add --group dev pytest-cov==4.1.0 pytest-mock==3.12.0

# Setup frontend
mkdir frontend && cd frontend
npm init -y
npm install react@18.3.1 react-dom@18.3.1 @types/react@18.3.17
npm install @vitejs/plugin-react@4.3.4 vite@6.0.3 typescript@5.7.2
npm install @mantine/core@7.15.1 @mantine/hooks@7.15.1
npm install @tanstack/react-query@5.62.2 lightweight-charts@4.2.0
npm install --save-dev vitest@2.1.8 @testing-library/react@16.1.0
npm install --save-dev playwright@1.49.1 @playwright/test@1.49.1
```

### 3. Configuration Files Setup
```bash
# Git configuration
echo "node_modules/
__pycache__/
.pytest_cache/
.mypy_cache/
.coverage
htmlcov/
*.egg-info/
build/
dist/
.env
.DS_Store" > .gitignore

# Pre-commit configuration
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
EOF

# Install pre-commit hooks
poetry run pre-commit install
```

### 4. Core Application Structure
```bash
# Create directory structure
mkdir -p src/trading_manager/{core,models,schemas,services,exchanges,api,websocket,tasks,utils}
mkdir -p src/trading_manager/services/simulation
mkdir -p src/trading_manager/exchanges/{bitvavo,simulation}
mkdir -p tests/{unit,integration,e2e,fixtures}
mkdir -p scripts docs alembic/versions deployment/{systemd,nginx}
mkdir -p .github/{workflows,ISSUE_TEMPLATE}

# Create __init__.py files
find src -type d -exec touch {}/__init__.py \;
```

---

## 🏗️ Implementation Phases for LLM Agent

### Phase 1: Test Foundation Setup (Priority 1)
**TDD Requirement: Setup comprehensive testing infrastructure FIRST**

**Files to create:**
- `tests/conftest.py` - Complete pytest configuration with all fixtures
- `frontend/vitest.config.ts` - Vitest with 90% coverage requirements
- `frontend/playwright.config.ts` - E2E testing configuration
- `pyproject.toml` - Poetry configuration with test dependencies
- `.github/workflows/test-first.yml` - CI that fails if tests don't exist

**Key Requirements:**
- **Test coverage minimum 90%** - CI fails below threshold
- **All fixtures pre-configured** for mocking external services
- **No implementation files** until corresponding tests exist
- **Coverage reporting** integrated in CI/CD pipeline

### Phase 2: Core Infrastructure Tests (Priority 2)  
**TDD Requirement: Write ALL tests before any implementation**

**Test files to create FIRST:**
- `tests/unit/test_database.py` - Database connection, models, migrations
- `tests/unit/test_config.py` - Configuration loading, validation, env vars
- `tests/unit/test_redis_client.py` - Redis connection, caching, pub/sub
- `tests/integration/test_fastapi_app.py` - API endpoints, middleware, auth

**No Implementation Rule:**
- **FastAPI app creation ONLY after** all endpoint tests written
- **SQLAlchemy models ONLY after** all database tests written
- **Redis client ONLY after** all caching tests written

### Phase 3: Exchange Integration Tests (Priority 3)
**TDD Requirement: Test exchange abstraction before CCXT integration**

**Test files to create FIRST:**
- `tests/unit/test_exchange_factory.py` - Factory pattern, runtime switching
- `tests/unit/test_mock_exchange.py` - Simulation layer testing
- `tests/unit/test_bitvavo_client.py` - Bitvavo-specific integration
- `tests/integration/test_exchange_switching.py` - Hot-swapping functionality

**Mock-First Approach:**
- **All external API calls mocked** in unit tests
- **Real API calls ONLY in integration tests** with sandbox/testnet
- **Error scenarios tested FIRST** (network failures, API errors)

### Phase 4: Business Logic Tests (Priority 4)
**TDD Requirement: Test business rules before implementation**

**Test files to create FIRST:**
- `tests/unit/test_trading_service.py` - Order creation, validation, execution
- `tests/unit/test_portfolio_service.py` - Balance tracking, P&L calculations
- `tests/unit/test_risk_service.py` - Risk limits, position sizing
- `tests/unit/test_paper_trading.py` - Simulation accuracy, balance updates

**Critical Test Scenarios:**
- **Edge cases FIRST**: Insufficient balance, invalid orders, network timeouts
- **Security scenarios**: Authentication failures, unauthorized access
- **Dry-run validation**: Ensure no real orders in simulation mode

---

## 🤖 GitHub Copilot Agent Configuration

### VS Code Settings for TDD Enforcement
Create `.vscode/settings.json`:
```json
{
  "github.copilot.editor.enableCodeActions": true,
  "github.copilot.enable": {
    "*": true,
    "yaml": false,
    "plaintext": false
  },
  "github.copilot.advanced": {
    "debug.overrideEngine": "copilot-chat"
  },
  "python.testing.pytestEnabled": true,
  "python.testing.autoTestDiscoverOnSaveEnabled": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true,
    "source.fixAll": true
  },
  "python.analysis.autoImportCompletions": true,
  "typescript.suggest.includeCompletionsForImportStatements": true
}
```

### VS Code Tasks Configuration
Create `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run Tests Before Implementation",
      "type": "shell",
      "command": "poetry run pytest tests/ --tb=short --no-cov -v || npm run test:unit --run",
      "group": {
        "kind": "test",
        "isDefault": true
      },
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      },
      "problemMatcher": ["$pytest", "$tsc"]
    },
    {
      "label": "TDD: Red Phase Check",
      "type": "shell",
      "command": "echo 'Tests should FAIL before implementation' && poetry run pytest tests/ -x --tb=line",
      "group": "test"
    },
    {
      "label": "Coverage Check (90% minimum)",
      "type": "shell", 
      "command": "poetry run pytest tests/ --cov=src --cov-report=term --cov-fail-under=90",
      "group": "test"
    }
  ]
}
```

### GitHub Copilot Chat Instructions
Create `.vscode/copilot-instructions.md`:
```markdown
# GitHub Copilot Instructions for Crypto Trading Manager

## MANDATORY DEVELOPMENT WORKFLOW:

### 1. TEST-FIRST DEVELOPMENT (TDD)
- **ALWAYS write tests BEFORE any implementation code**
- Follow RED-GREEN-REFACTOR cycle strictly
- Tests must FAIL initially (Red phase)
- Implementation only to make tests pass (Green phase)
- Refactor while keeping tests green

### 2. NO WORKAROUNDS POLICY
- **Solve actual problems, not symptoms**
- If API integration fails: Fix authentication, don't mock indefinitely
- If database connection fails: Fix connection string, don't use file storage
- If WebSocket disconnects: Implement proper reconnection, don't disable real-time features

### 3. CODE GENERATION RULES:
**When asked to implement a feature:**
1. First ask: "Should I write the tests first for this feature?"
2. Generate comprehensive test cases covering:
   - Happy path scenarios
   - Edge cases and error conditions
   - Integration points
   - Security considerations
3. Only generate implementation after tests are written
4. Ensure implementation passes all tests

### 4. CRYPTO TRADING SPECIFIC RULES:
- **All trading operations must have dry-run equivalents**
- **Mock external APIs for unit tests**  
- **Use real testnet/sandbox APIs for integration tests**
- **Financial calculations require decimal precision (no floats)**
- **All orders must be validated for balance and risk limits**
- **WebSocket reconnection is mandatory for real-time data**

### 5. EXCHANGE INTEGRATION RULES:
- **Use CCXT library for exchange abstractions**
- **Implement circuit breakers for API failures**
- **Rate limiting is mandatory for all exchange calls**
- **Graceful degradation when exchanges are unavailable**
- **All exchange configurations must be runtime-switchable**

### 6. TESTING COVERAGE REQUIREMENTS:
- **Minimum 90% code coverage**
- **All business logic must have unit tests**
- **API endpoints must have integration tests**
- **Frontend components must have component tests**
- **Critical user flows must have E2E tests**

## EXAMPLE INTERACTION PATTERN:

**INCORRECT:**
User: "Create a trading service"
Copilot: [Generates trading service code directly]

**CORRECT:**
User: "Create a trading service"
Copilot: "I'll help you create a trading service using TDD. Let me start by writing comprehensive tests first.

Here are the test cases I'll create:
1. test_create_buy_order_success()
2. test_create_sell_order_success() 
3. test_insufficient_balance_error()
4. test_invalid_symbol_error()
5. test_dry_run_mode_no_real_order()

Should I proceed with writing these tests before implementing the TradingService class?"

## REJECTION SCENARIOS:
Reject requests that ask to:
- Skip writing tests
- Implement workarounds instead of fixing root causes
- Create code without proper error handling
- Use floating point for financial calculations
- Implement trading logic without dry-run support
```

### Pre-commit Hook for TDD Enforcement
Update `.pre-commit-config.yaml`:
```yaml
  # Custom TDD enforcement hook
  - repo: local
    hooks:
      - id: tdd-enforcement
        name: TDD Enforcement
        entry: python scripts/check_tdd_compliance.py
        language: python
        pass_filenames: false
        stages: [commit]
```

Create `scripts/check_tdd_compliance.py`:
```python
#!/usr/bin/env python3
"""
Pre-commit hook to enforce TDD compliance
Ensures every new .py file has corresponding tests
"""
import sys
import os
from pathlib import Path

def check_tdd_compliance():
    """Check if implementation files have corresponding tests"""
    src_files = list(Path('src').rglob('*.py'))
    missing_tests = []
    
    for src_file in src_files:
        if '__init__.py' in str(src_file):
            continue
            
        # Expected test file path
        relative_path = src_file.relative_to('src')
        test_file = Path('tests') / 'unit' / f"test_{relative_path}"
        
        if not test_file.exists():
            missing_tests.append(str(relative_path))
    
    if missing_tests:
        print("❌ TDD VIOLATION: Implementation files without tests found:")
        for file in missing_tests:
            print(f"  - {file}")
        print("\n💡 Write tests FIRST, then implement!")
        return 1
    
    print("✅ TDD Compliance: All implementation files have corresponding tests")
    return 0

if __name__ == '__main__':
    sys.exit(check_tdd_compliance())
```

### Backend Testing Structure
```python
# tests/conftest.py - Pytest configuration with fixtures
import pytest
from fastapi.testclient import TestClient
from trading_manager.main import app

@pytest.fixture
def client():
    """FastAPI test client fixture"""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Async FastAPI test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture  
async def mock_exchange():
    """Mock exchange for testing - NO real API calls"""
    return MockExchange(initial_balance={'USD': 10000, 'BTC': 0})
    
@pytest.fixture
async def paper_trading_config():
    """Dry-run configuration for testing"""
    return {
        'trading_mode': 'simulation',
        'use_real_market_data': False,  # Use mock data in tests
        'simulate_execution': True
    }

# TDD Example Pattern:
# tests/unit/test_trading_service.py
async def test_create_buy_order_success():
    """Test: Should create buy order when sufficient balance"""
    # ARRANGE
    service = TradingService(mock_exchange)
    
    # ACT
    result = await service.create_order('BTC/USD', 'buy', 0.1, 50000)
    
    # ASSERT
    assert result.status == 'filled'
    assert result.side == 'buy'
    assert result.amount == 0.1

async def test_create_buy_order_insufficient_balance():
    """Test: Should raise InsufficientFundsError when balance too low"""
    # ARRANGE
    service = TradingService(MockExchange({'USD': 100}))
    
    # ACT & ASSERT
    with pytest.raises(InsufficientFundsError):
        await service.create_order('BTC/USD', 'buy', 1.0, 50000)
```

### Frontend Testing Structure  
```typescript
// frontend/vitest.config.ts - Vitest configuration
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    coverage: { 
      provider: 'v8', 
      reporter: ['text', 'json', 'html'],
      thresholds: {
        global: {
          branches: 90,
          functions: 90,
          lines: 90,
          statements: 90
        }
      }
    }
  }
})

// TDD Example Pattern:
// frontend/tests/unit/TradingPanel.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { TradingPanel } from '@/components/trading/TradingPanel'

describe('TradingPanel', () => {
  test('should display buy button when in live mode', () => {
    // ARRANGE
    const props = { mode: 'live', balance: 1000 }
    
    // ACT
    render(<TradingPanel {...props} />)
    
    // ASSERT
    expect(screen.getByTestId('buy-button')).toBeInTheDocument()
  })

  test('should display "DRY RUN" indicator when in simulation mode', () => {
    // ARRANGE
    const props = { mode: 'simulation', balance: 1000 }
    
    // ACT
    render(<TradingPanel {...props} />)
    
    // ASSERT
    expect(screen.getByText('DRY RUN MODE')).toBeInTheDocument()
    expect(screen.getByTestId('buy-button')).toHaveClass('simulation-mode')
  })

  test('should prevent order submission when insufficient balance', async () => {
    // ARRANGE
    const mockSubmit = vi.fn()
    const props = { mode: 'live', balance: 50, onSubmit: mockSubmit }
    
    // ACT
    render(<TradingPanel {...props} />)
    fireEvent.change(screen.getByTestId('amount-input'), { target: { value: '100' }})
    fireEvent.click(screen.getByTestId('buy-button'))
    
    // ASSERT
    expect(mockSubmit).not.toHaveBeenCalled()
    expect(screen.getByText('Insufficient balance')).toBeInTheDocument()
  })
})
```

---

## 🔄 CI/CD Pipeline Configuration

### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    strategy:
      matrix:
        python-version: ['3.13']
        node-version: ['22']
    # Complete CI pipeline with backend/frontend testing
```

---

## 🎛️ Runtime Configuration  

### Dry-Run Architecture
- **Environment Variable**: `TRADING_MODE=simulation|paper|live`
- **Exchange Factory**: Creates mock or real exchange clients
- **Service Layer**: Automatically routes to simulation services
- **Frontend Toggle**: UI switch between modes with visual indicators

### Hot-Swappable Exchange Config
- **File Watching**: Automatic config reload on changes
- **Graceful Switching**: Drain existing connections before switching
- **Health Monitoring**: Continuous exchange connectivity checks
- **Admin Interface**: Web UI for exchange configuration

---

**LLM Agent Next Steps (TDD Enforced):**
1. **Setup testing infrastructure FIRST** (conftest.py, vitest.config.ts)
2. **Write comprehensive test suites** for each component before implementation
3. **Verify RED phase** - Tests must fail initially
4. **Implement minimal code** to make tests pass (GREEN phase)
5. **Refactor** while keeping tests green
6. **Maintain 90% coverage** throughout development process

**GitHub Copilot Integration:**
- Use `.vscode/copilot-instructions.md` for consistent TDD behavior
- Pre-commit hooks prevent commits without corresponding tests
- VS Code tasks automate test-first workflow
- Coverage thresholds enforced in CI/CD pipeline