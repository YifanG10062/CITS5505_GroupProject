import unittest
from unittest.mock import patch
import pandas as pd
from io import StringIO
import sys

from app import create_app, db
from app.config import TestConfig
from app.services.fetch_price import fetch_all_history

class TestFetchAllHistory(unittest.TestCase):
    def setUp(self):
        # Create Flask app with test config and initialize database
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Capture stdout
        self._stdout = sys.stdout
        sys.stdout = StringIO()

    def tearDown(self):
        # Restore stdout and drop database
        sys.stdout = self._stdout
        db.drop_all()
        self.ctx.pop()

    @patch('os.path.exists', return_value=False)
    @patch('app.services.fetch_price.pd.read_csv')
    @patch('app.services.fetch_price.yf.download')
    def test_yfinance_success(self, mock_download, mock_read_csv, mock_exists):
        # Simulate yfinance returning a valid DataFrame
        dates = pd.to_datetime(['2020-01-01', '2020-01-02'])
        df_stub = pd.DataFrame({'Close': [1.0, 2.0]}, index=dates)
        df_stub.index.name = 'Date'
        mock_download.return_value = df_stub
        # Ensure read_csv isn't called
        mock_read_csv.return_value = pd.DataFrame()

        # Run the fetch
        fetch_all_history()
        output = sys.stdout.getvalue()

        # Should attempt yfinance and not hit fallback
        self.assertIn('📈 Fetching: AAPL', output)
        self.assertNotIn('Using Stooq', output)
        self.assertIn('✔ All historical prices saved successfully', output)
        print("✔ Test yfinance_success passed", file=sys.__stdout__)

    @patch('os.path.exists', return_value=False)
    @patch('app.services.fetch_price.pd.read_csv')
    @patch('app.services.fetch_price.yf.download', side_effect=Exception('yfinance error'))
    def test_stooq_fallback(self, mock_download, mock_read_csv, mock_exists):
        # Simulate Stooq CSV providing data
        dates = pd.to_datetime(['2020-01-01', '2020-01-02'])
        df_stub = pd.DataFrame({'Close': [3.0, 4.0]}, index=dates)
        df_stub.index.name = 'Date'
        mock_read_csv.return_value = df_stub

        fetch_all_history()
        output = sys.stdout.getvalue()

        self.assertIn('✘ yfinance failed for AAPL', output)
        self.assertIn('Using Stooq data source for AAPL', output)
        self.assertIn('✔ All historical prices saved successfully', output)
        print("✔ Test stooq_fallback passed", file=sys.__stdout__)

    @patch('os.path.exists', return_value=True)
    @patch('app.services.fetch_price.pd.read_csv')
    @patch('app.services.fetch_price.yf.download', side_effect=Exception('yfinance error'))
    def test_cache_fallback(self, mock_download, mock_read_csv, mock_exists):
        # Simulate Stooq failure then cache success
        def read_csv_side_effect(path, *args, **kwargs):
            if 'stooq.com' in path:
                raise Exception('stooq error')
            # Cache read: return DataFrame with index named 'Date'
            cache_dates = pd.to_datetime(['2020-01-01'])
            cache_df = pd.DataFrame({'Close': [5.0]}, index=cache_dates)
            cache_df.index.name = 'Date'
            return cache_df
        mock_read_csv.side_effect = read_csv_side_effect

        fetch_all_history()
        output = sys.stdout.getvalue()

        self.assertIn('✘ Stooq failed for AAPL', output)
        self.assertIn('Loaded cache for AAPL', output)
        self.assertIn('✔ All historical prices saved successfully', output)
        print("✔ Test cache_fallback passed", file=sys.__stdout__)

if __name__ == '__main__':
    unittest.main()
