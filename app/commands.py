from app.models.user import User
from app.models.portfolio import PortfolioSummary
from flask import current_app
import os
from werkzeug.security import generate_password_hash
import click
from flask.cli import with_appcontext
import sys

@click.command('refresh-user-info')
@with_appcontext
def refresh_user_info_command():
    """Refresh all user information in portfolio summaries."""
    from app import db
    portfolios = PortfolioSummary.query.all()
    updated_count = 0
    
    for portfolio in portfolios:
        portfolio.update_user_info()
        updated_count += 1
    
    db.session.commit()
    click.echo(f"Updated user information for {updated_count} portfolios.")

def setup_dev_environment():
    """Setup test users and other configurations in development environment"""
    # Only execute in development environment
    if os.environ.get('FLASK_ENV') != 'development' and not current_app.config.get('TESTING', False):
        return
    
    # Ensure db is initialized
    from app import db
    
    # Check if database tables exist, create them if not
    try:
        # Check and create test users
        create_test_users()
    except Exception as e:
        print(f"Error setting up development environment: {e}")
    
    # Additional development environment initialization code can be added here
    print("Development environment setup completed, test users are ready")

def create_test_users():
    """Create test users if they don't exist"""
    from app import db
    
    # Ensure User is a SQLAlchemy model
    # If User is not a subclass of db.Model, check and handle it this way
    if not hasattr(User, 'query'):
        print("Error: User model has no query attribute, please check the User class definition")
        return
    
    test_users = [
        {
            'username': 'rich1',
            'user_email': 'rich1@example.com',
            'user_pswd': 'password123',
            'user_fName': 'Rich',
            'user_lName': 'One'
        },
        {
            'username': 'rich2',
            'user_email': 'rich2@example.com',
            'user_pswd': 'password123',
            'user_fName': 'Rich',
            'user_lName': 'Two'
        },
        {
            'username': 'rich3',
            'user_email': 'rich3@example.com',
            'user_pswd': 'password123',
            'user_fName': 'Rich',
            'user_lName': 'Three'
        }
    ]
    
    for user_data in test_users:
        # Check if user already exists
        existing_user = User.query.filter_by(user_email=user_data['user_email']).first()
        if not existing_user:
            # Create new user
            new_user = User(
                username=user_data['username'],
                user_email=user_data['user_email'],
                user_pswd=generate_password_hash(user_data['user_pswd']),
                user_fName=user_data['user_fName'],
                user_lName=user_data['user_lName']
            )
            db.session.add(new_user)
            print(f"Created test user: {user_data['username']}")
    
    # Commit all changes
    db.session.commit()

@click.command('setup-dev')
@with_appcontext
def setup_dev_command():
    """Command to manually setup development environment"""
    setup_dev_environment()
    click.echo('Development environment setup completed.')

def init_app(app):
    """Register commands with the Flask application"""
    app.cli.add_command(setup_dev_command)
    app.cli.add_command(refresh_user_info_command)
    
    # Only run dev setup if FLASK_ENV is development AND running the actual server
    if (
        os.environ.get('FLASK_ENV') == 'development'
        and 'flask' in sys.argv[0]    # basic CLI check
        and 'run' in sys.argv    # only when running `flask run`
    ) or app.config.get('TESTING', False):
        with app.app_context():
            setup_dev_environment()
