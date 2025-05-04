from app import db
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text

# --- Price Table ---
class Price(db.Model):
    __tablename__ = 'prices'

    asset_code = db.Column(db.String, db.ForeignKey('assets.asset_code'), primary_key=True)
    date = db.Column(db.Date, primary_key=True)
    close_price = db.Column(db.Float)

    asset = db.relationship("Asset", back_populates="prices")

# --- Asset Table ---
class Asset(db.Model):
    __tablename__ = 'assets'
    asset_code = db.Column(db.String, primary_key=True)
    display_name = db.Column(db.String)
    full_name = db.Column(db.String)
    type = db.Column(db.String)
    currency = db.Column(db.String)
    logo_url = db.Column(db.String)

    prices = db.relationship("Price", back_populates="asset", cascade="all, delete-orphan")
