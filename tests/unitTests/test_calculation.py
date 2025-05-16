import unittest
from datetime import date, timedelta
import pandas as pd

from app import create_app, db
from app.config import TestConfig
from app.models import Price
from app.services.calculation import (
    calculate_portfolio_metrics,
    get_portfolio_timeseries,
    get_spy_cumulative_returns,
    calculate_drawdown_series,
)

class CalculationEdgeCases(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # seed 30 days of deterministic prices for two assets and SPY
        start = date.today() - timedelta(days=29)
        for i in range(30):
            d = start + timedelta(days=i)
            db.session.add_all([
                Price(asset_code="MSFT", date=d, close_price=100 + i),
                Price(asset_code="TSLA", date=d, close_price=200 + 2 * i),
                Price(asset_code="SPY",  date=d, close_price=300 + 3 * i),
            ])
        db.session.commit()

        self.allocation = {"MSFT": 0.6, "TSLA": 0.4}
        self.start_date = start.strftime("%Y-%m-%d")
        self.initial_amount = 1_000

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    # ---------- calculate_portfolio_metrics ----------
    def test_calc_metrics_empty_allocation(self):
        self.assertEqual(calculate_portfolio_metrics({}, self.start_date, self.initial_amount), {})
        print("✔ calculate_portfolio_metrics: returns empty dict when allocation is empty")

    def test_calc_metrics_after_last_record(self):
        future_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertEqual(calculate_portfolio_metrics(self.allocation, future_date, self.initial_amount), {})
        print("✔ calculate_portfolio_metrics: returns empty dict when start_date is beyond available data range")

    def test_calc_metrics_selected_fields(self):
        res = calculate_portfolio_metrics(self.allocation, self.start_date, self.initial_amount, fields=["current_value", "profit"])
        self.assertEqual(set(res.keys()), {"current_value", "profit"})
        self.assertTrue(res["current_value"] > 0)
        print("✔ calculate_portfolio_metrics: returns only the requested fields when 'fields' parameter is provided")

    # ---------- get_portfolio_timeseries ----------
    def test_timeseries_empty_db(self):
        db.session.query(Price).delete()
        db.session.commit()
        ts = get_portfolio_timeseries(self.allocation, self.start_date, self.initial_amount)
        self.assertEqual(ts, {})
        print("✔ get_portfolio_timeseries: returns empty dict when the Price table is empty")

    # ---------- get_spy_cumulative_returns ----------
    def test_spy_cum_returns_match_dates(self):
        match_dates = [(date.today() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)]
        vals = get_spy_cumulative_returns(self.start_date, match_dates)
        self.assertEqual(len(vals), len(match_dates))
        print("✔ get_spy_cumulative_returns: returned list length matches the number of matched dates")

    def test_spy_cum_returns_no_data(self):
        future_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        vals = get_spy_cumulative_returns(future_date, [])
        self.assertEqual(vals, [])
        print("✔ get_spy_cumulative_returns: returns empty list when no data is available for the given start_date")

    # ---------- calculate_drawdown_series ----------
    def test_drawdown_series_shape(self):
        dd = calculate_drawdown_series(self.allocation, self.start_date, self.initial_amount)
        self.assertIn("labels", dd)
        self.assertIn("values", dd)
        self.assertEqual(len(dd["labels"]), len(dd["values"]))
        print("✔ calculate_drawdown_series: 'labels' and 'values' arrays have the same length")

    def test_drawdown_series_empty(self):
        # clear table
        db.session.query(Price).delete()
        db.session.commit()
        dd = calculate_drawdown_series(self.allocation, self.start_date, self.initial_amount)
        self.assertEqual(dd, {})
        print("✔ calculate_drawdown_series: returns empty dict when the Price table is empty")

if __name__ == "__main__":
    unittest.main()
