import uuid
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate, upgrade
from flask_wtf.csrf import CSRFProtect, CSRFError
from app.config import get_config, DevelopmentConfig, TestConfig, ProductionConfig

# --- Extensions ---
db = SQLAlchemy() 
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()
login_manager = LoginManager()

# --- Flask App Factory ---
def create_app(config_class=None):
    # Use the get_config() function that handles both APP_ENV and FLASK_DEBUG
    config_obj = config_class or get_config()
    
    app = Flask(__name__)
    app.config.from_object(config_obj)

    # Determine environment name from the config class for migrations
    if isinstance(config_class, DevelopmentConfig):
        config_name = 'development'
    elif isinstance(config_class, TestConfig):
        config_name = 'testing'
    else:
        config_name = 'production'
    
    # Initialize extensions
    db.init_app(app)  
    
    # Choose migrations directory based on environment name rather than just DEBUG flag
    migrations_directory = 'migrations_dev' if config_name == 'development' else 'migrations'
    migrate.init_app(app, db, directory=migrations_directory)
    
    csrf.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'user.login' 

    # Suppress the default "Please log in to access this page." message
    login_manager.login_message = None

    # Secret key fallback
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'temporary-secret-key'
        print("WARNING: Using temporary secret key")

    # CLI commands
    from app.services.fetch_price import refresh_history_command
    app.cli.add_command(refresh_history_command)
    
    # Register custom commands
    with app.app_context():
        from app.cli.commands import init_app as init_commands
        init_commands(app)
    
    # Register blueprints
    from app.routes.main import main
    from app.routes.portfolio import portfolios
    from app.routes.user import user
    from app.routes.comparison import comparison
    from app.services.api import api_bp
    from app.routes.dashboard import dashboard

    app.register_blueprint(main)
    app.register_blueprint(portfolios)
    app.register_blueprint(user)
    app.register_blueprint(comparison)
    csrf.exempt(api_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(dashboard)

    import sys
    from datetime import date, timedelta
    from sqlalchemy import func
    from app.models import Price
    from app.services.fetch_price import fetch_all_history

    # Check if the app is running in CLI mode
    # and if the command is "run"
    cmd = os.environ.get("FLASK_CLI_COMMAND") or (sys.argv[1] if len(sys.argv) > 1 else "")
    if cmd == "run":

        # Check if the database is up-to-date
        with app.app_context():
            last_date = db.session.query(func.max(Price.date)).scalar()
            yesterday = date.today() - timedelta(days=1)

            if last_date and last_date >= yesterday:
                app.logger.info(f"✅ Price data is up-to-date (latest date: {last_date})")
            else:
                if last_date:
                    app.logger.warning(f"⚠️ Price data is outdated (latest date: {last_date}), fetching new data…")
                else:
                    app.logger.warning("⚠️ No price data found in database, fetching all history…")

                fetch_all_history()

                app.logger.info("✅ Historical price data fetched and saved successfully.")

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # CSRF error handler
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('error.html', code=400, title="Security Error",
                               heading="Security Error", subheading="Access Denied",
                               details="Your request could not be processed due to security concerns.",
                               reason=e.description), 400

    @app.errorhandler(404)
    def handle_404(e):
        return render_template('error.html', code=404, title="Page Not Found",
                               heading="Page Not Found", subheading="This page doesn't exist.",
                               details="Check the URL or go back to home."), 404

    @app.errorhandler(500)
    def handle_500(e):
        return render_template('error.html', code=500, title="Server Error",
                               heading="Something went wrong", subheading="Internal Server Error",
                               details="Try again later or contact support."), 500

    return app
