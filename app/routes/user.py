from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

from app.forms.user import LoginForm, RegistrationForm, ResetRequestForm
from app.models.user import User
from app import db

# =============================================================================
# TEMPORARY USER AUTHENTICATION MODULE - TO BE REPLACED
# =============================================================================
# WARNING: This is a placeholder implementation that will be removed once 
# the proper user management module is implemented.
# It provides minimal routing to prevent template errors with current_user.
# =============================================================================
user = Blueprint("user", __name__, url_prefix="/user")

@user.route("/account")
def account():
    return render_template("error.html", 
                          code=501, 
                          title="Not Implemented",
                          heading="Feature Not Implemented", 
                          details="User account is not yet available.")
# =============================================================================
# END OF TEMPORARY USER AUTHENTICATION MODULE
# =============================================================================

@user.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.Email.data).first()
        if user and check_password_hash(user.user_pswd, form.Password.data):
            login_user(user)
            return redirect(url_for('portfolios.list'))
        flash("Invalid email or password.", "error")
    return render_template("user/login.html", form=form)  # Updated template path

@user.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(user_email=form.Email.data).first()
        if existing_user:
            flash("Email already registered.", "error")
        else:
            new_user = User(
                username=form.FirstName.data,  # Setting username to FirstName
                user_fName=form.FirstName.data,
                user_lName=form.LastName.data,
                user_email=form.Email.data,
                user_pswd=generate_password_hash(form.Password.data)
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("user.login"))
    return render_template("user/register.html", form=form)  # Updated template path

@user.route("/resetrequest", methods=["GET", "POST"])
def resetrequest():
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.Email.data).first()
        if user:
            flash("Reset link would be sent to your email (not implemented).", "success")
            return redirect(url_for("user.login"))
        else:
            flash("Email not found.", "error")
    return render_template("user/resetrequest.html", form=form)  # Updated template path

@user.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    # Add password change functionality here when needed
    return render_template("user/changepassword.html")  # Updated template path

@user.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("user.login"))

# Added from __init__.py - Root route
@user.route("/")
def index():
    return redirect(url_for('user.login'))