# app/models.py
from app import db

class Price(db.Model):
    __tablename__ = 'prices'
    asset_code = db.Column(db.String, primary_key=True)
    date = db.Column(db.String, primary_key=True)
    close_price = db.Column(db.Float)