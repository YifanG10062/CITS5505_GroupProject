from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length, ValidationError

class LoginForm(FlaskForm):
    Email = StringField(validators=[InputRequired(), Email(message='Please enter valid email address.'), Length(min=1, max=200)], render_kw={"placeholder": "Email"})
    Password = PasswordField(validators=[InputRequired(), Length(min=1, max=200)], render_kw={"placeholder": "Password"})

class RegistrationForm(FlaskForm):
    FirstName = StringField(validators=[InputRequired(), Length(min=1, max=200)], render_kw={"placeholder": "First Name"})
    LastName = StringField(validators=[InputRequired(), Length(min=1, max=200)], render_kw={"placeholder": "Last Name"})
    Email = StringField(validators=[InputRequired(), Length(min=1, max=200), Email("This field requires a valid email address")], render_kw={"placeholder": "Email"})
    Password = PasswordField(validators=[InputRequired(), Length(min=1, max=200)], render_kw={"placeholder": "Password"})

class ResetRequestForm(FlaskForm):
    Email = StringField(validators=[InputRequired(), Length(min=1, max=200), Email("Please enter valid email address.")], render_kw={"placeholder": "Email"})
    UserToken = StringField(render_kw={"placeholder": "UserToken"})
    Password = PasswordField(render_kw={"placeholder": "Password"})
    ConfirmPassword = PasswordField(render_kw={"placeholder": "ConfirmPassword"})

class ChangePasswordForm(FlaskForm):
    Email = StringField(validators=[InputRequired(), Length(min=1, max=200), Email("Please enter valid email address.")], render_kw={"placeholder": "Email"})
    Password = PasswordField(validators=[InputRequired(), Length(min=1, max=200)], render_kw={"placeholder": "Password"})
    ConfirmPassword = PasswordField(validators=[InputRequired(), Length(min=1, max=200)], render_kw={"placeholder": "ConfirmPassword"})
    UserToken = StringField(validators=[InputRequired()], render_kw={"placeholder": "UserToken"})
