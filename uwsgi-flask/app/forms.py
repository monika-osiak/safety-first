from flask_wtf.form import FlaskForm
from wtforms import StringField, PasswordField, ValidationError, Form, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp
from wtforms.csrf.session import SessionCSRF
from datetime import timedelta

# <----- my imports ----->
from .config import Config
from .validators import UniqueLogin, UniqueEmail, CorrectLogin, CorrectPassword

class BaseForm(FlaskForm):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = Config.SECRET_KEY.encode()
        csrf_time_limit = timedelta(minutes=20)

class RegisterForm(BaseForm):
    login = StringField('login', validators=[
        DataRequired('Login required!'),
        Length(min=6, message='Login needs to have at least 6 characters!'),
        Regexp('^[a-z0-9_-]*$',
               message='Only small letters, digits, a dash and an underscore allowed!'),
        UniqueLogin()
    ])

    password = PasswordField('password', validators=[
        DataRequired('Password required!'),
        Length(min=8, message='Password needs to have at least 8 characters!')
        # todo: add regexp to check if a) at least one digit and b) at least one special character and c) etc.
    ])

    confirm_password = PasswordField('confirm_password', validators=[
        EqualTo('password', 'Passwords are different!')
    ])

    email = StringField('email', validators=[
        DataRequired('E-mail required!'),
        Email('This is not valid e-mail address!'),
        UniqueEmail()
    ])

class LoginForm(BaseForm):
    login = StringField('login', validators=[
        DataRequired('Login required!'),
        CorrectLogin()
    ])

    password = StringField('password', validators=[
        DataRequired('Password required!'),
        CorrectPassword()
    ])

class ChangePasswordForm(BaseForm):
    login = StringField('login', validators=[
        DataRequired('Login required!'),
        CorrectLogin()
    ])

    password = PasswordField('password', validators=[
        DataRequired('Current password required!'),
        CorrectPassword()
    ])

    new_password = PasswordField('new_password', validators=[
        DataRequired('New password required!'),
        Length(min=8, message='Password needs to have at least 8 characters!')
        # todo: add regexp to check if a) at least one digit and b) at least one special character and c) etc.
    ])
    
    confirm_new_password = PasswordField('confirm_new_password', validators=[
        EqualTo('new_password', 'Passwords are different!')
    ])

class CreatePostForm(BaseForm):
    title = StringField(validators=[
        DataRequired('Title required!'),
        Length(max=50, message='Title cannot be longer that 50 characters!')
    ])

    content = TextAreaField()
    public = BooleanField()

class RecoverPasswordForm(BaseForm):
    login = StringField('login', validators=[
        DataRequired('Login required!'),
        CorrectLogin()
    ])

class ResetPasswordForm(BaseForm):
    password = PasswordField('password', validators=[
        DataRequired('New password required!'),
        Length(min=8, message='Password needs to have at least 8 characters!')
        # todo: add regexp to check if a) at least one digit and b) at least one special character and c) etc.
    ])
    confirm_password = PasswordField('confirm_password', validators=[
        EqualTo('password', 'Passwords are different!')
    ])