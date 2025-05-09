# 💰 CITS5505 Group Project – The Richverse

**The Richverse** is an interactive web application built with **Flask** that allows users to track, compare, and analyze investment portfolios over time. Users can create portfolios, view cumulative returns, benchmark against SPY and explore key performance metrics via interactive charts.

The application is designed to support retail investors, students, and finance enthusiasts in understanding the impact of asset allocation over time to support future investments. The dashboard visualizations are inspired by industry tear sheets, with a modern UI powered by Chart.js.

---

## 👥 Group Members

| UWA ID     | Name                      |
|------------|---------------------------|
| 24365906   | Aoli Wang                 |
| 24509011   | Farah Warnakulasuriya     |
| 23966753   | Yifan Gao                 |
| 23866945   | Pavan Kumar Potukuchi     |

---

## 🚀 Launch Instructions

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

### 5. Populate historical price data
This fetches asset prices (BTC-USD, AAPL, SPY, QQQ, etc.) from 2015 to today:
```bash
flask --app run.py refresh-history
```

### 6. Run the application
```bash
python run.py
```

Visit: `http://localhost:5000`

---

## 🧪 Running Tests

The project includes unit tests for portfolio metric calculations and drawdown logic.

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

## 📝 Notes

- The system uses mock asset data and real-time price history from Yahoo Finance.
- Unit tests are isolated from login/auth logic and use seeded mock data.
- CLI commands (`setup-dev`, `refresh-user-info`) are provided for local development support.
