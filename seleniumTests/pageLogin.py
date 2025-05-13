import os
import sys
import threading
import time
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask.testing import FlaskClient
from flask_migrate import upgrade
from werkzeug.security import generate_password_hash
from werkzeug.serving import make_server

from app import create_app
from app.config import TestConfig
from app.models import User, db


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


class LoginPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create and start the Flask app server
        cls.app = create_app(config_class=TestConfig)
        cls.app.app_context().push()
            # --- Apply migrations ---
        try:
            upgrade()  # This will apply all Alembic migrations
        except Exception as e:
            print("Migration error:", e)
            raise
        cls.server_thread = ServerThread(cls.app)
        cls.server_thread.start()
        time.sleep(1)

        # Create test client (no browser needed)
        cls.client: FlaskClient = cls.app.test_client()


    @classmethod
    def tearDownClass(cls):
        cls.server_thread.shutdown()

    def test_login_page_elements(self):
        response = self.client.get("/user/login")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("THE RICHVERSE", html)
        self.assertIn("Sign In", html)
        self.assertIn('name="Email"', html)
        self.assertIn('name="Password"', html)
        self.assertIn('value="Login"', html)
        self.assertIn("Not a member?", html)
        self.assertIn("Forgot Password?", html)



if __name__ == "__main__":
    unittest.main()
