from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models.portfolio import PortfolioSummary
from app.models.asset import Price
from app import db
import json
from datetime import datetime

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/portfolios/<int:portfolio_id>/dashboard", endpoint="show")
@login_required
def show(portfolio_id):
    portfolio = PortfolioSummary.query.get(portfolio_id)

    if not portfolio:
        # fallback: for when the user hasn't saved a portfolio yet (e.g. testing or preview mode)
        weights = {"BTC-USD": 0.5, "NVDA": 0.3, "AAPL": 0.2}
        portfolio_name = "Preview Portfolio"
        creator = current_user.username
        updated_at = datetime.today().strftime("%b %d %Y")
        initial_investment = 1000
        asset_codes = list(weights.keys())
    else:
        if portfolio.user_id != current_user.id and not portfolio.is_shared:
            abort(403)

        try:
            weights = json.loads(portfolio.allocation_json)
        except Exception:
            weights = {}

        portfolio_name = portfolio.portfolio_name
        creator = portfolio.creator_username
        initial_investment = portfolio.initial_amount
        asset_codes = list(weights.keys())
        updated_at = portfolio.metric_updated_at.strftime("%b %d %Y") if portfolio.metric_updated_at else "Unknown"

    # Compute shared start and end dates
    start_date_result = db.session.query(func.min(Price.date)).filter(
        Price.asset_code.in_(asset_codes)
    ).group_by(Price.asset_code).all()
    start_date = max((r[0] for r in start_date_result), default=datetime(2015, 1, 1)).strftime("%Y-%m-%d")

    end_date_result = db.session.query(func.max(Price.date)).filter(
        Price.asset_code.in_(asset_codes)
    ).group_by(Price.asset_code).all()
    end_date = min((r[0] for r in end_date_result), default=datetime.today()).strftime("%Y-%m-%d")

    # Allocation summary string
    asset_string = " + ".join([f"{int(w * 100)}% {code}" for code, w in weights.items()])

    return render_template("dashboard.html",
        weights=weights,
        asset_string=asset_string,
        portfolio_name=portfolio_name,
        creator=creator,
        updated_at=updated_at,
        start_date=start_date,
        end_date=end_date,
        initial_investment=initial_investment
    )
