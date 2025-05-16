import unittest
from unittest.mock import patch, mock_open, call
import pandas as pd
from io import StringIO
import sys
import os

from app import create_app, db
from app.config import TestConfig
from app.services.fetch_price import fetch_all_history

class TestFetchAllHistory(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        self._stdout = sys.stdout
        sys.stdout = StringIO()

    def tearDown(self):
        sys.stdout = self._stdout
        db.drop_all()
        self.ctx.pop()

    @patch('os.makedirs')
    @patch('os.path.exists', side_effect=lambda path: False if path == 'data' else False)
    @patch('app.services.fetch_price.pd.read_csv')
    @patch('app.services.fetch_price.yf.download')
    @patch('pandas.DataFrame.to_csv')
    def test_yfinance_success(self, mock_to_csv, mock_download, mock_read_csv, mock_exists, mock_makedirs):
        dates = pd.to_datetime(['2020-01-01', '2020-01-02'])
        df_stub = pd.DataFrame({'Close': [1.0, 2.0]}, index=dates)
        df_stub.index.name = 'Date'
        mock_download.return_value = df_stub
        mock_read_csv.return_value = pd.DataFrame()

        fetch_all_history()
        output = sys.stdout.getvalue()
        
        # Check directory creation
        mock_makedirs.assert_called_once_with('data')
        
        # Check data source detection and logging
        self.assertIn('📈 Fetching: AAPL', output)
        self.assertNotIn('Using Stooq', output)
        
        # Check cache saving
        self.assertIn('✓ Saved', output)
        mock_to_csv.assert_called()
        
        # Check final success message
        self.assertIn('✔ All historical prices saved successfully', output)
        print("✔ Test yfinance_success passed", file=sys.__stdout__)

    @patch('os.path.exists', side_effect=lambda path: False if path == 'data' else False)
    @patch('os.makedirs')
    @patch('app.services.fetch_price.pd.read_csv')
    @patch('app.services.fetch_price.yf.download', side_effect=Exception('yfinance error'))
    @patch('pandas.DataFrame.to_csv')
    def test_stooq_fallback(self, mock_to_csv, mock_download, mock_read_csv, mock_makedirs, mock_exists):
        dates = pd.to_datetime(['2020-01-01', '2020-01-02'])
        df_stub = pd.DataFrame({'Close': [3.0, 4.0]}, index=dates)
        df_stub.index.name = 'Date'
        mock_read_csv.return_value = df_stub

        fetch_all_history()
        output = sys.stdout.getvalue()
        
        # Check error handling and fallback
        self.assertIn('✘ yfinance failed for AAPL', output)
        self.assertIn('Using Stooq data source for AAPL', output)
        
        # Check cache saving
        self.assertIn('✓ Saved', output)
        mock_to_csv.assert_called()
        
        # Check final success message
        self.assertIn('✔ All historical prices saved successfully', output)
        print("✔ Test stooq_fallback passed", file=sys.__stdout__)

    @patch('os.path.exists', return_value=True)
    @patch('app.services.fetch_price.pd.read_csv')
    @patch('app.services.fetch_price.yf.download', side_effect=Exception('yfinance error'))
    @patch('pandas.DataFrame.to_csv')
    def test_cache_fallback(self, mock_to_csv, mock_download, mock_read_csv, mock_exists):
        def read_csv_side_effect(path, *args, **kwargs):
            if 'stooq.com' in path:
                raise Exception('stooq error')
            cache_dates = pd.to_datetime(['2020-01-01'])
            cache_df = pd.DataFrame({'Close': [5.0]}, index=cache_dates)
            cache_df.index.name = 'Date'
            return cache_df

        mock_read_csv.side_effect = read_csv_side_effect
        fetch_all_history()
        output = sys.stdout.getvalue()

        # Check error handling and fallback
        self.assertIn('✘ Stooq failed for AAPL', output)
        self.assertIn('Loaded cache for AAPL', output)
        
        # Verify cache file was NOT written to when loaded from cache
        self.assertNotIn('✓ Saved', output)
        mock_to_csv.assert_not_called()
        
        # Check final success message
        self.assertIn('✔ All historical prices saved successfully', output)
        print("✔ Test cache_fallback passed", file=sys.__stdout__)

    @patch('os.makedirs')
    @patch('os.path.exists', side_effect=lambda path: False if path == 'data' else True)
    @patch('app.services.fetch_price.pd.read_csv')
    @patch('app.services.fetch_price.yf.download')
    @patch('pandas.DataFrame.to_csv')
    def test_directory_creation(self, mock_to_csv, mock_download, mock_read_csv, mock_exists, mock_makedirs):
        dates = pd.to_datetime(['2020-01-01', '2020-01-02'])
        df_stub = pd.DataFrame({'Close': [1.0, 2.0]}, index=dates)
        df_stub.index.name = 'Date'
        mock_download.return_value = df_stub

        fetch_all_history()
        output = sys.stdout.getvalue()
        
        # Verify data directory creation check
        self.assertIn('Created data directory', output)
        mock_makedirs.assert_called_once_with('data')
        print("✔ Test directory_creation passed", file=sys.__stdout__)

if __name__ == '__main__':
    unittest.main()
