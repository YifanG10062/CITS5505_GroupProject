from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.models.portfolio import PortfolioSummary
from app.models.asset import Price
from app import db
import json

dashboard = Blueprint("dashboard", __name__)  

@dashboard.route("/portfolios/<int:portfolio_id>/dashboard")
@login_required
def show(portfolio_id):
    portfolio = PortfolioSummary.query.get(portfolio_id)

    if portfolio is None:
        # fallback to mock portfolio for testing
        weights = {"BTC-USD": 0.5, "NVDA": 0.3, "AAPL": 0.2}
    else:
        if portfolio.user_id != current_user.id and not portfolio.is_shared:
            abort(403)

        try:
            weights = json.loads(portfolio.allocation_json)
        except Exception:
            weights = {}

    return render_template("dashboard.html",
                           weights=weights,
                           start_date="2015-01-01",
                           initial_investment=1000)

