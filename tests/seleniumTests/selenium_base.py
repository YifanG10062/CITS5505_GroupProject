import os
import sys
import tempfile
import time
import unittest
import threading
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from werkzeug.serving import make_server

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

class SeleniumBaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(TestConfig)

        with cls.app.app_context():
            db.create_all()
            db.session.query(Asset).delete()
            db.session.add_all([
                Asset(asset_code="AAPL", display_name="Apple", full_name="Apple Inc.", type="stock", currency="USD",
                      logo_url="https://logo.clearbit.com/apple.com", strategy_description="Technology stock"),
                Asset(asset_code="MSFT", display_name="Microsoft", full_name="Microsoft Corp", type="stock", currency="USD",
                      logo_url="https://logo.clearbit.com/microsoft.com", strategy_description="Software stock"),
                Asset(asset_code="TSLA", display_name="Tesla", full_name="Tesla Inc.", type="stock", currency="USD",
                      logo_url="https://logo.clearbit.com/tesla.com", strategy_description="EV and clean energy stock"),
            ])
            db.session.commit()

        cls.server_thread = ServerThread(cls.app)
        cls.server_thread.start()

        for _ in range(20):
            try:
                if requests.get("http://127.0.0.1:5000").status_code == 200:
                    break
            except requests.ConnectionError:
                time.sleep(0.5)

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.maximize_window()

        cls._ensure_logged_in()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.server_thread.shutdown()

    @classmethod
    def _ensure_logged_in(cls):
        cls.driver.get("http://127.0.0.1:5000/user/login")

        # Try login first
        try:
            cls.driver.find_element(By.ID, "Email").send_keys("testuser@example.com")
            cls.driver.find_element(By.ID, "Password").send_keys("password123")
            cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

            # Wait for redirect to /portfolios
            WebDriverWait(cls.driver, 10).until(
                EC.url_contains("/portfolios")
            )
            return

        except Exception:
            print("Login failed — attempting registration...")

        # Try registration if login fails
        cls.driver.get("http://127.0.0.1:5000/user/register")
        cls.driver.find_element(By.ID, "FirstName").send_keys("Test")
        cls.driver.find_element(By.ID, "LastName").send_keys("User")
        cls.driver.find_element(By.ID, "Email").send_keys("testuser@example.com")
        cls.driver.find_element(By.ID, "Password").send_keys("password123")
        cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Sign Up']").click()

        # Wait for successful redirect to /portfolios or /login
        WebDriverWait(cls.driver, 10).until(
            lambda driver: "/portfolios" in driver.current_url or "/login" in driver.current_url
        )

        # If redirected to login, login again
        if "/login" in cls.driver.current_url:
            cls.driver.find_element(By.ID, "Email").clear()
            cls.driver.find_element(By.ID, "Email").send_keys("testuser@example.com")
            cls.driver.find_element(By.ID, "Password").send_keys("password123")
            cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

            # Final confirmation
            WebDriverWait(cls.driver, 10).until(
                EC.url_contains("/portfolios")
            )

            cls.driver.get("http://127.0.0.1:5000/user/login")

            if "/portfolios" in cls.driver.current_url:
                return

            try:
                email_input = WebDriverWait(cls.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "Email"))
                )
                email_input.send_keys("testuser@example.com")
                cls.driver.find_element(By.ID, "Password").send_keys("password123")
                cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

                WebDriverWait(cls.driver, 5).until(EC.url_contains("/portfolios"))
            except:
                cls.driver.get("http://127.0.0.1:5000/user/register")

                WebDriverWait(cls.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "FirstName"))
                )
                cls.driver.find_element(By.ID, "FirstName").send_keys("Test")
                cls.driver.find_element(By.ID, "LastName").send_keys("User")
                cls.driver.find_element(By.ID, "Email").send_keys("testuser@example.com")
                cls.driver.find_element(By.ID, "Password").send_keys("password123")
                cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Sign Up']").click()

                WebDriverWait(cls.driver, 5).until(EC.url_contains("/user/login"))

                cls.driver.find_element(By.ID, "Email").send_keys("testuser@example.com")
                cls.driver.find_element(By.ID, "Password").send_keys("password123")
                cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

                WebDriverWait(cls.driver, 5).until(EC.url_contains("/portfolios"))
