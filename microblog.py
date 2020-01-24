from flask import Flask, make_response, render_template, session, request, flash, redirect, url_for, abort
from flask_session import Session
from flask_login import current_user, login_user, logout_user, login_required
from bcrypt import hashpw, gensalt
from datetime import datetime, timedelta
from time import sleep

# <----- my imports ----->
from forms import RegisterForm, LoginForm, ChangePasswordForm, CreatePostForm
from config import Config
from models import db, set_test_data, User, Login, Post
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
    return render_template('index.html', user=current_user)

# <------ LOGGING IN ----->

@app.route('/login', methods=['GET', 'POST'])  # login form
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'), user=current_user)

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
            next_page = url_for('get_posts', id=current_user.id)
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

# <----- MANAGING AN ACCOUNT ----->
@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm({'csrf_context': session})
    form.login.data = current_user.login
    if form.validate_on_submit():
        new_password = form.new_password.data
        current_id = current_user.id
        user = User.query.filter_by(id=current_id).first()
        user.set_password(new_password)
        db.session.commit()

        flash('Password successfully changed!', 'alert-success')
        return redirect(url_for('index'))

    return render_template('change-password.html', form=form, user=current_user)


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

# <----- supplementary functions ----->
@app.route('/all-users')
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

if __name__ == '__main__':
    app.run(debug=True)