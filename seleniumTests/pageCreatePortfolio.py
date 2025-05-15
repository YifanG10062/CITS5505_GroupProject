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


class CreatePortfolioPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(config_class=TestConfig)
        cls.server_thread = ServerThread(cls.app)
        cls.server_thread.start()

        # Wait for server to start
        for _ in range(20):
            try:
                if requests.get("http://127.0.0.1:5000").status_code == 200:
                    break
            except requests.ConnectionError:
                time.sleep(0.5)
        else:
            raise Exception("Server did not start in time.")

        # Start Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.maximize_window()

        # Attempt login
        cls.driver.get("http://127.0.0.1:5000/user/login")
        cls.driver.find_element(By.ID, "Email").send_keys("testuser@example.com")
        cls.driver.find_element(By.ID, "Password").send_keys("password123")
        cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        time.sleep(2)

        # Register via UI if login fails
        if "login" in cls.driver.current_url.lower():
            print("Login failed — registering user via UI.")
            cls.driver.get("http://127.0.0.1:5000/user/register")
            cls.driver.find_element(By.ID, "FirstName").send_keys("Test")
            cls.driver.find_element(By.ID, "LastName").send_keys("User")
            cls.driver.find_element(By.ID, "Email").send_keys("testuser@example.com")
            cls.driver.find_element(By.ID, "Password").send_keys("password123")
            cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Sign Up']").click()
            time.sleep(2)

            cls.driver.get("http://127.0.0.1:5000/user/login")
            cls.driver.find_element(By.ID, "Email").send_keys("testuser@example.com")
            cls.driver.find_element(By.ID, "Password").send_keys("password123")
            cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
            time.sleep(2)

            if "login" in cls.driver.current_url.lower():
                raise Exception("Login failed even after registration.")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.server_thread.shutdown()

    def test_create_portfolio_page_ui_elements(self):
        self.driver.get("http://127.0.0.1:5000/portfolios/new")
        time.sleep(2)

        html = self.driver.page_source

        self.assertEqual(self.driver.title.strip(), "Create New Portfolio - The Richverse")
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

        # Use visible text instead of brittle HTML match
        subheading = self.driver.find_element(By.CSS_SELECTOR, "p.page-subheading").text
        self.assertIn("pick up to", subheading)
        self.assertIn("3 assets", subheading)

        print("✅ Create Portfolio page structure successfully validated.")

if __name__ == '__main__':
    unittest.main()
