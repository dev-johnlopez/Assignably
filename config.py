import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.flaskenv'))


class Config(object):
    DEBUG = os.environ.get('FLASK_DEBUG') or False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_TO_STDOUT = 1
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')
    SECURITY_EMAIL_SENDER = os.environ.get('SECURITY_EMAIL_SENDER')
    SECURITY_FLASH_MESSAGES = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_REGISTER_URL = '/u/register'
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_DEBUG = os.environ.get('MAIL_DEBUG') or 0
    ADMINS = ['john@johnlopez.org']
    SECURITY_TRACKABLE = True
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    S3_KEY = os.environ.get('S3_KEY')
    S3_SECRET_ACCESS_KEY = os.environ.get('S3_SECRET_ACCESS_KEY')
    S3_BUCKET = os.environ.get('S3_BUCKET')
    SSL_DISABLE = False


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    WTF_CSRF_METHODS = []
