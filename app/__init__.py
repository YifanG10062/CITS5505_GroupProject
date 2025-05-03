from flask import Flask, render_template, g, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from app.config import DeploymentConfig
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, CSRFError
from app.fetch_price import refresh_history_command

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

# =============================================================================
# TEMPORARY USER MOCK - TO BE REPLACED
# =============================================================================
# This class temporarily simulates a logged-in user until the proper user 
# authentication system is implemented. All references to this mock should be 
# removed when integrating with the real user module.
# =============================================================================
class MockUser:
    def __init__(self, is_authenticated=False):
        self.is_authenticated = is_authenticated
        self.id = 1 if is_authenticated else None
        self.username = "test_user" if is_authenticated else None

# =============================================================================
# END OF TEMPORARY USER MOCK
# =============================================================================

def create_app(config_class=DeploymentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Ensure SECRET_KEY is set for CSRF
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'temporary-secret-key'  # Only for development
        print("WARNING: Using temporary secret key")
    
    # TEMPORARY: Add test user to app context
    @app.before_request
    def inject_user():
        g.current_user = MockUser(is_authenticated=False)  # Set to True to simulate logged-in user
    
    # TEMPORARY: Make current_user available to templates
    @app.context_processor
    def inject_user_template():
        return {'current_user': getattr(g, 'current_user', MockUser())}
    
    # Register error handlers
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('error.html', 
                               code=400,
                               title="Security Error",
                               heading="Security Error",
                               subheading="Access Denied",
                               details="Your request could not be processed due to security concerns.",
                               reason=e.description), 400
    
    @app.errorhandler(404)
    def handle_not_found_error(e):
        return render_template('error.html',
                              code=404,
                              title="Page Not Found",
                              heading="Page Not Found",
                              subheading="The requested page does not exist",
                              details="The link you followed may be broken, or the page may have been removed."), 404
    
    @app.errorhandler(500)
    def handle_server_error(e):
        return render_template('error.html',
                              code=500,
                              title="Server Error",
                              heading="Server Error",
                              subheading="Something went wrong on our end",
                              details="Our technical team has been notified. Please try again later."), 500
    
    # Register blueprints
    from app.routes.main import main
    from app.routes.portfolio import portfolios
    from app.routes.user import user
    
    app.register_blueprint(main)
    app.register_blueprint(portfolios)
    app.register_blueprint(user)

    app.cli.add_command(refresh_history_command)

    from app.api import api_bp
    csrf.exempt(api_bp)
    app.register_blueprint(api_bp)

    return app
