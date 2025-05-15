import os
import sys
import threading
import time
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from werkzeug.serving import make_server

from app import create_app
from app.config import TestConfig

class ServerThread(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.server = make_server('127.0.0.1', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


class RegisterPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(TestConfig)
        cls.server_thread = ServerThread(cls.app)
        cls.server_thread.start()
        time.sleep(1)
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.server_thread.shutdown()

    def test_register_page_elements(self):
        response = self.client.get("/user/register")
        html = response.get_data(as_text=True)

        # Check status and title
        self.assertEqual(response.status_code, 200)
        self.assertIn("<title>Register - The Richverse</title>", html)

        # Branding section
        self.assertIn("THE RICHVERSE", html)
        self.assertIn("Test your insights with a $1000 investment from 2015.", html)
        self.assertIn("Compare strategies", html)

        # Form labels
        self.assertIn('<label for="FirstName">Firstname</label>', html)
        self.assertIn('<label for="LastName">Lastname</label>', html)
        self.assertIn('<label for="Email">Email</label>', html)
        self.assertIn('<label for="Password">Password</label>', html)

        # Form inputs
        self.assertIn('name="FirstName"', html)
        self.assertIn('name="LastName"', html)
        self.assertIn('name="Email"', html)
        self.assertIn('name="Password"', html)
        self.assertIn('type="submit" value="Sign Up"', html)

        # Navigation links
        self.assertIn('Already a member?', html)
        self.assertIn('href="/user/login"', html)

        # CSS & JS checks (optional but helpful)
        self.assertIn('bootstrap.min.css', html)
        self.assertIn('/static/css/userpage.css', html)
        self.assertIn('bootstrap.bundle.min.js', html)

        print("✅ Register page UI structure validated successfully.")

if __name__ == '__main__':
    unittest.main()
