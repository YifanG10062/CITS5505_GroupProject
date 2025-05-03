from app import db
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text

class Price(db.Model):
    __tablename__ = 'prices'
    asset_code = db.Column(db.String, primary_key=True)
    date = db.Column(db.Date, primary_key=True)
    close_price = db.Column(db.Float)

class Asset(db.Model):
    __tablename__ = 'assets'
    asset_code = db.Column(db.String, primary_key=True)
    display_name = db.Column(db.String)
    full_name = db.Column(db.String)
    type = db.Column(db.String)
    currency = db.Column(db.String)