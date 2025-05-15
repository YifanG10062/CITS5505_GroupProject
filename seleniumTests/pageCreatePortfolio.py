import os
import sys
import threading
import time
import unittest
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from werkzeug.serving import make_server

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.config import TestConfig
from app.models.asset import Asset


class ServerThread(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ctx = app.app_context()

    def run(self):
        with self.ctx:
            self.server = make_server('127.0.0.1', 5000, self.app)
            self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


class CreatePortfolioPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(config_class=TestConfig)

        # Seed required assets
        with cls.app.app_context():
            db.create_all()
            db.session.query(Asset).delete()
            db.session.add_all([
                Asset(
                    asset_code="AAPL",
                    display_name="Apple",
                    full_name="Apple Inc.",
                    type="stock",
                    currency="USD",
                    logo_url="https://logo.clearbit.com/apple.com",
                    strategy_description="Technology stock"
                ),
                Asset(
                    asset_code="MSFT",
                    display_name="Microsoft",
                    full_name="Microsoft Corp",
                    type="stock",
                    currency="USD",
                    logo_url="https://logo.clearbit.com/microsoft.com",
                    strategy_description="Software stock"
                ),
                Asset(
                    asset_code="TSLA",
                    display_name="Tesla",
                    full_name="Tesla Inc.",
                    type="stock",
                    currency="USD",
                    logo_url="https://logo.clearbit.com/tesla.com",
                    strategy_description="EV and clean energy stock"
                ),
            ])
            db.session.commit()

        # Start Flask test server
        cls.server_thread = ServerThread(cls.app)
        cls.server_thread.start()

        for _ in range(20):
            try:
                if requests.get("http://127.0.0.1:5000").status_code == 200:
                    break
            except requests.ConnectionError:
                time.sleep(0.5)
        else:
            raise RuntimeError("Flask test server did not start in time.")

        # Launch browser in headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.maximize_window()

        # Register/login user
        cls._ensure_logged_in()

    @classmethod
    def _ensure_logged_in(cls):
        cls.driver.get("http://127.0.0.1:5000/user/login")

        try:
            cls.driver.find_element(By.ID, "Email").send_keys("testuser@example.com")
            cls.driver.find_element(By.ID, "Password").send_keys("password123")
            cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
            WebDriverWait(cls.driver, 5).until(EC.url_changes("http://127.0.0.1:5000/user/login"))
        except:
            print("Login failed — registering user via UI.")
            cls.driver.get("http://127.0.0.1:5000/user/register")
            cls.driver.find_element(By.ID, "FirstName").send_keys("Test")
            cls.driver.find_element(By.ID, "LastName").send_keys("User")
            cls.driver.find_element(By.ID, "Email").send_keys("testuser@example.com")
            cls.driver.find_element(By.ID, "Password").send_keys("password123")
            cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Sign Up']").click()
            WebDriverWait(cls.driver, 5).until(EC.url_contains("/user/login"))

            cls.driver.find_element(By.ID, "Email").send_keys("testuser@example.com")
            cls.driver.find_element(By.ID, "Password").send_keys("password123")
            cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
            WebDriverWait(cls.driver, 5).until_not(EC.url_contains("/login"))

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.server_thread.shutdown()

    def test_create_portfolio_page_ui_elements(self):
        self.driver.get("http://127.0.0.1:5000/portfolios/new")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form#portfolio-form"))
        )

        html = self.driver.page_source
        title = self.driver.title.strip()

        # Assertions
        self.assertEqual(title, "Create New Portfolio - The Richverse")
        self.assertIn("Build your Portfolio in", html)
        self.assertIn("$1,000", html)
        self.assertIn("Apple Inc.", html)
        self.assertIn("Microsoft Corp", html)
        self.assertIn("Tesla Inc.", html)
        self.assertIn("Initial Amount", html)
        self.assertIn("Start From", html)
        self.assertIn("Portfolio Name", html)
        self.assertIn("id=\"portfolio_name\"", html)
        self.assertIn("Create Portfolio", html)
        self.assertIn("csrf_token", html)
        self.assertIn("THE RICHVERSE", html)
        self.assertIn("portfolio.css", html)

        subheading = self.driver.find_element(By.CSS_SELECTOR, "p.page-subheading").text
        self.assertIn("pick up to", subheading.lower())
        self.assertIn("3 assets", subheading)

        print("✅ Create Portfolio page structure successfully validated.")

    def test_create_portfolio_page_has_asset_cards(self):
        self.driver.get("http://127.0.0.1:5000/portfolios/new")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "asset-card"))
        )
        cards = self.driver.find_elements(By.CLASS_NAME, "asset-card")
        self.assertGreaterEqual(len(cards), 1, "Expected at least one asset card")

if __name__ == '__main__':
    unittest.main()
