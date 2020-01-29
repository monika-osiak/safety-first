from flask import Flask, make_response, render_template, session, request, flash, redirect, url_for, abort
from flask_session import Session
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime, timedelta
from time import sleep
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlsplit, urlunsplit

import smtplib
import ssl

# <----- my imports ----->
from .forms import RegisterForm, LoginForm, ChangePasswordForm, CreatePostForm, RecoverPasswordForm, ResetPasswordForm
from .config import Config
from .models import db, set_test_data, User, Login, Post, RecoveryToken
from .login_manager import login_manager

# <----- config code ----->
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
    return render_template('index.html', user=current_user)

# <------ LOGGING IN ----->

@app.route('/login', methods=['GET', 'POST'])  # login form
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'), user=current_user)

    form = LoginForm(meta={'crsf_context': session})
    user = User.query.filter_by(login=form.login.data).first()

    if user and form.password.data:  # oh, a login attempt!
        ip = request.remote_addr
        new_login_attempt = Login(
            successful=form.validate(),
            ip=ip,
            user=user
        )
        db.session.add(new_login_attempt)
        db.session.commit()

        # add timestamp to slow down the brute force, let's say 3 minutes
        timestamp = datetime.utcnow() - timedelta(minutes=3)
        login_attempts = [a for a in user.login_attempts if a.timestamp > timestamp and not a.successful]
        count = len(login_attempts)
        sleep(get_delay(count))

    if form.validate_on_submit():
        login_user(user)

        next_page = session.get('next', None)
        if not next_page:
            next_page = url_for('get_posts', id=current_user.id)
        session['next'] = None
        return redirect(next_page)

    return render_template('login.html', form=form)

@app.route('/logout')  #logout
def logout():
    logout_user()
    return redirect(url_for('index'))

# <----- CREATING NEW ACCOUNT ----->

@app.route('/new-account', methods=['GET', 'POST'])  # registration form
def new_account():
    form = RegisterForm(meta={'csrf_context': session})

    if form.validate_on_submit():
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

        login_user(new_user)

        return redirect(url_for('get_posts', id=current_user.id))

    return render_template('register.html', form=form)

# <----- MANAGING AN ACCOUNT ----->

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(meta={'csrf_context': session})
    form.login.data = current_user.login

    if form.validate_on_submit():
        new_password = form.new_password.data
        current_id = current_user.id
        user = User.query.filter_by(id=current_id).first()
        user.set_password(new_password)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('change-password.html', form=form, user=current_user)

@app.route('/recover-password', methods=['GET', 'POST'])
def recover_password():
    form = RecoverPasswordForm(meta={'csrf_context': session})

    if form.validate_on_submit():
        login = form.login.data
        user = User.query.filter_by(login=login).first()
        email = user.email
        recovery_token = RecoveryToken(user=user)
        db.session.add(recovery_token)
        db.session.commit()

        app_url_parts = urlsplit(request.base_url)
        url_path = url_for('validate_password_token')
        url_query = f'user={login}&token={recovery_token.token}'
        recovery_link = urlunsplit((app_url_parts.scheme, app_url_parts.netloc, url_path, url_query, ''))

        topic = 'Recover password'
        message = f'You can reset your password here: {recovery_link}'
        send_email(email, topic, message)

        info = "Check your e-mail address. We sent you a message so you can recover your password."
        return render_template('info.html', message=info)

    return render_template('recover-password.html', form=form)

@app.route('/validate-password-token')
def validate_password_token():
    token = request.args.get('token', None)
    login = request.args.get('user', None)

    if not token or not login: # if something is missing
        abort(400)

    user = User.query.filter_by(login=login).first() # if there is not such user
    if not user:
        abort(404)

    recovery_token = [t for t in user.recovery_tokens if t.token == token]
    if len(recovery_token) < 1: # no tokens
        abort(404)
    if len(recovery_token) > 1: # to many tokens
        abort(500)

    recovery_token = recovery_token[0]
    if recovery_token.exp_date < datetime.utcnow(): # old token
        abort(400)

    session['can_reset_password'] = True
    session['login'] = login
    return redirect(url_for('reset_password'))

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    login = session.get('login', None)
    if not session.get('can_reset_password', None) or not login: # if something is missing
        abort(400)

    form = ResetPasswordForm(meta={'csrf_context': session})

    if form.validate_on_submit():
        password = form.password.data
        user = User.query.filter_by(login=login).first()
        user.set_password(password)
        db.session.commit()
        session['can_reset_password'] = False

        info = "Password successfully updated. You can login now."
        return render_template('info.html', message=info)

    return render_template('reset-password.html', form=form)

# <----- POSTS ----->

@app.route('/posts/<id>')
@login_required
def get_posts(id):
    user = User.query.filter_by(id=id).first()
    posts = user.posts
    return render_template('posts.html', posts=posts, user=current_user)

@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = CreatePostForm(meta={'csrf_context': session})

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        public = form.public.data
        new_post = Post(
            title=title,
            content=content,
            author=current_user,
            public=public
        )
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('get_posts', id=current_user.id))
    
    return render_template('add-post.html', form=form, user=current_user)

@app.route('/remove-post/<id>')
@login_required
def remove_post(id):
    post = Post.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('get_posts', id=current_user.id))

# <----- supplementary functions ----->
@app.route('/all-users') # debug only
def all_users():
    users = User.query.all()
    return ' '.join([str(user.id) for user in users])

def get_delay(count):
    if count < 4:
        return 0
    elif count < 10:
        return 1
    elif count < 50:
        return 3
    else:
        return 10

def send_email(email, title, content):
    port = 465  # For SSL
    mail_login = app.config['GMAIL_LOGIN']
    mail_password = app.config['GMAIL_PASSWORD']

    if not mail_login or not mail_password:
        abort(500)

    sender_email = mail_login
    receiver_email = email
    message = MIMEMultipart("alternative")
    message["Subject"] = title
    message["From"] = sender_email
    message["To"] = receiver_email

    part1 = MIMEText(content, "plain")
    message.attach(part1)

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=ssl.create_default_context()) as server:
        server.login(mail_login, mail_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

if __name__ == '__main__':
    app.run(debug=True)