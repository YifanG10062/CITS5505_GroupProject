import os
import sys
import unittest

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.config import TestConfig
from app.models.user import User


class LoginTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    # def test_register_login(self):
    #         # Test registration
    #     response = self.client.post('/register', data={
    #         'FirstName': 'Test',
    #         'LastName': 'User',
    #         'Email': 'test@example.com',
    #         'Password': 'password123'
    #     }, follow_redirects=True)
    #     user = User.query.filter_by(user_email='test@example.com').first()
    #     self.assertIsNotNone(user)
    #     self.assertEqual(user.username, 'Test')
    #     self.assertEqual(response.status_code, 200)

        # Create a user for login tests
        self.test_user = User(
            username='TestUser',
            user_fName='Test',
            user_lName='User',
            user_email='test@example.com',
            user_pswd='password@12'  # Use hashed password if needed
        )
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()



    def test_login_page_loads(self):
        response = self.client.get('/user/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sign In", response.data)

    def test_login_valid_credentials(self):
        response = self.client.post('/user/login', data={
            'Email': 'test@example.com',
            'Password': 'password@12'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"The Richverse", response.data)  

    def test_login_invalid_password(self):
        response = self.client.post('/user/login', data={
            'Email': 'test@example.com',
            'Password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b"Invalid email or password", response.data)

    def test_login_nonexistent_user(self):
        response = self.client.post('/user/login', data={
            'Email': 'nonexistent@example.com',
            'Password': 'anyvalue'
        }, follow_redirects=True)
        self.assertIn(b"Invalid email or password", response.data)

if __name__ == '__main__':
    unittest.main()
