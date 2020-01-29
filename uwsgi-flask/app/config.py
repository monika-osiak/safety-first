import os
from secrets import token_hex
from dotenv import load_dotenv
from redis import Redis

load_dotenv(verbose=True)
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'sqlite.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_TYPE = 'redis'
    SESSION_REDIS = Redis(host='redis', port=6379)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'something'

    TESTING = False

    GMAIL_LOGIN = os.getenv('GMAIL_LOGIN')
    GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')