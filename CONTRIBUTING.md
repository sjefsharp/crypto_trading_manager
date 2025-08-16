# Contributing to Crypto Trading Manager

We welcome contributions to the Crypto Trading Manager project! This document provides guidelines for contributing to the project.

## Table of Contents

- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Review Process](#code-review-process)

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Git
- Docker (optional)

### Backend Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/sjefsharp/crypto_trading_manager.git
   cd crypto_trading_manager
   ```

2. Set up Python environment:

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up pre-commit hooks:

   ```bash
   cd ..
   pip install pre-commit
   pre-commit install
   ```

4. Copy environment file and configure:
   ```bash
   cd backend
   cp .env.development .env
   # Edit .env with your configuration
   ```

### Frontend Setup

1. Install dependencies:

   ```bash
   cd frontend
   npm install
   ```

2. Copy environment file:
   ```bash
   cp .env.example .env.local
   # Edit .env.local if needed
   ```

## Code Standards

### Python (Backend)

- **Formatting**: Use Black with 88 character line length
- **Import Sorting**: Use isort with Black profile
- **Linting**: Follow flake8 rules
- **Type Hints**: Use type hints for all function parameters and return values
- **Docstrings**: Use Google-style docstrings for all public functions and classes

Example:

```python
from typing import Optional, List
from pydantic import BaseModel

def calculate_portfolio_value(
    positions: List[Position],
    current_prices: Dict[str, float]
) -> float:
    """Calculate total portfolio value based on current positions and prices.

    Args:
        positions: List of current portfolio positions
        current_prices: Dictionary mapping symbols to current prices

    Returns:
        Total portfolio value in USD

    Raises:
        ValueError: If required price data is missing
    """
    total_value = 0.0
    for position in positions:
        if position.symbol not in current_prices:
            raise ValueError(f"Price data missing for {position.symbol}")
        total_value += position.quantity * current_prices[position.symbol]
    return total_value
```

### TypeScript/React (Frontend)

- **Formatting**: Use Prettier with single quotes and trailing commas
- **Linting**: Follow ESLint React and TypeScript rules
- **Components**: Use functional components with TypeScript interfaces
- **Naming**: Use PascalCase for components, camelCase for functions and variables

Example:

```typescript
interface PortfolioProps {
  positions: Position[];
  onPositionClick: (position: Position) => void;
  loading?: boolean;
}

export const Portfolio: React.FC<PortfolioProps> = ({
  positions,
  onPositionClick,
  loading = false,
}) => {
  const calculateTotalValue = useCallback((): number => {
    return positions.reduce((total, position) => {
      return total + position.quantity * position.currentPrice;
    }, 0);
  }, [positions]);

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="portfolio">
      <h2>Portfolio Overview</h2>
      <div className="total-value">
        Total Value: ${calculateTotalValue().toFixed(2)}
      </div>
      {positions.map((position) => (
        <PositionCard
          key={position.id}
          position={position}
          onClick={() => onPositionClick(position)}
        />
      ))}
    </div>
  );
};
```

## Testing Requirements

### Backend Testing

- **Unit Tests**: All business logic must have unit tests with >90% coverage
- **Integration Tests**: API endpoints must have integration tests
- **Test Organization**: Use pytest fixtures and test classes
- **Mocking**: Use pytest mocks for external dependencies

Run tests:

```bash
cd backend
pytest tests/ --cov=app --cov-report=html
```

### Frontend Testing

- **Unit Tests**: Components and utilities must have unit tests
- **Integration Tests**: User flows must have integration tests
- **Visual Tests**: UI components must have Playwright visual tests

Run tests:

```bash
cd frontend
npm run test:run          # Unit tests
npm run test:visual       # Visual tests
npm run test:all          # All tests
```

## Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

### Examples

```
feat(trading): add stop-loss order functionality

- Implement stop-loss calculation logic
- Add stop-loss API endpoints
- Update trading service with stop-loss support

Closes #123
```

```
fix(portfolio): correct portfolio value calculation

The portfolio value was not accounting for fees properly.
This fix ensures fees are deducted from the total value.

Fixes #456
```

## Pull Request Process

1. **Create Feature Branch**: Create a branch from `develop` for new features

   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**: Implement your changes following the code standards

3. **Run Quality Checks**: Ensure all checks pass

   ```bash
   # Backend
   cd backend
   black .
   isort .
   flake8 .
   mypy app/
   pytest tests/

   # Frontend
   cd frontend
   npm run quality
   ```

4. **Commit Changes**: Use conventional commit messages

5. **Push and Create PR**: Push your branch and create a pull request

6. **PR Requirements**:
   - All CI checks must pass
   - Code coverage must not decrease
   - At least one approving review required
   - All conversations must be resolved

## Code Review Process

### For Reviewers

- **Functionality**: Does the code work as intended?
- **Code Quality**: Is the code clean, readable, and maintainable?
- **Performance**: Are there any performance concerns?
- **Security**: Are there any security vulnerabilities?
- **Tests**: Are there adequate tests for the changes?
- **Documentation**: Is the code properly documented?

### Review Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Code coverage is maintained or improved
- [ ] No security vulnerabilities introduced
- [ ] Performance impact is acceptable
- [ ] Documentation is updated if needed
- [ ] Breaking changes are documented

### Approval Process

1. **Initial Review**: At least one team member must review
2. **Security Review**: Required for security-related changes
3. **Performance Review**: Required for performance-critical changes
4. **Final Approval**: Maintainer approval required for merge

## Getting Help

- **Issues**: Check existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the project wiki
- **Contact**: Reach out to maintainers directly

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.
