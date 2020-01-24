from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from secrets import token_urlsafe
from datetime import datetime, timedelta
from bcrypt import hashpw, gensalt

db = SQLAlchemy()

TOKEN_VALID_TIME = timedelta(minutes=15)
TOKEN_LENGTH = 64

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(), index=True, unique=True)
    email = db.Column(db.String(), unique=True)
    password_hash = db.Column(db.String())

    posts = db.relationship('Post', backref='author', lazy=True)
    login_attempts = db.relationship('Login', backref='user', lazy=True)
    recovery_tokens = db.relationship('RecoveryToken', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = hashpw(password.encode(), gensalt()).decode()

    def __repr__(self):
        return f'{self.login}'

class RecoveryToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exp_date = db.Column(db.DateTime, default=(lambda: datetime.utcnow() + TOKEN_VALID_TIME))
    token = db.Column(db.String(), index=True, default=(lambda: token_urlsafe(TOKEN_LENGTH)))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    content = db.Column(db.String())
    public = db.Column(db.Boolean())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<title: {self.title} by {self.user_id}>'

class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    successful = db.Column(db.Boolean())
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip = db.Column(db.String())

def set_test_data():
    user1 = User(
        login='admin',
        email='admin@gmail.com',
    )
    user1.set_password('password')
    user2 = User(
        login='monika',
        email='monika@gmail.com'
    )
    user2.set_password('password')
    db.session.add(user1)
    db.session.add(user2)

    post1 = Post(
        title='Public post',
        content='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum pharetra.',
        author=user1,
        public=True
    )
    db.session.add(post1)

    post2 = Post(
        title='Private post',
        content='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum pharetra.',
        author=user1,
        public=False
    )
    db.session.add(post2)

    post3 = Post(
        title='Private post',
        content='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum pharetra.',
        author=user2,
        public=False
    )
    db.session.add(post3)

    db.session.commit()