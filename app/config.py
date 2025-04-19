import os

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('GROUP_PROJECT_SECRET_KEY', 'dev-default-key')

class DeploymentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'portfolio_prices.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory"