from flask import Flask

app = Flask(__name__)

@app.route('/')  # main page
def index():
    return "Hello, World!"

# <------ LOGGING IN ----->

@app.route('/login')  # login form
def login():
    pass

@app.route('/logout')  #logout
def logout():
    pass

@app.route('/auth', methods=['POST'])  # authenticate user
def auth():
    pass

# <----- CREATING NEW ACCOUNT ----->

@app.route('/new-account')  # registration form
def new_account():
    pass

@app.route('/validate', methods=['POST'])  # validate new account
def validate():
    pass

if __name__ == '__main__':
    app.run(debug=True)