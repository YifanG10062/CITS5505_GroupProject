from app import db
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

# --- PortfolioSummary Table ---
class PortfolioSummary(db.Model):
    __tablename__ = 'portfolio_summary'

    portfolio_id = Column(Integer, primary_key=True)
    portfolio_name = Column(String(255), nullable=False)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    creator_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    shared_from_id = Column(Integer, ForeignKey('user.id'), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    input_updated_at = Column(DateTime, default=datetime.utcnow)
    metric_updated_at = Column(DateTime, default=datetime.utcnow)

    calculated_at = Column(Date, nullable=True)
    allocation_json = Column(Text, nullable=False)

    start_date = Column(Date, nullable=False)
    initial_amount = Column(Float, nullable=False)

    current_value = Column(Float, nullable=True)
    profit = Column(Float, nullable=True)
    return_percent = Column(Float, nullable=True)
    cagr = Column(Float, nullable=True)
    volatility = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)

    is_editable = Column(Boolean, default=True)
    is_shareable = Column(Boolean, default=True)
    is_deletable = Column(Boolean, default=True)
    is_shown = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    creator = relationship("User", foreign_keys=[creator_id])
    shared_from = relationship("User", foreign_keys=[shared_from_id])

    def __repr__(self):
        return f'<PortfolioSummary {self.portfolio_name}>'

# --- PortfolioVersion Table ---
class PortfolioVersion(db.Model):
    __tablename__ = 'portfolio_version'

    portfolio_version_id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolio_summary.portfolio_id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    updated_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

    allocation_json = Column(Text, nullable=False)

    # Optional fields (can be duplicated for easier recovery)
    portfolio_name = Column(String(255), nullable=True)
    start_date = Column(Date, nullable=True)
    initial_amount = Column(Float, nullable=True)

    def __repr__(self):
        return f'<PortfolioVersion {self.portfolio_version_id}>'

# --- PortfolioChangeLog Table ---
class PortfolioChangeLog(db.Model):
    __tablename__ = 'portfolio_change_log'

    portfolio_log_id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolio_summary.portfolio_id'), nullable=False)
    changed_by = Column(Integer, ForeignKey('user.id'), nullable=False)

    field_changed = Column(String(255), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PortfolioChangeLog {self.portfolio_log_id}>'

# --- PortfolioShareLog Table ---
class PortfolioShareLog(db.Model):
    __tablename__ = 'portfolio_share_log'

    portfolio_share_id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    to_user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    from_portfolio_id = Column(Integer, ForeignKey('portfolio_summary.portfolio_id'), nullable=False)
    to_portfolio_id = Column(Integer, ForeignKey('portfolio_summary.portfolio_id'), nullable=False)

    shared_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PortfolioShareLog {self.portfolio_share_id}>'