from flask import Flask, make_response, render_template, session, request, flash, redirect, url_for
from flask_session import Session
from flask_login import current_user, login_user, logout_user
from bcrypt import hashpw, gensalt
from datetime import datetime, timedelta
from time import sleep

# <----- my imports ----->
from forms import RegisterForm, LoginForm
from config import Config
from models import db, set_test_data, User, Login
from login_manager import login_manager

app = Flask(__name__)
app.config.from_object(Config)
Session(app)

db.init_app(app)
with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.commit()
    set_test_data()
login_manager.init_app(app)

@app.route('/')  # main page
def index():
    return "Hello, World!"

# <------ LOGGING IN ----->

@app.route('/login', methods=['GET', 'POST'])  # login form
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm(meta={'crsf_context': session})
    user = User.query.filter_by(login=form.login.data).first()

    if user and form.password.data:  # login attempt
        ip = request.remote_addr
        login = Login(
            successful=form.validate(),
            ip=ip,
            user=user
        )
        db.session.add(login)
        db.session.commit()

        # slow down the brute force
        timestamp = datetime.utcnow() - timedelta(minutes=3)
        login_attempts = [a for a in user.login_attempts if a.timestamp > timestamp and not a.successful]
        count = len(login_attempts)
        sleep(get_delay(count))

    if form.validate_on_submit():
        login_user(user)

        next_page = session.get('next', None)
        if not next_page:
            next_page = url_for('index')
        session['next'] = None
        return redirect(next_page)

    return render_template('login.html', form=form)

@app.route('/logout')  #logout
def logout():
    logout_user()
    flash('You\'ve been logged out.')
    return redirect(url_for('index'))

# <----- CREATING NEW ACCOUNT ----->

@app.route('/new-account', methods=['GET', 'POST'])  # registration form
def new_account():
    
    form = RegisterForm(meta={'csrf_context': session})
    if form.validate_on_submit():
        flash('Your account has been created!', 'alert-success')

        login = form.login.data
        password = form.password.data
        email = form.email.data

        new_user = User(
            login=login,
            email=email
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return f'Hello {login}'

    return render_template('register.html', form=form)

# <----- supplementary functions ----->

def get_delay(count):
    if count < 4:
        return 0
    elif count < 10:
        return 1
    elif count < 50:
        return 3
    else:
        return 10

if __name__ == '__main__':
    app.run(debug=True)