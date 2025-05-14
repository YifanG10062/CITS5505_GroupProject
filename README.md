# CITS5505 Group Project – The Richverse

**The Richverse** is an interactive web application built with **Flask** that allows users to track, compare, and analyze investment portfolios over time. Users can create portfolios, view cumulative returns, benchmark against SPY and explore key performance metrics via interactive charts.

The application is designed to support retail investors, students, and finance enthusiasts in understanding the impact of asset allocation over time to support future investments. The dashboard visualizations are inspired by industry tear sheets, with a modern UI powered by Chart.js.

---

## Group Members - Masters Group 30

| UWA ID     | Name                      |
|------------|---------------------------|
| 24365906   | Aoli Wang                 |
| 24509011   | Farah Warnakulasuriya     |
| 23966753   | Yifan Gao                 |
| 23866945   | Pavan Kumar Potukuchi     |

---

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

### 5. Check historical price data and Run the application
This will fetch any missing price data from 2015 to today for the assets and then start the Flask server.
```bash
python run.py
```

Visit: `http://localhost:5000`

---

## Running Tests

The project includes unit tests for Login, register, portfolio metric calculations and drawdown logic.

To run the tests:
```bash
python -m unittest tests/test_visualization.py
```

> **Note:** Replace `test_visualization.py` with the actual test file name you want to run, e.g.:
> ```bash
> python -m unittest tests/test_file_name.py
> ```

Expected output:
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

---
## Running Selenium test cases
The project includes Selenium test cases
Page level - all element validations for User registration, Login,  PortfolioList, CreatePortfolio, Dashboard
Happy Path scenarios for User registration, Login,  PortfolioList, CreatePortfolio, Dashboard

>A specific selenium test file can be run by the command in terminal: python -m seleniumTests.pageLogin
>Please replace the file of your choice in place of pageLogin like loginTest, pageCreatePortfolio, pageDashboard,...

> A script like: run_selenium_tests.bat can be created :
> To run the tests: (for Windows)
@echo off
python -m unittest discover -s seleniumTests -p "*.py"
pause
 
>To run the tests: (for Mac/Linux)
```bash
#!/bin/bash
python -m unittest discover -s seleniumTests -p "*.py"
```

>To make it executable
>chmod +x run_selenium_tests.sh

---

## Notes

- The system uses mock asset data and real-time price history from Yahoo Finance.
- Unit tests are isolated from login/auth logic and use seeded mock data.
- CLI commands (`setup-dev`, `refresh-user-info`) are provided for local development support.
