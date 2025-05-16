from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
import uuid
from flask_mail import Message

from app.forms.user import LoginForm, RegistrationForm, ResetRequestForm, ChangePasswordForm
from app.models.user import User
from app import db, mail

user = Blueprint("user", __name__, url_prefix="/user")

@user.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.Email.data).first()
        if user and check_password_hash(user.user_pswd, form.Password.data):
            login_user(user)
            return redirect(url_for('portfolios.list'))
        flash("Invalid email or password.", "error")
    return render_template("user/login.html", form=form, hide_footer=True)

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
            
            # Automatically log in the new user
            login_user(new_user)
            flash("Registration successful. Welcome to The Richverse.", "success")
            return redirect(url_for("portfolios.create"))
            
    return render_template("user/register.html", form=form, hide_footer=True)

@user.route("/resetrequest", methods=["GET", "POST"])
def resetrequest():
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.Email.data).first()
        if user:
            # generate token but not send email
            reset_token = uuid.uuid4().hex
            user.user_token = reset_token
            db.session.commit()
            
            # show maintenance message instead of sending email
            flash("The password reset function is currently being upgraded. Please try again later.", "success")
            return render_template("user/resetrequest.html", form=form, hide_footer=True)
        else:
            flash("Email not found.", "error")
    return render_template("user/resetrequest.html", form=form, hide_footer=True)

@user.route("/changepassword", methods=["GET", "POST"])
def changepassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.Email.data).first()
        if user:
            # System maintenance message
            flash("The password reset function is currently being upgraded. Please try again later.", "success")
            return render_template("user/changepassword.html", form=form, hide_footer=True)
        else:
            flash("Email not found or invalid token.", "error")
    return render_template("user/changepassword.html", form=form, hide_footer=True)

@user.route("/update", methods=["POST"])
@login_required
def update():
    try:
        my_data = User.query.get(request.form.get('id'))
        my_data.user_fName = request.form['firstname']
        my_data.user_lName = request.form['lastname']
        my_data.user_email = request.form['email']
        db.session.commit()
        flash("User updated successfully", "success")
        return redirect(url_for('user.account'))
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for('user.account'))

@user.route("/delete/<id>/", methods=["GET", "POST"])
@login_required
def delete(id):
    try:
        my_data = User.query.get(id)
        db.session.delete(my_data)
        db.session.commit()
        flash("User deleted successfully", "success")
        return redirect(url_for('user.account'))
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for('user.account'))

@user.route("/email/<emailID>/", methods=["GET", "POST"])
def email(emailID):
    try:
        flash("Email function is currently unavailable.", "success")
        return redirect(url_for('user.account'))
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for('user.account'))

@user.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("user.login"))

# Added from __init__.py - Root route
@user.route("/")
def index():
    return redirect(url_for('user.login'))

def sendemail(userid, email, uid):
    try:
        user = User.query.filter_by(id=userid).first()
        user.user_token = uid
        db.session.commit()
        return '1'
    except Exception as e:
        flash(str(e), "error")
        return '0'