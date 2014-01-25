from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from wtforms import form, fields, validators

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(64))

    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username

    def save(self):
        db.session.add(self)
        db.session.commit()
        

class LoginForm(form.Form):
    email = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_email(self, field):
        user = self.get_user()
        if user is None:
            raise validators.ValidationError('Invalid user')
        if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(email=self.email.data).first()

class RegistrationForm(form.Form):
    email = fields.TextField(validators=[validators.required(),
                                         validators.Email(message="Invalid email address...")])
    password = fields.PasswordField(validators=[validators.required(),
                                    validators.EqualTo('confirm', message='Passwords must match')])
    confirm = fields.PasswordField('Repeat Password')

    def validate_email(self, field):
        if db.session.query(User).filter_by(email=self.email.data).count() > 0:
            raise validators.ValidationError('Duplicate email')

def init_login(app):
    login_manager = LoginManager()
    login_manager.session_protection = "strong"
    login_manager.init_app(app)
    

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)
