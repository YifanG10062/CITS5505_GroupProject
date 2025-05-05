import os

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    SECRET_KEY = os.environ.get('GROUP_PROJECT_SECRET_KEY', 'dev-default-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CSRF specific settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # Token validity period (1 hour)

# Create database directory if it doesn't exist (for DeploymentConfig)
os.makedirs(os.path.join(basedir, 'db'), exist_ok=True)
class DeploymentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'db', 'portfolio_data.db')

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
