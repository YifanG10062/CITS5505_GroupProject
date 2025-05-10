# Standard library imports
import uuid

# Third-party imports
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, CSRFError

# Local application imports
from app.config import ProductionConfig

# --- Extensions ---
db = SQLAlchemy()  # Create db instance first
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()
login_manager = LoginManager()

# --- Flask App Factory ---
def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)  # Initialize db with app
    migrate.init_app(app, db)
    csrf.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'  # Updated to use blueprint route

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
