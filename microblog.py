from flask import Flask, make_response, render_template

app = Flask(__name__)

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

@app.route('/auth', methods=['POST'])  # authenticate user
def auth():
    return "Auth endpoint"

# <----- CREATING NEW ACCOUNT ----->

@app.route('/new-account')  # registration form
def new_account():
    return make_response(render_template('register.html'))

@app.route('/validate', methods=['POST'])  # validate new account
def validate():
    return "Validate new user"

if __name__ == '__main__':
    app.run(debug=True)