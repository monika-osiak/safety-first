from flask import current_app
from wtforms import ValidationError

# <----- my imports ----->
from .models import User
from .password_manager import hash_password, verify_password

class UniqueLogin(object):
    def __init__(self, message=None):
        if not message:
            message = 'This login is taken!'
        self.message = message

    def __call__(self, form, field):
        login = field.data
        with current_app.app_context():
            result = User.query.filter(User.login == login).first()
            if result is not None:
                raise ValidationError(self.message)

class UniqueEmail(object):
    def __init__(self, message=None):
        if not message:
            message = 'E-mail already in the database!'
        self.message = message

    def __call__(self, form, field):
        email = field.data
        with current_app.app_context():
            result = User.query.filter(User.email == email).first()
            if result is not None:
                raise ValidationError(self.message)

class CorrectLogin(object):
    def __init__(self, message=None):
        if not message:
            message = 'User does not exist.'
        self.message = message

    def __call__(self, form, field):
        login = field.data
        with current_app.app_context():
            result = User.query.filter(User.login == login).first()
            if result is None:
                raise ValidationError(self.message)

class CorrectPassword(object):
    def __init__(self, message=None):
        if not message:
            message = 'Wrong password!'
        self.message = message

    def __call__(self, form, field):
        login = form.login.data
        password = field.data
        with current_app.app_context():
            user = User.query.filter(User.login == login).first()
            if user is None:
                return
            if not verify_password(user.password_hash, password):
                raise ValidationError(self.message)