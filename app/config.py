import os
from datetime import timedelta

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'development-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CSRF specific settings
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
        'sqlite:///' + os.path.join(basedir, 'db',  'dev-database.sqlite')
    
    # Safari‐friendly overrides for local HTTP development:
    SESSION_COOKIE_SAMESITE = None
    SESSION_COOKIE_SECURE   = False
    REMEMBER_COOKIE_SECURE  = False

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db', 'test-database.sqlite')


# Create database directory if it doesn't exist for production config
os.makedirs(os.path.join(basedir, 'db'), exist_ok=True)

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'db', 'portfolio_data.db')

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig
}

def get_config():
    """Return the appropriate configuration object based on environment variables."""
    # Check FLASK_DEBUG first - if it's explicitly set to 0, use production
    if os.environ.get('FLASK_DEBUG') == '0':
        return config['production']
    
    # Then check for environment name - for Flask 3.x, APP_ENV is preferred
    env_name = os.environ.get('APP_ENV') or os.environ.get('FLASK_ENV', 'production')
    
    # Return the appropriate config or default to production if invalid
    return config.get(env_name, config['production'])
