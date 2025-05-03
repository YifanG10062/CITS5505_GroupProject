# This file re-exports all models to maintain backwards compatibility
# with code that imports from app.models

from app import db 

from app.models.user import User
from app.models.asset import Asset, Price
from app.models.portfolio import (
    PortfolioSummary, 
    PortfolioVersion, 
    PortfolioChangeLog, 
    PortfolioShareLog
)

# Add any additional models here when created