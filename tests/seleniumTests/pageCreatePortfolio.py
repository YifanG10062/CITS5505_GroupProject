import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium_base import SeleniumBaseTest  # Reuse memory-safe base class


class CreatePortfolioPageTest(SeleniumBaseTest):

    def test_create_portfolio_page_ui_elements(self):
        self.driver.get("http://127.0.0.1:5000/portfolios/new")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form#portfolio-form"))
        )

        html = self.driver.page_source
        title = self.driver.title.strip()

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
