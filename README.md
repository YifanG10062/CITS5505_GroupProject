# CITS5505 Group Project – The Richverse

## Application Purpose and Design

**The Richverse** is an interactive web application built with **Flask** that allows users to track, compare, analyze and share investment portfolios. The platform combines powerful analytics with an intuitive interface, enabling data-driven investment decisions through visual insights.

The application is inspired by professional financial analysis tools but made accessible for everyday investors, students, and finance enthusiasts. The modern UI, powered by Chart.js, delivers clean and informative portfolio visualizations with a focus on user experience.

## Key Features

- **Portfolio Management**: Create, compare and share investment portfolios with customizable allocations
- **Performance Analytics**: Track and compare key metrics including returns, volatility, Sharpe ratio, and more
- **Visual Insights**: Interactive dashboards with dynamic charts for data-driven decisions
- **Benchmark Comparison**: Measure portfolio performance against market indices
- **Data Integration**: Powered by Yahoo Finance API for real historical asset prices

## Target Users

- **Retail Investors**: Seeking insights to optimize existing portfolios
- **Finance Students**: Learning investment strategies through hands-on analysis
- **Investment Enthusiasts**: Exploring market trends and portfolio construction

## Group Members - Masters Group 30

| UWA ID     | Name                      | GitHub Username |
|------------|---------------------------|-----------------|
| 24365906   | Aoli Wang                 | aolilfn         |
| 24509011   | Farah Warnakulasuriya     | KiwiFarah       |
| 23966753   | Yifan Gao                 | YifanG10062     |
| 23866945   | Pavan Kumar Potukuchi     | Pavan23866945   |

## Launch Instructions

Ensure you are using **Python 3.10+**. Python 3.13 is **not recommended** due to package compatibility issues.

### 1. Clone the repository
```bash
git clone https://github.com/YifanG10062/CITS5505_GroupProject.git
cd CITS5505_GroupProject
```

### 2. Create and activate virtual environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize the database
```bash
flask db upgrade
```

### 5. Launch the application
The application will automatically fetch any missing price data and start the Flask server:
```bash
python run.py
```

Visit: `http://localhost:5000`

## Running Tests

The project includes both unit tests and Selenium UI tests that verify the key frontend components and user flows in a real browser environment.

### What is Tested

#### Unit Tests
The unit test suite covers the following components:
- **Login & Registration** (`test_login.py`, `test_register_server.py`): Tests for user authentication
- **Portfolio Management** (`test_portfolio.py`): Tests for portfolio creation and management
- **Calculations** (`test_calculation.py`): Tests for financial calculations and metrics
- **Data Fetching** (`test_fetch_price.py`): Tests for price data retrieval
- **Visualizations** (`test_visualization.py`): Tests for chart data generation

#### Selenium UI Tests
Each Selenium script tests the following:
- **Login Page** (`pageLoginUI.py`): Tests login interface and authentication
- **Portfolio List Page** (`pagePortfolioList.py`): Tests portfolio listing and management UI
- **Create Portfolio Page** (`pageCreatePortfolio.py`): Tests portfolio creation interface
- **Dashboard Page** (`pageDashboard.py`): Tests dashboard visualization and metrics display

All Selenium tests extend from a base test class (`selenium_base.py`) that handles server setup and teardown. They focus on **happy path flows** and structural validation of key screens in the user journey.

**Test Environment Setup**: Each Selenium test automatically:
- Starts a local Flask server via a background thread
- Uses an in-memory SQLite database with shared connection pool
- Uses Selenium ChromeDriver in headless mode
- Logs in as a test user (or registers the user if login fails)

### Running All Tests

1. Run all Selenium UI tests:
```bash
python -m unittest discover -s tests/seleniumTests -p "*.py"
```

2. Run all unit tests:
```bash
python tests/run_unit_tests.py
```

### Example Unit Test Output

```
✔ Test 1 passed
✔ Test 2 passed
✔ Test 3 passed
✔ Test 4 passed
✔ Test 5 passed
.
----------------------------------------------------------------------
Ran 5 tests in X.XXXs

OK
```

### Example Selenium Test Output

```
Create Portfolio page structure successfully validated.
Dashboard UI structure and metrics successfully validated.
'Create New Portfolio' button is visible on Portfolio List page.

----------------------------------------------------------------------
Ran 6 tests in 32.53s
OK
```

This satisfies the **"5+ Selenium tests run on a live server"** requirement.

## Notes

- The system uses mock asset data and real-time price history from Yahoo Finance
- Unit tests are isolated from login/auth logic and use seeded mock data
- CLI commands are provided for local development support:
  - `setup-dev`: Creates test users and initializes development environment
  - `refresh-user-info`: Updates user information in portfolio summaries
  - `refresh-history`: Updates historical price data from Yahoo Finance

## Browser Compatibility

- The application works seamlessly on Chrome, Firefox, and Edge browsers
- **Safari Users Note**: Due to Safari's strict privacy policies and CSRF cookie handling, macOS Safari users may experience issues with login and data fetching. Safari's default settings can block third-party cookies and enforce strict SameSite cookie policies. To use the application on Safari:
  
  ```bash
  # Set development environment (disables strict CSRF and cookie settings)
  export APP_ENV=development && export FLASK_ENV=development
  
  # Apply development database migrations
  flask dev-db-upgrade
  
  # Launch the APP
  flask run
  ```
  
  After these steps, the application should work properly in Safari. The development mode relaxes some security settings that may otherwise prevent proper authentication in Safari. Other browsers do not require these special steps.

## References

### Financial Theory
[1] Zvi Bodie, Investments. New York: Mcgraw-Hill Education Asia, 2014.
[2] W. F. Sharpe, "Capital Asset Prices: A Theory of Market Equilibrium under Conditions of Risk," Journal of Finance, vol. 19, no. 3, pp. 425-442, 1964.

### Design Inspiration
[1] "Morningstar Direct Portfolio Analysis," Morningstar, Inc., 2024. https://www.morningstar.com/products/portfolio-analysis (accessed May 16, 2025).
[2] "Backtest Portfolio Asset Allocation," www.portfoliovisualizer.com. https://www.portfoliovisualizer.com/backtest-portfolio

### Technical Resources
[1] "Chart.js documentation," www.chartjs.org. https://www.chartjs.org/docs/latest/
[2] "Flask Documentation," Pallets, 2024. https://flask.palletsprojects.com/ (accessed May 15, 2025).
[3] "SQLAlchemy - The Database Toolkit for Python," SQLAlchemy, 2024. https://www.sqlalchemy.org/ (accessed May 16, 2025).
[4] "yfinance - Yahoo Finance market data downloader," PyPI, 2024. https://pypi.org/project/yfinance/ (accessed May 16, 2025).
[5] "Selenium Documentation," Selenium Project, 2024. https://www.selenium.dev/documentation/ (accessed May 16, 2025).
