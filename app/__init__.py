import uuid

from flask import (Blueprint, Flask, Response, flash, g, redirect,
                   render_template, request, url_for)
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFError, CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import Email, InputRequired, Length, ValidationError

from app.config import DeploymentConfig
from app.fetch_price import refresh_history_command

#from app.routes.portfolio import list

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

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'


    #Email Configuration
    mail = Mail(app)
    app.config['MAIL_SERVER']= "smtp.gmail.com"# "live.smtp.mailtrap.io"
    app.config['MAIL_PORT'] = 465 #587
    app.config['MAIL_USERNAME'] = "pythonuserflask@gmail.com"
    app.config['MAIL_PASSWORD'] =  "lwtq mygm ksuc tbpm"
    #app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = True
    mail = Mail(app)


    class Users(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        user_fName = db.Column(db.String(200), nullable=False)
        user_lName = db.Column(db.String(200), nullable=False)
        user_email = db.Column(db.String(200), nullable=False, unique =True)
        user_pswd = db.Column(db.String(200), nullable=False)
        user_token = db.Column(db.String(1000), nullable=True)

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    class FooException(Exception):
        """ Binds optional status code and encapsulates returing Response when error is caught """
        def __init__(self, *args, **kwargs):
            code = kwargs.pop('code', 400)
            Exception.__init__(self)
            self.code = code

        def as_http_error(self):
            return Response(str(self), self.code)

    class LoginForm(FlaskForm):
        Email = StringField(validators=[InputRequired(), Email(message ='Please enter valid email address.'), Length(min=4, max=200)], render_kw={"placeholder": "Email"})
        Password = PasswordField(validators=[InputRequired(), Length(min=4, max=200)], render_kw={"placeholder": "Password"})

    class RegistrationForm(FlaskForm):
        FirstName = StringField(validators=[InputRequired(), Length(min=4, max=200)], render_kw={"placeholder": "First Name"})
        LastName = StringField(validators=[InputRequired(), Length(min=4, max=200)], render_kw={"placeholder": "Last Name"})
        Email = StringField(validators=[InputRequired(), Length(min=4, max=200), Email("This field requires a valid email address")], render_kw={"placeholder": "Email"})
        Password = PasswordField(validators=[InputRequired(), Length(min=4, max=200)], render_kw={"placeholder": "Password"})

    class ResetRequestForm(FlaskForm):
        Email = StringField(validators=[InputRequired(), Length(min=4, max=200), Email("Please enter valid email address.")], render_kw={"placeholder": "Email"})
        UserToken = StringField(render_kw={"placeholder": "UserToken"})
        Password = PasswordField(render_kw={"placeholder": "Password"})
        ConfirmPassword = PasswordField(render_kw={"placeholder": "ConfirmPassword"})

    class ChangePasswordForm(FlaskForm):
        Email = StringField(validators=[InputRequired(), Length(min=4, max=200), Email("Please enter valid email address.")], render_kw={"placeholder": "Email"})
        Password = PasswordField(validators=[InputRequired(), Length(min=4, max=200)], render_kw={"placeholder": "Password"})
        ConfirmPassword = PasswordField(validators=[InputRequired(), Length(min=4, max=200)], render_kw={"placeholder": "ConfirmPassword"})
        UserToken = StringField(validators=[InputRequired()], render_kw={"placeholder": "UserToken"})

          
    app.app_context().push()
    db.create_all()



    @app.route("/")    
    @app.route('/login', methods = ['GET', 'POST'])
    def login():
        try:
            form = LoginForm()
            if form.validate_on_submit():
                user = Users.query.filter_by(user_email = form.Email.data).first()
                if user:
                    #session['user_name'] = User['user_fName'] + ' ' + User['user_lName']
                    #if user.user_pswd == form.Password.data:
                    if check_password_hash(user.user_pswd, form.Password.data):
                        login_user(user, remember='')
                        #return redirect(url_for('home'))
                        #return render_template ('home.html', legend=user.user_fName + ' ' + user.user_lName)
                        return redirect(url_for('portfolios.list'))
                    else: 
                        flash("Password does not match, please re-enter again.", "error")         
                else:
                    flash("User not found. Please register to gain access.", "error")
            return render_template ('login.html', form=form)
        except Exception as e:
            flash(str(e), "error")     

    @app.route('/register', methods = ['GET', 'POST'])
    def register():
        try:
            form = RegistrationForm()

            if form.validate_on_submit():        
                existing_useremail = Users.query.filter_by(user_email = form.Email.data).first()
                hashed_password = generate_password_hash(form.Password.data, method='pbkdf2:sha256')

                if existing_useremail:
                    if existing_useremail.user_email != form.Email.data:                
                        new_user = Users(user_fName = form.FirstName.data, user_lName = form.LastName.data, user_email = form.Email.data, user_pswd = hashed_password)
                        db.session.add(new_user)
                        db.session.commit()
                    else: 
                        flash("User with email " + form.Email.data + " already exists. Please choose a different email.", "error")
                else:
                    if existing_useremail is None:
                        new_user = Users(user_fName = form.FirstName.data, user_lName = form.LastName.data, user_email = form.Email.data, user_pswd = hashed_password)
                        db.session.add(new_user)
                        db.session.commit()
                        flash ("New User " + form.FirstName.data + " " + form.LastName.data + " created Successfully", "success")
                        return render_template ('login.html', form=form)
                
            return render_template ('register.html', form=form)
        except Exception as e:
            flash(str(e), "error")


    @app.route('/home', methods = ['GET', 'POST'])
    @login_required
    def home():
        try:
            allusers = Users.query.all()
            print (allusers)
            return render_template ('home.html', users = allusers)
        except Exception as e:
            flash(str(e), "error")

    @app.route('/update', methods = ['GET', 'POST'])
    def update():
        try:
            if request.method == 'POST':
                my_data = Users.query.get(request.form.get('id'))
                
                my_data.user_fName = request.form['firstname']
                my_data.user_lName = request.form['lastname']
                my_data.user_email = request.form['email']

                db.session.commit()
                flash("User updated successfully", "success")

            return redirect(url_for('home'))
        except Exception as e:
            flash(str(e), "error")


    @app.route('/delete/<id>/', methods = ['GET', 'POST'])
    def delete(id):    
        try:
            my_data = Users.query.get(id)
            db.session.delete(my_data)
            db.session.commit()
            flash("User deleted successfully", "success")   
            return redirect(url_for('home'))
        except Exception as e:
            flash(str(e), "error")

    @app.route('/email/<emailID>/', methods = ['GET', 'POST'])
    def email(emailID):
        try:
            message = Message(
                                subject = 'Hello', 
                                sender =   'pythonuserflask@gmail.com', 
                                recipients = [emailID]
                                )
            
            message.body = "This is a test to " + emailID
            mail.send(message)
            flash("Email sent successfully.", 'success')
            return redirect(url_for('home')) 
        except Exception as e:
            flash(str(e), "error")           

    @app.route('/upload', methods = ['GET', 'POST'])
    def upload():
        try:

            if request.method == 'POST':
                file = request.files['file']
                upload = Upload(eventid='0', filename=file.filename, file = file.read())
                db.session.add(upload)
                db.session.commit()
                flash("File uploaded successfully", "success")
                #return f'Uploaded: {file.filename}'
            return render_template ('Upload.html')
        except Exception as e:
            flash(str(e), "error")

    @app.route('/resetrequest', methods = ['GET', 'POST'])
    def resetrequest():
        try:
            form = ResetRequestForm()

            if form.validate_on_submit():  
                user = Users.query.filter_by(user_email=form.Email.data).first()
                if user:
                    x = uuid.uuid1()
                    uid = (uuid.uuid5(x,form.Email.data))
                    _sendEmail = sendemail(user.id, user.user_email, str(uid))
                    if _sendEmail == '1':

                        flash("Thank you for providing your email address. We'll send you a verification code shortly.", "success")
                        return render_template ('changepassword.html', form=form)
                else:
                    flash("User email not found in the system","error")
                        
            return render_template ('resetrequest.html', form=form)
        except Exception as e:
            flash(str(e), "error")

    @app.route('/changepassword', methods = ['GET', 'POST'])
    def changepassword():
        try:
            form = ChangePasswordForm()

            if form.validate_on_submit(): 
                user = Users.query.filter_by(user_email=form.Email.data).first()
                if user.user_token == form.UserToken.data:
                    if form.Password.data == form.ConfirmPassword.data:
                        
                        hashed_password = generate_password_hash(form.Password.data, method='pbkdf2:sha256')
                        user.user_pswd = hashed_password
                        user.user_token = None
                        db.session.commit()

                        flash("Password has been reset successfully.", "success")
                        return render_template ('login.html', form=form)
                    else:
                        flash("Passwords do not match.", "error")
                else:   
                    flash("Invalid Token, please re-enter.", "error")                
            return render_template ('changepassword.html', form=form)
        except Exception as e:
            flash(str(e), "error")
        
    def sendemail(userid, email, uid):
        try:
            user = Users.query.filter_by(id=userid).first()
            message = Message(
                            subject = 'Password Reset Token', 
                            sender =   'pythonuserflask@gmail.com',#'mailtrap@demomailtrap.com', 
                            recipients = [email]
                            )
            message.body = "<table cellpadding='0' cellspacing='0' width='100%' bgcolor='#fafafa' style='background-color: #fafafa; border-radius: 10px; border-collapse: separate;font-size:18px; color:grey; font-family:calibri'><tbody class='ui-droppable'><tr class='ui-draggable'><td align='left' class='esd-block-text es-p20 esd-frame esd-hover esd-draggable esd-block esdev-enable-select' esd-handler-name='textElementHandler'><div class='esd-block-btn esd-no-block-library'><div class='esd-more'><a><span class='es-icon-dot-3'></span></a></div><div class='esd-move ui-draggable-handle' title='Move'><a><span class='es-icon-move'></span></a></div><div class='esd-copy ui-draggable-handle' title='Copy'><a><span class='es-icon-copy'></span></a></div><div class='esd-delete' title='Delete'><a><span class='es-icon-delete'></span></a></div></div><h3>Welcome &nbsp;" + user.user_fName + " " + user.user_lName +",</h3><p><br></p><p style=''>You're receiving this message because you recently reset your password&nbsp;for a account.<br><br>Please copy the below token and confirm your email address for resetting your password. This step adds extra security to your business by verifying the token and email.</p>    <br></td></tr><tr><td>This is your password reset token:<br></td></tr><tr><td><b>"+ uid + "</b></td></tr></tbody></table>"    
            message.html = message.body
            mail.send(message)

            my_data = Users.query.get(userid)        
            my_data.user_token = uid
            db.session.commit()
            return '1'
        
        except Exception as e:
            flash(str(e), "error") 
        
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash ("Logged Out Successfully", "success")
        return redirect('/')
    
    return app
