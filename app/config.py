import os

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    SECRET_KEY = os.environ.get('GROUP_PROJECT_SECRET_KEY', 'dev-default-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DeploymentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'db', 'portfolio_data.db')

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
