from app import db
from sqlalchemy import Float, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

# --- PortfolioSummary Table ---
class PortfolioSummary(db.Model):
    __tablename__ = 'portfolio_summary'

    portfolio_id = db.Column(db.Integer, primary_key=True)
    portfolio_name = db.Column(db.String(255), nullable=False)

    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    creator_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    shared_from_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=True)
    
    # Add username and email fields for denormalization
    user_username = db.Column(db.String(200), nullable=False)
    user_email = db.Column(db.String(200), nullable=False)
    creator_username = db.Column(db.String(200), nullable=False)
    creator_email = db.Column(db.String(200), nullable=False)
    shared_from_username = db.Column(db.String(200), nullable=True)
    shared_from_email = db.Column(db.String(200), nullable=True)

    created_at = db.Column(DateTime, default=datetime.utcnow)
    input_updated_at = db.Column(DateTime, default=datetime.utcnow)
    metric_updated_at = db.Column(DateTime, default=datetime.utcnow)

    calculated_at = db.Column(Date, nullable=True)
    allocation_json = db.Column(Text, nullable=False)

    start_date = db.Column(Date, nullable=False)
    initial_amount = db.Column(Float, nullable=False)

    current_value = db.Column(Float, nullable=True)
    profit = db.Column(Float, nullable=True)
    return_percent = db.Column(Float, nullable=True)
    cagr = db.Column(Float, nullable=True)
    volatility = db.Column(Float, nullable=True)
    max_drawdown = db.Column(Float, nullable=True)

    is_editable = db.Column(Boolean, default=True)
    is_shareable = db.Column(Boolean, default=True)
    is_deletable = db.Column(Boolean, default=True)
    is_shown = db.Column(Boolean, default=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="portfolio_summaries")
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_portfolios")
    shared_from = relationship("User", foreign_keys=[shared_from_id], back_populates="shared_portfolios")

    def __repr__(self):
        return f'<PortfolioSummary {self.portfolio_name}>'

    # Helper method to update user info from related users
    def update_user_info(self):
        from app.models.user import User
        
        # Update owner info
        owner = User.query.get(self.user_id)
        if owner:
            self.user_username = owner.username
            self.user_email = owner.user_email
            
        # Update creator info  
        creator = User.query.get(self.creator_id)
        if creator:
            self.creator_username = creator.username
            self.creator_email = creator.user_email
            
        # Update shared_from info if applicable
        if self.shared_from_id:
            shared_from = User.query.get(self.shared_from_id)
            if shared_from:
                self.shared_from_username = shared_from.username
                self.shared_from_email = shared_from.user_email

# --- PortfolioVersion Table ---
class PortfolioVersion(db.Model):
    __tablename__ = 'portfolio_version'

    portfolio_version_id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, ForeignKey('portfolio_summary.portfolio_id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    updated_by = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    updated_at = db.Column(DateTime, default=datetime.utcnow)

    allocation_json = db.Column(Text, nullable=False)

    # Optional fields (can be duplicated for easier recovery)
    portfolio_name = db.Column(db.String(255), nullable=True)
    start_date = db.Column(Date, nullable=True)
    initial_amount = db.Column(Float, nullable=True)

    def __repr__(self):
        return f'<PortfolioVersion {self.portfolio_version_id}>'

# --- PortfolioChangeLog Table ---
class PortfolioChangeLog(db.Model):
    __tablename__ = 'portfolio_change_log'

    portfolio_log_id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, ForeignKey('portfolio_summary.portfolio_id'), nullable=False)
    changed_by = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)

    field_changed = db.Column(db.String(255), nullable=False)
    old_value = db.Column(Text, nullable=True)
    new_value = db.Column(Text, nullable=True)

    timestamp = db.Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PortfolioChangeLog {self.portfolio_log_id}>'

# --- PortfolioShareLog Table ---
class PortfolioShareLog(db.Model):
    __tablename__ = 'portfolio_share_log'

    portfolio_share_id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    to_user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)

    from_portfolio_id = db.Column(db.Integer, ForeignKey('portfolio_summary.portfolio_id'), nullable=False)
    to_portfolio_id = db.Column(db.Integer, ForeignKey('portfolio_summary.portfolio_id'), nullable=False)

    shared_at = db.Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PortfolioShareLog {self.portfolio_share_id}>'