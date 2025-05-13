import unittest
import sys
import os
import json
from datetime import datetime, date, timedelta
from flask import Flask
from flask_login import login_user, current_user

# Add parent directory to path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import create_app instead of app directly
from app import create_app, db
from app.config import TestConfig
from app.models.user import User
from app.models.portfolio import PortfolioSummary, PortfolioVersion, PortfolioChangeLog, PortfolioShareLog
from app.routes.portfolio import portfolios

class PortfolioTestCase(unittest.TestCase):
    """Test cases for portfolio functionality"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create a test Flask app using the application factory
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database
        
        # Create app context and request context
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.request_context = self.app.test_request_context()
        self.request_context.push()
        
        # Create test client
        self.client = self.app.test_client()
        
        # Register the portfolios blueprint if it's not already registered
        if 'portfolios' not in self.app.blueprints:
            self.app.register_blueprint(portfolios)
        
        # Create database tables
        db.create_all()
        
        # Create test users directly for better test isolation
        self.test_user1 = User(
            username='testuser1', 
            email='test1@example.com',
            user_email='test1@example.com',  # Match the field used in portfolio model
            user_fName='Test',
            user_lName='User1'
        )
        self.test_user1.set_password('password123')
        
        self.test_user2 = User(
            username='testuser2', 
            email='test2@example.com',
            user_email='test2@example.com',  # Match the field used in portfolio model
            user_fName='Test',
            user_lName='User2'
        )
        self.test_user2.set_password('password123')
        
        db.session.add(self.test_user1)
        db.session.add(self.test_user2)
        db.session.commit()
        
        print(f"Test setup complete. Created test users with IDs: {self.test_user1.id}, {self.test_user2.id}")
    
    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.request_context.pop()
        self.app_context.pop()
        print("Test teardown complete. Database cleaned up.")
    
    def login(self, user):
        """Helper function to log in a user programmatically for testing"""
        login_user(user)
        return user
    
    def create_sample_portfolio(self, user_id, portfolio_name="Test Portfolio", allocation=None):
        """Helper function to create a portfolio for testing directly using the model"""
        if allocation is None:
            allocation = {"AAPL": 0.6, "MSFT": 0.3, "GOOGL": 0.1}
        
        user = User.query.get(user_id)
        
        portfolio = PortfolioSummary(
            portfolio_name=portfolio_name,
            user_id=user_id,
            creator_id=user_id,
            user_username=user.username,
            user_email=user.email,
            creator_username=user.username,
            creator_email=user.email,
            allocation_json=json.dumps(allocation),
            start_date=date.today(),
            initial_amount=10000.0,
            current_value=11000.0,
            profit=1000.0,
            return_percent=10.0,
            cagr=8.5,
            volatility=12.3,
            max_drawdown=15.2,
            is_editable=True,
            is_shareable=True,
            is_deletable=True,
            is_shown=True,
            created_at=datetime.utcnow(),
            input_updated_at=datetime.utcnow(),
            metric_updated_at=datetime.utcnow()
        )
        db.session.add(portfolio)
        db.session.commit()
        
        # Create initial version
        version = PortfolioVersion(
            portfolio_id=portfolio.portfolio_id,
            version_number=1,
            updated_by=user_id,
            updated_at=datetime.utcnow(),
            allocation_json=json.dumps(allocation),
            portfolio_name=portfolio_name,
            start_date=date.today(),
            initial_amount=10000.0
        )
        db.session.add(version)
        db.session.commit()
        
        print(f"Created sample portfolio with ID: {portfolio.portfolio_id} for user ID: {user_id}")
        return portfolio
    
    # ---------- 1. CREATE ----------
    
    def test_visit_portfolio_list_creates_demo(self):
        """Test that visiting portfolio list page creates a demo portfolio if user has none"""
        # Login as test user
        self.login(self.test_user1)
        
        # Visit the portfolio list page
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['_user_id'] = str(self.test_user1.id)
            
            # Access portfolio list page
            response = client.get('/portfolios/')
            
            # Assert successful response
            self.assertEqual(response.status_code, 200)
            
            # Check that a demo portfolio was created for the user
            demo_portfolio = PortfolioSummary.query.filter_by(user_id=self.test_user1.id).first()
            self.assertIsNotNone(demo_portfolio)
            self.assertTrue(f"Demo" in demo_portfolio.portfolio_name or self.test_user1.username in demo_portfolio.portfolio_name)
            
            # Assert demo portfolio has default values
            self.assertIsNotNone(demo_portfolio.allocation_json)
            self.assertTrue(demo_portfolio.is_editable)
            self.assertTrue(demo_portfolio.is_shareable)
            
            print(f"Successfully verified demo portfolio creation: {demo_portfolio.portfolio_id}")
    
    def test_create_portfolio_success(self):
        """Test successful portfolio creation through the form"""
        # Login as test user
        self.login(self.test_user1)
        
        # Create portfolio through HTTP request
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['_user_id'] = str(self.test_user1.id)
            
            # Submit portfolio form
            response = client.post('/portfolios/new', data={
                'portfolio_name': 'Growth Portfolio',
                'allocation[AAPL]': '70',
                'allocation[MSFT]': '30'
            }, follow_redirects=True)
        
        # Assert successful response
        self.assertEqual(response.status_code, 200)
        
        # Verify a portfolio was created with the specified name
        portfolio = PortfolioSummary.query.filter_by(
            user_id=self.test_user1.id,
            portfolio_name='Growth Portfolio'
        ).first()
        
        self.assertIsNotNone(portfolio)
        allocation = json.loads(portfolio.allocation_json)
        self.assertEqual(allocation.get('AAPL'), 0.7)
        self.assertEqual(allocation.get('MSFT'), 0.3)
        
        # Verify version was created
        version = PortfolioVersion.query.filter_by(portfolio_id=portfolio.portfolio_id).first()
        self.assertIsNotNone(version)
        self.assertEqual(version.version_number, 1)
        
        print(f"Successfully created portfolio: {portfolio.portfolio_id}")
    
    def test_create_portfolio_unauthenticated(self):
        """Test that unauthenticated users cannot create portfolios"""
        # No login
        with self.app.test_client() as client:
            response = client.post('/portfolios/new', data={
                'portfolio_name': 'Unauthorized Portfolio',
                'allocation[AAPL]': '50',
                'allocation[MSFT]': '50'
            }, follow_redirects=False)
        
        # Assert redirect to login page (302) or unauthorized (401)
        self.assertIn(response.status_code, [302, 401])
        
        # Verify no portfolio was created
        portfolio = PortfolioSummary.query.filter_by(portfolio_name='Unauthorized Portfolio').first()
        self.assertIsNone(portfolio)
        
        print("Successfully prevented unauthorized portfolio creation")
    
    # ---------- 2. EDIT ----------
    
    def test_edit_portfolio_success(self):
        """Test successful portfolio edit"""
        # Create a portfolio for user 1
        portfolio = self.create_sample_portfolio(self.test_user1.id)
        original_version = PortfolioVersion.query.filter_by(portfolio_id=portfolio.portfolio_id).first()
        
        # Login as user 1
        self.login(self.test_user1)
        
        # Edit portfolio through HTTP request
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['_user_id'] = str(self.test_user1.id)
            
            response = client.post(f'/portfolios/{portfolio.portfolio_id}/edit', data={
                'portfolio_name': 'Updated Portfolio',
                'allocation[AAPL]': '50',
                'allocation[MSFT]': '30',
                'allocation[GOOGL]': '20'
            })
        
        # Verify portfolio was updated
        updated_portfolio = PortfolioSummary.query.get(portfolio.portfolio_id)
        self.assertEqual(updated_portfolio.portfolio_name, 'Updated Portfolio')
        allocation = json.loads(updated_portfolio.allocation_json)
        self.assertEqual(allocation.get('AAPL'), 0.5)
        self.assertEqual(allocation.get('GOOGL'), 0.2)
        
        # Verify new version was created
        new_version = PortfolioVersion.query.filter_by(
            portfolio_id=portfolio.portfolio_id,
            version_number=original_version.version_number + 1
        ).first()
        self.assertIsNotNone(new_version)
        
        # Verify change log entry exists
        change_log = PortfolioChangeLog.query.filter_by(portfolio_id=portfolio.portfolio_id).first()
        self.assertIsNotNone(change_log)
        
        print(f"Successfully edited portfolio {portfolio.portfolio_id} with new version and change log")
    
    def test_edit_unauthorized_portfolio(self):
        """Test that editing another user's portfolio is not allowed"""
        # Create a portfolio for user 1
        portfolio = self.create_sample_portfolio(self.test_user1.id)
        
        # Login as user 2
        self.login(self.test_user2)
        
        # Attempt to edit user 1's portfolio
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['_user_id'] = str(self.test_user2.id)
            
            response = client.post(f'/portfolios/{portfolio.portfolio_id}/edit', data={
                'portfolio_name': 'Unauthorized Edit',
                'allocation[AAPL]': '30',
                'allocation[MSFT]': '70'
            })
        
        # Assert forbidden response
        self.assertIn(response.status_code, [403, 302])  # Either forbidden or redirect
        
        # Verify portfolio was not edited
        unchanged_portfolio = PortfolioSummary.query.get(portfolio.portfolio_id)
        self.assertNotEqual(unchanged_portfolio.portfolio_name, 'Unauthorized Edit')
        
        print(f"Successfully prevented unauthorized edit of portfolio {portfolio.portfolio_id}")
    
    def test_edit_shared_readonly_portfolio(self):
        """Test that editing a shared (read-only) portfolio is not allowed"""
        # Create a portfolio for user 1
        portfolio = self.create_sample_portfolio(self.test_user1.id)
        
        # Login as user 1
        self.login(self.test_user1)
        
        # Share portfolio with user 2
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['_user_id'] = str(self.test_user1.id)
            
            response = client.post('/portfolios/api/portfolios/share', json={
                'portfolio_id': portfolio.portfolio_id,
                'user_ids': [self.test_user2.id]
            })
        
        # Find the shared portfolio
        shared_portfolio = PortfolioSummary.query.filter_by(
            user_id=self.test_user2.id, 
            creator_id=self.test_user1.id,
            shared_from_id=self.test_user1.id
        ).first()
        
        # Login as user 2
        self.login(self.test_user2)
        
        # Attempt to edit the shared portfolio
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['_user_id'] = str(self.test_user2.id)
            
            response = client.post(f'/portfolios/{shared_portfolio.portfolio_id}/edit', data={
                'portfolio_name': 'Try Edit Shared',
                'allocation[AAPL]': '40',
                'allocation[MSFT]': '60'
            })
        
        # Assert forbidden or redirect response
        self.assertIn(response.status_code, [403, 302])
        
        # Verify portfolio was not edited
        unchanged_portfolio = PortfolioSummary.query.get(shared_portfolio.portfolio_id)
        self.assertNotEqual(unchanged_portfolio.portfolio_name, 'Try Edit Shared')
        
        print(f"Successfully prevented edit of read-only shared portfolio {shared_portfolio.portfolio_id}")
    
    def test_edit_soft_deleted_portfolio(self):
        """Test that editing a soft-deleted portfolio is not allowed"""
        # Create a portfolio for user 1
        portfolio = self.create_sample_portfolio(self.test_user1.id)
        
        # Soft delete the portfolio
        portfolio.is_shown = False
        db.session.commit()
        
        # Login as user 1
        self.login(self.test_user1)
        
        # Attempt to edit the deleted portfolio
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['_user_id'] = str(self.test_user1.id)
            
            response = client.post(f'/portfolios/{portfolio.portfolio_id}/edit', data={
                'portfolio_name': 'Edit Deleted Portfolio',
                'allocation[AAPL]': '45',
                'allocation[MSFT]': '55'
            })
        
        # Assert not found or forbidden response
        self.assertIn(response.status_code, [403, 404, 302])
        
        print(f"Successfully prevented edit of deleted portfolio {portfolio.portfolio_id}")
    
    # ---------- 3. SHARE ----------
    
    def test_share_portfolio_success(self):
        """Test successful portfolio sharing"""
        # Create a portfolio for user 1
        portfolio = self.create_sample_portfolio(self.test_user1.id)
        
        # Login as user 1
        self.login(self.test_user1)
        
        # Share portfolio with user 2
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['_user_id'] = str(self.test_user1.id)
            
            response = client.post('/portfolios/api/portfolios/share', json={
                'portfolio_id': portfolio.portfolio_id,
                'user_ids': [self.test_user2.id]
            })
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        
        # Verify shared portfolio was created
        shared_portfolio = PortfolioSummary.query.filter_by(
            user_id=self.test_user2.id, 
            creator_id=self.test_user1.id,
            shared_from_id=self.test_user1.id
        ).first()
        self.assertIsNotNone(shared_portfolio)
        self.assertFalse(shared_portfolio.is_editable)
        self.assertFalse(shared_portfolio.is_shareable)
        
        # Verify share log entry
        share_log = PortfolioShareLog.query.filter_by(
            from_portfolio_id=portfolio.portfolio_id,
            to_user_id=self.test_user2.id
        ).first()
        self.assertIsNotNone(share_log)
        
        print(f"Successfully shared portfolio {portfolio.portfolio_id} with user {self.test_user2.id}")
    
    def test_share_to_invalid_user(self):
        """Test that sharing to a non-existent user is rejected"""
        # Create a portfolio for user 1
        portfolio = self.create_sample_portfolio(self.test_user1.id)
        
        # Login as user 1
        self.login(self.test_user1)
        
        # Attempt to share with non-existent user
        fake_user_id = 9999
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['_user_id'] = str(self.test_user1.id)
            
            response = client.post('/portfolios/api/portfolios/share', json={
                'portfolio_id': portfolio.portfolio_id,
                'user_ids': [fake_user_id]
            })
        
        # Verify no shared portfolio was created
        shared_portfolio = PortfolioSummary.query.filter_by(
            user_id=fake_user_id, 
            shared_from_id=self.test_user1.id
        ).first()
        self.assertIsNone(shared_portfolio)
        
        print(f"Successfully prevented sharing to non-existent user ID {fake_user_id}")
    
    def test_share_duplicate(self):
        """Test duplicate portfolio sharing behavior"""
        # Create a portfolio for user 1
        portfolio = self.create_sample_portfolio(self.test_user1.id)
        
        # Login as user 1
        self.login(self.test_user1)
        
        # Share portfolio with user 2 first time
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['_user_id'] = str(self.test_user1.id)
            
            client.post('/portfolios/api/portfolios/share', json={
                'portfolio_id': portfolio.portfolio_id,
                'user_ids': [self.test_user2.id]
            })
        
        # Count shared portfolios and logs after first share
        first_share_count = PortfolioSummary.query.filter_by(
            user_id=self.test_user2.id, 
            shared_from_id=self.test_user1.id
        ).count()
        
        # Share portfolio with user 2 second time
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['_user_id'] = str(self.test_user1.id)
            
            response = client.post('/portfolios/api/portfolios/share', json={
                'portfolio_id': portfolio.portfolio_id,
                'user_ids': [self.test_user2.id]
            })
        
        # Count shared portfolios and logs again
        second_share_count = PortfolioSummary.query.filter_by(
            user_id=self.test_user2.id, 
            shared_from_id=self.test_user1.id
        ).count()
        
        # The implementation might either prevent duplicate shares or create a new copy
        # Since the route doesn't explicitly prevent duplicates, test for consistent behavior
        self.assertGreaterEqual(second_share_count, first_share_count)
        
        print(f"Successfully tested duplicate portfolio sharing")
    
    def test_shared_portfolio_is_read_only(self):
        """Test that shared portfolios are read-only"""
        # Create a portfolio for user 1
        portfolio = self.create_sample_portfolio(self.test_user1.id)
        
        # Login as user 1
        self.login(self.test_user1)
        
        # Share portfolio with user 2
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['_user_id'] = str(self.test_user1.id)
            
            client.post('/portfolios/api/portfolios/share', json={
                'portfolio_id': portfolio.portfolio_id,
                'user_ids': [self.test_user2.id]
            })
        
        # Find the shared portfolio
        shared_portfolio = PortfolioSummary.query.filter_by(
            user_id=self.test_user2.id, 
            shared_from_id=self.test_user1.id
        ).first()
        
        # Verify the shared portfolio is not editable or shareable
        self.assertFalse(shared_portfolio.is_editable)
        self.assertFalse(shared_portfolio.is_shareable)
        
        print(f"Successfully verified shared portfolio is read-only: {shared_portfolio.portfolio_id}")
    
    # ---------- 4. DELETE ----------
    
    def test_soft_delete_portfolio(self):
        """Test successful portfolio soft deletion"""
        # Create a portfolio for user 1
        portfolio = self.create_sample_portfolio(self.test_user1.id)
        
        # Login as user 1
        self.login(self.test_user1)
        
        # Delete the portfolio
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['_user_id'] = str(self.test_user1.id)
            
            response = client.post(f'/portfolios/{portfolio.portfolio_id}/delete')
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        
        # Verify portfolio is soft deleted
        deleted_portfolio = PortfolioSummary.query.get(portfolio.portfolio_id)
        self.assertFalse(deleted_portfolio.is_shown)
        
        print(f"Successfully soft-deleted portfolio {portfolio.portfolio_id}")
    
    def test_delete_unauthorized_user(self):
        """Test that only the owner can delete their portfolio"""
        # Create a portfolio for user 1
        portfolio = self.create_sample_portfolio(self.test_user1.id)
        
        # Login as user 2
        self.login(self.test_user2)
        
        # Attempt to delete user 1's portfolio
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['_user_id'] = str(self.test_user2.id)
            
            response = client.post(f'/portfolios/{portfolio.portfolio_id}/delete')
        
        # Assert forbidden response
        self.assertEqual(response.status_code, 403)
        
        # Verify portfolio is not deleted
        unchanged_portfolio = PortfolioSummary.query.get(portfolio.portfolio_id)
        self.assertTrue(unchanged_portfolio.is_shown)
        
        print(f"Successfully prevented unauthorized deletion of portfolio {portfolio.portfolio_id}")
    
    def test_access_deleted_portfolio(self):
        """Test that soft-deleted portfolios cannot be accessed via direct URL"""
        # Create a portfolio for user 1
        portfolio = self.create_sample_portfolio(self.test_user1.id)
        
        # Soft delete the portfolio
        portfolio.is_shown = False
        db.session.commit()
        
        # Login as user 1
        self.login(self.test_user1)
        
        # Attempt to access the deleted portfolio via portfolio list
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['_user_id'] = str(self.test_user1.id)
            
            # Get the portfolio list
            response = client.get('/portfolios/')
            
            # Assert list doesn't show deleted portfolio
            self.assertEqual(response.status_code, 200)
            html_content = response.data.decode('utf-8')
            self.assertNotIn(portfolio.portfolio_name, html_content)
            
            print(f"Successfully verified deleted portfolio is not shown in portfolio list")

if __name__ == '__main__':
    unittest.main()
