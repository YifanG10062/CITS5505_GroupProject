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
from app.models import db


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


class HomepageUITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(config_class=TestConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        # ✅ Use in-memory DB (no migrations)
        with cls.app.app_context():
            db.create_all()

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

        # Register or log in user
        cls.driver.get("http://127.0.0.1:5000/user/login")
        cls.driver.find_element(By.ID, "Email").send_keys("test1@test.com")
        cls.driver.find_element(By.ID, "Password").send_keys("123456")
        cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']").click()
        time.sleep(2)

        if "login" in cls.driver.current_url.lower():
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
            cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']").click()
            time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.server_thread.shutdown()

    def test_create_portfolio_button_visibility(self):
        self.driver.get("http://127.0.0.1:5000/portfolios/")
        time.sleep(1)
        button = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Create New Portfolio')]")
        self.assertTrue(button.is_displayed(), "Create New Portfolio button should be visible")
        print("✅ 'Create New Portfolio' button is visible on Portfolio List page.")

    def test_homepage_ui_elements(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/portfolios/")
        time.sleep(2)

        wait = WebDriverWait(driver, 10)
        brand = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "navbar-brand")))
        self.assertIn("the richverse", brand.text.lower())

        list_view_btn = driver.find_element(By.ID, "listViewBtn")
        card_view_btn = driver.find_element(By.ID, "cardViewBtn")
        self.assertTrue(list_view_btn.is_enabled())
        self.assertTrue(card_view_btn.is_enabled())

        card_view_section = driver.find_element(By.ID, "cardView")
        self.assertIn("d-none", card_view_section.get_attribute("class"))

        compare_btn = driver.find_element(By.ID, "compareBtn")
        self.assertIsNotNone(compare_btn)

        html = driver.page_source
        self.assertTrue(
            "Invested $1,000" in html or "No investment history available." in html,
            "Neither investment message was found"
        )

        create_btn = driver.find_element(By.XPATH, "//a[contains(text(),'Create New Portfolio')]")
        self.assertTrue(create_btn.is_displayed())

        list_view_btn.click()
        time.sleep(1)
        headers = [th.text.strip() for th in driver.find_elements(By.XPATH, "//table/thead/tr/th")]
        expected = ["Portfolio Name", "Allocation", "Creator", "Current Value", "Total Return%", "CAGR%", "Volatility", "Max Drawdown", "Action"]
        for col in expected:
            self.assertIn(col, headers)

        share_modal = driver.find_element(By.ID, "sharePortfolioModal")
        self.assertIsNotNone(share_modal)


if __name__ == '__main__':
    unittest.main()
