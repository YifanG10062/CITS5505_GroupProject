import os
from datetime import timedelta
from sqlalchemy.pool import StaticPool  # Added for in-memory DB sharing

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'development-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CSRF settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # Token validity period (1 hour)
    
    SESSION_COOKIE_SECURE = True  
    SESSION_COOKIE_HTTPONLY = True  
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'db', 'dev-database.sqlite')
    
    SESSION_COOKIE_SAMESITE = None
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # shared in-memory DB for unit and selenium tests
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'check_same_thread': False},
        'poolclass': StaticPool
    }


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'db', 'portfolio_data.db')


# Ensure the database folder exists
os.makedirs(os.path.join(basedir, 'db'), exist_ok=True)

# Environment mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig
}

def get_config():
    """Return the appropriate configuration object based on environment variables."""
    if os.environ.get('FLASK_DEBUG') == '0':
        return config['production']

    env_name = os.environ.get('APP_ENV') or os.environ.get('FLASK_ENV', 'production')
    return config.get(env_name, config['production'])
