# This file re-exports all models for easier imports

# Export db for backwards compatibility with other modules
from app import db

# Direct re-exports of all models
from app.models.user import User
from app.models.asset import Asset, Price
from app.models.portfolio import (
    PortfolioSummary, 
    PortfolioVersion, 
    PortfolioChangeLog, 
    PortfolioShareLog
)

# Add any additional models here when created