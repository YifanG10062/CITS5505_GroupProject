import os
import sys
import click
from flask import current_app
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from flask_migrate import init as migrate_init, migrate, upgrade

@click.command('refresh-user-info')
@with_appcontext
def refresh_user_info_command():
    """Refresh all user information in portfolio summaries."""
    from app import db
    from app.models.portfolio import PortfolioSummary
    
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
    from app.models.user import User
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
    
@click.command('dev-db-init')
@with_appcontext
def dev_db_init_command():
    """Initialize database migrations for development environment"""
    # Add a local import here to ensure it's available
    import os
    
    if os.environ.get('FLASK_ENV') != 'development':
        click.echo('Warning: This command should be run in development environment')
        return
    
    migrations_dev_dir = 'migrations_dev'
    
    # Check if directory already exists
    if os.path.exists(migrations_dev_dir):
        click.echo(f"Warning: {migrations_dev_dir} directory already exists")
        if not click.confirm('Do you want to continue? This may overwrite existing files'):
            click.echo('Operation cancelled')
            return
    
    from flask_migrate import init as _init
    click.echo("Initializing development migrations...")
    _init(directory=migrations_dev_dir)
    click.echo(f"Development migrations initialized in {migrations_dev_dir} directory")

@click.command('dev-db-migrate')
@click.option('--message', '-m', default=None, help='Migration message')
@with_appcontext
def dev_db_migrate_command(message):
    """Create database migration scripts for development environment"""
    if os.environ.get('FLASK_ENV') != 'development':
        click.echo('Warning: This command should be run in development environment')
        return
    
    from flask_migrate import migrate as _migrate
    click.echo(f"Creating development migration, message: {message}")
    _migrate(directory='migrations_dev', message=message)
    click.echo("Migration script created.")
    
@click.command('dev-db-upgrade')
@with_appcontext
def dev_db_upgrade_command():
    """Apply database migrations for development environment"""
    if os.environ.get('FLASK_ENV') != 'development':
        click.echo('Warning: This command should be run in development environment')
        return
    
    from flask_migrate import upgrade as _upgrade
    click.echo("Applying development migrations...")
    _upgrade(directory='migrations_dev')
    click.echo("Development database migrations applied.")

def init_app(app):
    """Register CLI commands and conditionally run setup logic."""
    app.cli.add_command(setup_dev_command)
    app.cli.add_command(refresh_user_info_command)
    app.cli.add_command(dev_db_init_command)
    app.cli.add_command(dev_db_migrate_command)
    app.cli.add_command(dev_db_upgrade_command)

    # Only run setup when launching dev server via `flask run`
    if (
        os.environ.get("FLASK_ENV") == "development"
        and "flask" in sys.argv[0]
        and "run" in sys.argv
    ):
        with app.app_context():
            setup_dev_environment()