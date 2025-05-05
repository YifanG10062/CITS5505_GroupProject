import uuid

from flask import Flask, render_template, redirect, url_for, flash, g, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from flask_mail import Mail
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect, CSRFError
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash

from app.config import DeploymentConfig
from app.fetch_price import refresh_history_command

# --- Extensions ---
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()
login_manager = LoginManager()

# --- Optional Mock User (for dev mode) ---
class MockUser:
    def __init__(self, is_authenticated=False):
        self.is_authenticated = is_authenticated
        self.id = 1 if is_authenticated else None
        self.username = "test_user" if is_authenticated else None

# --- Flask App Factory ---
def create_app(config_class=DeploymentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Import models
    from app import models
    from app.models.user import User  

    # Secret key fallback
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'temporary-secret-key'
        print("WARNING: Using temporary secret key")

    # CLI command
    app.cli.add_command(refresh_history_command)

    # Register blueprints
    from app.routes.main import main
    from app.routes.portfolio import portfolios
    from app.routes.user import user
    from app.routes.comparison import comparison
    from app.api import api_bp

    app.register_blueprint(main)
    app.register_blueprint(portfolios)
    app.register_blueprint(user)
    app.register_blueprint(comparison)
    csrf.exempt(api_bp)
    app.register_blueprint(api_bp)

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
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

    # Optional: mock user for dev
    @app.before_request
    def inject_user():
        g.current_user = MockUser(is_authenticated=False)

    @app.context_processor
    def inject_user_template():
        return {'current_user': getattr(g, 'current_user', MockUser())}

    # --- Auth Forms ---
    class LoginForm(FlaskForm):
        Email = StringField(validators=[InputRequired(), Email(), Length(min=4, max=200)],
                            render_kw={"placeholder": "Email"})
        Password = PasswordField(validators=[InputRequired(), Length(min=4, max=200)],
                                 render_kw={"placeholder": "Password"})

    class RegistrationForm(FlaskForm):
        FirstName = StringField(validators=[InputRequired(), Length(min=4, max=200)],
                                render_kw={"placeholder": "First Name"})
        LastName = StringField(validators=[InputRequired(), Length(min=4, max=200)],
                               render_kw={"placeholder": "Last Name"})
        Email = StringField(validators=[InputRequired(), Email(), Length(min=4, max=200)],
                            render_kw={"placeholder": "Email"})
        Password = PasswordField(validators=[InputRequired(), Length(min=4, max=200)],
                                 render_kw={"placeholder": "Password"})

    class ResetRequestForm(FlaskForm):
        Email = StringField(validators=[InputRequired(), Email(), Length(min=4, max=200)],
                            render_kw={"placeholder": "Email"})

    # --- Routes ---
    @app.route("/")
    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(user_email=form.Email.data).first()
            if user and check_password_hash(user.user_pswd, form.Password.data):
                login_user(user)
                return redirect(url_for('portfolios.list'))
            flash("Invalid email or password.", "error")
        return render_template("login.html", form=form)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            existing_user = User.query.filter_by(user_email=form.Email.data).first()
            if existing_user:
                flash("Email already registered.", "error")
            else:
                new_user = User(
                    user_fName=form.FirstName.data,
                    user_lName=form.LastName.data,
                    user_email=form.Email.data,
                    user_pswd=generate_password_hash(form.Password.data)
                )
                db.session.add(new_user)
                db.session.commit()
                flash("Registration successful. Please log in.", "success")
                return redirect(url_for("login"))
        return render_template("register.html", form=form)

    @app.route("/resetrequest", methods=["GET", "POST"])
    def resetrequest():
        form = ResetRequestForm()
        if form.validate_on_submit():
            user = User.query.filter_by(user_email=form.Email.data).first()
            if user:
                flash("Reset link would be sent to your email (not implemented).", "success")
                return redirect(url_for("login"))
            else:
                flash("Email not found.", "error")
        return render_template("resetrequest.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Logged out successfully.", "success")
        return redirect("/")

    return app
