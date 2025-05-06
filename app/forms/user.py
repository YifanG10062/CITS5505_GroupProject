from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length

class LoginForm(FlaskForm):
    Email = StringField(validators=[InputRequired(), Email(), Length(min=4, max=200)],
                        render_kw={"placeholder": "Email"})
    Password = PasswordField(validators=[InputRequired(), Length(min=4, max=200)],
                             render_kw={"placeholder": "Password"})

class RegistrationForm(FlaskForm):
    FirstName = StringField(validators=[InputRequired(), Length(min=2, max=200)],
                            render_kw={"placeholder": "First Name"})
    LastName = StringField(validators=[InputRequired(), Length(min=2, max=200)],
                           render_kw={"placeholder": "Last Name"})
    Email = StringField(validators=[InputRequired(), Email(), Length(min=4, max=200)],
                        render_kw={"placeholder": "Email"})
    Password = PasswordField(validators=[InputRequired(), Length(min=4, max=200)],
                             render_kw={"placeholder": "Password"})

class ResetRequestForm(FlaskForm):
    Email = StringField(validators=[InputRequired(), Email(), Length(min=4, max=200)],
                        render_kw={"placeholder": "Email"})
