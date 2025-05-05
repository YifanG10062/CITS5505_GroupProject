from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from app import db

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(200), nullable=False, unique=True)
    user_pswd = db.Column(db.String(200), nullable=False)
    user_fName = db.Column(db.String(200), nullable=False)
    user_lName = db.Column(db.String(200), nullable=False)
    user_token = db.Column(db.String(1000), nullable=True)

    portfolio_summaries = relationship("PortfolioSummary", foreign_keys='PortfolioSummary.user_id', back_populates="user")
    created_portfolios = relationship("PortfolioSummary", foreign_keys='PortfolioSummary.creator_id', back_populates="creator")
    shared_portfolios = relationship("PortfolioSummary", foreign_keys='PortfolioSummary.shared_from_id', back_populates="shared_from")
