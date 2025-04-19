import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.calculation import (
    calculate_portfolio_metrics,
    get_portfolio_timeseries,
    get_spy_cumulative_returns
)
import pandas as pd

# Step 1: Create the Flask app
app = create_app()

# Step 2: Run inside the app context
with app.app_context():
    # Define test inputs
    allocation = {
        "MSFT": 0.6,
        "TSLA": 0.4
    }
    start_date = "2020-01-01"
    initial_amount = 10000
    fields = None

    # --- 1. Test portfolio summary ---
    result = calculate_portfolio_metrics(allocation, start_date, initial_amount, fields)
    print("Summary Result:")
    print(result)

    # --- 2. Test time series ---
    ts_data = get_portfolio_timeseries(allocation, start_date, initial_amount)
    print("\nTime Series Keys:", ts_data.keys())

    for key, series in ts_data.items():
        print(f"\nPreview of '{key}':")
        for i, (timestamp, value) in enumerate(series.items()):
            if i >= 3:
                break
            print(f"{timestamp}: {value}")

    # --- 3. Test SPY benchmark cumulative returns ---
    print("\nSPY Benchmark Preview:")
    match_dates = list(ts_data["cumulative_returns_series"].keys())
    spy_returns = get_spy_cumulative_returns(start_date, match_dates)

    # Print first 3 SPY returns
    for i, value in enumerate(spy_returns[:3]):
        print(f"{match_dates[i]}: {value}")