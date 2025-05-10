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
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("user.login"))
    return render_template("user/register.html", form=form, hide_footer=True)

@user.route("/resetrequest", methods=["GET", "POST"])
def resetrequest():
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.Email.data).first()
        if user:
            x = uuid.uuid1()
            uid = str(uuid.uuid5(x, form.Email.data))
            _sendEmail = sendemail(user.id, user.user_email, uid)
            if _sendEmail == '1':
                flash("Thank you for providing your email address. We'll send you a verification code shortly.", "success")
                return render_template('user/changepassword.html', form=ChangePasswordForm(), hide_footer=True)
        else:
            flash("Email not found.", "error")
    return render_template("user/resetrequest.html", form=form, hide_footer=True)

@user.route("/changepassword", methods=["GET", "POST"])
def changepassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.Email.data).first()
        if user and user.user_token == form.UserToken.data:
            if form.Password.data == form.ConfirmPassword.data:
                hashed_password = generate_password_hash(form.Password.data)
                user.user_pswd = hashed_password
                user.user_token = None
                db.session.commit()
                flash("Password has been reset successfully.", "success")
                return redirect(url_for('user.login'))
            else:
                flash("Passwords do not match.", "error")
        else:
            flash("Invalid Token, please re-enter.", "error")
    return render_template("user/changepassword.html", form=form, hide_footer=True)  # Updated template path

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
        message = Message(
            subject='Hello',
            sender='pythonuserflask@gmail.com',
            recipients=[emailID]
        )
        message.body = "This is a test to " + emailID
        mail.send(message)
        flash("Email sent successfully.", 'success')
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
        message = Message(
            subject='Password Reset Token',
            sender='pythonuserflask@gmail.com',
            recipients=[email]
        )
        message.body = "<table cellpadding='0' cellspacing='0' width='100%' bgcolor='#fafafa' style='background-color: #fafafa; border-radius: 10px; border-collapse: separate;font-size:18px; color:grey; font-family:calibri'><tbody class='ui-droppable'><tr class='ui-draggable'><td align='left' class='esd-block-text es-p20 esd-frame esd-hover esd-draggable esd-block esdev-enable-select' esd-handler-name='textElementHandler'><div class='esd-block-btn esd-no-block-library'><div class='esd-more'><a><span class='es-icon-dot-3'></span></a></div><div class='esd-move ui-draggable-handle' title='Move'><a><span class='es-icon-move'></span></a></div><div class='esd-copy ui-draggable-handle' title='Copy'><a><span class='es-icon-copy'></span></a></div><div class='esd-delete' title='Delete'><a><span class='es-icon-delete'></span></a></div></div><h3>Welcome &nbsp;" + user.user_fName + " " + user.user_lName +",</h3><p><br></p><p style=''>You're receiving this message because you recently reset your password&nbsp;for a account.<br><br>Please copy the below token and confirm your email address for resetting your password. This step adds extra security to your business by verifying the token and email.</p>    <br></td></tr><tr><td>This is your password reset token:<br></td></tr><tr><td><b>"+ uid + "</b></td></tr></tbody></table>"
        message.html = message.body
        mail.send(message)

        user.user_token = uid
        db.session.commit()
        return '1'
    except Exception as e:
        flash(str(e), "error")
        return '0'