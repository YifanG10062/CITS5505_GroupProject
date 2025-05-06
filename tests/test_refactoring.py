import unittest
from app import create_app, db
from app.models.user import User
from app.models.portfolio import PortfolioSummary
from config import TestConfig

class RefactoringTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_register_login(self):
        # Test registration
        response = self.client.post('/register', data={
            'FirstName': 'Test',
            'LastName': 'User',
            'Email': 'test@example.com',
            'Password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify username is set correctly
        user = User.query.filter_by(user_email='test@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'Test')
        
        # Test login
        response = self.client.post('/login', data={
            'Email': 'test@example.com',
            'Password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
    def test_portfolio_user_info(self):
        # Create test user
        user = User(
            username='Test',
            user_fName='Test',
            user_lName='User',
            user_email='test@example.com',
            user_pswd='hashed_password'
        )
        db.session.add(user)
        db.session.commit()
        
        # Create test portfolio
        portfolio = PortfolioSummary(
            portfolio_name='Test Portfolio',
            user_id=user.id,
            creator_id=user.id,
            user_username=user.username,
            user_email=user.user_email,
            creator_username=user.username,
            creator_email=user.user_email,
            allocation_json='{}',
            start_date='2023-01-01',
            initial_amount=1000.0
        )
        db.session.add(portfolio)
        db.session.commit()
        
        # Change username
        user.username = 'Updated'
        db.session.commit()
        
        # Test user info update method
        portfolio.update_user_info()
        db.session.commit()
        
        # Verify updated information
        updated_portfolio = PortfolioSummary.query.get(portfolio.portfolio_id)
        self.assertEqual(updated_portfolio.user_username, 'Updated')

if __name__ == '__main__':
    unittest.main()
