from flask import Flask, make_response, render_template, session, request, flash
from flask_session import Session
from bcrypt import hashpw, gensalt

# <----- my imports ----->
from forms import RegisterForm
from config import Config
from models import db, User, set_test_data

app = Flask(__name__)
app.config.from_object(Config)
Session(app)

db.init_app(app)
with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.commit()
    set_test_data()

@app.route('/')  # main page
def index():
    return "Hello, World!"

# <------ LOGGING IN ----->

@app.route('/login')  # login form
def login():
    return make_response(render_template('login.html'))

@app.route('/logout')  #logout
def logout():
    pass

# <----- CREATING NEW ACCOUNT ----->

@app.route('/new-account', methods=['GET', 'POST'])  # registration form
def new_account():
    
    form = RegisterForm(meta={'csrf_context': session})
    if request.method == 'POST':
        print(form.password.data)
        print(form.confirm_password.data)
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

if __name__ == '__main__':
    app.run(debug=True)