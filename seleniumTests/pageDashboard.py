import os
import sys
import threading
import time
import unittest

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from werkzeug.serving import make_server

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.config import TestConfig


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


class DashboardPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(config_class=TestConfig)
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

        cls.login_or_register_user()

        cls.ensure_portfolio_exists()

        cls.open_first_dashboard()

    @classmethod
    def login_or_register_user(cls):
        cls.driver.get("http://127.0.0.1:5000/user/login")
        cls.driver.find_element(By.ID, "Email").send_keys("test1@test.com")
        cls.driver.find_element(By.ID, "Password").send_keys("123456")
        cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        time.sleep(2)

        if "login" in cls.driver.current_url.lower():
            print("Login failed — registering new user via UI.")
            cls.driver.get("http://127.0.0.1:5000/user/register")
            cls.driver.find_element(By.ID, "FirstName").send_keys("Test")
            cls.driver.find_element(By.ID, "LastName").send_keys("User")
            cls.driver.find_element(By.ID, "Email").send_keys("test1@test.com")
            cls.driver.find_element(By.ID, "Password").send_keys("123456")
            cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Sign Up']").click()
            time.sleep(2)

            cls.driver.get("http://127.0.0.1:5000/user/login")
            cls.driver.find_element(By.ID, "Email").send_keys("test1@test.com")
            cls.driver.find_element(By.ID, "Password").send_keys("123456")
            cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
            time.sleep(2)

    @classmethod
    def ensure_portfolio_exists(cls):
        cls.driver.get("http://127.0.0.1:5000/portfolios/")
        time.sleep(1)
        portfolio_links = cls.driver.find_elements(By.XPATH, "//a[contains(@href, '/dashboard')]")
        if not portfolio_links:
            print("📌 No portfolios found. Creating one...")
            cls.driver.get("http://127.0.0.1:5000/portfolios/new")
            time.sleep(1)

            # Select 2 assets (assumes asset cards are clickable)
            cards = cls.driver.find_elements(By.CLASS_NAME, "asset-card")
            for i in range(min(2, len(cards))):
                cards[i].click()
                time.sleep(0.5)

            # Set portfolio name
            cls.driver.find_element(By.CLASS_NAME, "edit-icon").click()
            name_input = cls.driver.find_element(By.ID, "portfolio_name")
            name_input.clear()
            name_input.send_keys("PortfolioDemoFortest1")

            # Submit
            cls.driver.find_element(By.ID, "create-portfolio-btn").click()
            time.sleep(2)

    @classmethod
    def open_first_dashboard(cls):
        cls.driver.get("http://127.0.0.1:5000/portfolios/")
        try:
            first_portfolio = WebDriverWait(cls.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/dashboard')]"))
            )
            dashboard_url = first_portfolio.get_attribute("href")
            print(f"▶ Opening dashboard for portfolio: {first_portfolio.text}")
        
            # 👉 Directly navigate instead of clicking
            cls.driver.get(dashboard_url)

            # Confirm dashboard has loaded
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "portfolio-title")))
            time.sleep(1)
        except Exception as e:
            raise Exception("Dashboard page could not be opened.") from e

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.server_thread.shutdown()

    def test_dashboard_ui_elements(self):
        driver = self.driver
        wait = WebDriverWait(driver, 20)

        # Confirm URL includes /dashboard
        self.assertIn("/dashboard", driver.current_url, "Did not land on dashboard page.")

        # Check for '404' or 'not found' if dashboard page is broken
        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        self.assertNotIn("not found", body_text)
        self.assertNotIn("404", body_text)

        # Branding check
        self.assertIn("THE RICHVERSE", driver.page_source)

        # Wait and verify portfolio title
        try:
            portfolio_title_elem = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "portfolio-title"))
            )
            self.assertTrue(len(portfolio_title_elem.text.strip()) > 0)
        except:
            self.fail("Timed out waiting for .portfolio-title element")

        # Wait and verify asset string (e.g., 33% BTC-USD + 33% ...)
        try:
            asset_string_elem = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "overview-asset-string"))
            )
            self.assertIn("%", asset_string_elem.text)
        except:
            self.fail("Timed out waiting for .overview-asset-string element")

        # Metrics section
        for metric_id in ["netWorth", "profit", "volatility", "cumulativeReturn", "cagr", "maxDrawdown", "longestDD"]:
            try:
                elem = wait.until(EC.presence_of_element_located((By.ID, metric_id)))
                self.assertTrue(elem.is_displayed(), f"{metric_id} is not visible")
            except:
                self.fail(f"Timed out waiting for metric ID: {metric_id}")

        # Charts section
        for chart_id in ["cumulativeChart", "heatmapChart", "topMoversChart", "underwaterChart"]:
            try:
                chart = wait.until(EC.presence_of_element_located((By.ID, chart_id)))
                self.assertTrue(chart.is_displayed(), f"{chart_id} chart is not visible")
            except:
                self.fail(f"Timed out waiting for chart ID: {chart_id}")

        print("✅ Dashboard UI structure and metrics successfully validated.")



if __name__ == '__main__':
    unittest.main()
