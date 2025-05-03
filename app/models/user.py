# app/models.py
from app import db
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

# --- User Table ---
# NOTE: Temporary placeholder for User table.
# Please update this model later (assigned to Pavan).
# Current version only exists to support building Portfolio tables.
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)