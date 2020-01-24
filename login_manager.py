from flask import current_app
from flask_login import LoginManager

# <----- my imports ----->
from models import User

login_manager = LoginManager()
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    with current_app.app_context():
        return User.query.filter_by(id=int(user_id)).first()