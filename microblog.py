from flask import Flask, make_response, render_template, session
from forms import RegisterForm
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

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
    if form.validate_on_submit():
        flash('Your account has been created!', 'alert-success')

        login = form.login.data
        password = form.password.data
        email = form.email.data

        return make_response(200, f'Hello {login}')

    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)