# unit test for data visualization dashboard module
import unittest
import pandas as pd
from app import create_app, db
from app.models import Price
from app.calculation import (
    calculate_portfolio_metrics,
    get_portfolio_timeseries,
    calculate_drawdown_series
)
from config import TestConfig


class VisualizationTestCases(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.allocation = {"MSFT": 0.6, "TSLA": 0.4}
        self.start_date = "2020-01-01"
        self.initial_amount = 10000

        dates = pd.date_range(start=self.start_date, periods=30, freq="D")
        for i, date in enumerate(dates):
            db.session.add_all([
                Price(asset_code="MSFT", date=date, close_price=100 + i),
                Price(asset_code="TSLA", date=date, close_price=200 + i * 2),
                Price(asset_code="SPY", date=date, close_price=300 + i * 3),
            ])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_1_empty_allocation_returns_empty_dict(self):
        result = calculate_portfolio_metrics({}, self.start_date, self.initial_amount)
        self.assertEqual(result, {})
        print("✔ Test 1 passed")

    def test_2_calculate_portfolio_metrics_returns_keys(self):
        result = calculate_portfolio_metrics(self.allocation, self.start_date, self.initial_amount)
        expected_keys = {
            "current_value", "profit", "return_percent", "cagr",
            "volatility", "max_drawdown", "longestDD"
        }
        self.assertTrue(expected_keys.issubset(result.keys()))
        print("✔ Test 2 passed")

    def test_3_get_portfolio_timeseries_returns_series(self):
        result = get_portfolio_timeseries(self.allocation, self.start_date, self.initial_amount)
        expected_keys = {
            "portfolio_value_series", "daily_returns_series", "cumulative_returns_series"
        }
        self.assertTrue(expected_keys.issubset(result.keys()))
        print("✔ Test 3 passed")

    def test_4_calculate_drawdown_series_returns_dict(self):
        result = calculate_drawdown_series(self.allocation, self.start_date, self.initial_amount)
        self.assertIn("labels", result)
        self.assertIn("values", result)
        self.assertEqual(len(result["labels"]), len(result["values"]))
        print("✔ Test 4 passed")

    def test_5_drawdown_values_contain_no_nans(self):
        result = calculate_drawdown_series(self.allocation, self.start_date, self.initial_amount)
        self.assertTrue(all(pd.notna(result["values"])), "Drawdown values contain NaNs")
        print("✔ Test 5 passed")


if __name__ == "__main__":
    unittest.main()
