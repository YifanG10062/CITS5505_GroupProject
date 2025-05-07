from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models.portfolio import PortfolioSummary
from app.models.asset import Price
from app import db
import json
from datetime import datetime
from flask import request, jsonify
from app.calculation import calculate_portfolio_metrics

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
@dashboard.route("/api/portfolio-top-movers", methods=["POST"])
@login_required
def top_movers():
    data = request.get_json()
    weights = data.get("weights", {})
    if not weights:
        return jsonify({"error": "Missing weights"}), 400

    start_date = "2015-01-01"
    initial_amount = 1000

    asset_returns = []
    for asset, weight in weights.items():
        metrics = calculate_portfolio_metrics({asset: 1.0}, start_date, initial_amount, fields=["return_percent"])
        if metrics and "return_percent" in metrics:
            asset_returns.append((asset, round(metrics["return_percent"] * 100, 2)))

    asset_returns.sort(key=lambda x: x[1], reverse=True)
    top = asset_returns[:3]
    bottom = asset_returns[-3:] if len(asset_returns) > 3 else []

    combined = top + bottom
    labels = [a[0] for a in combined]
    values = [a[1] for a in combined]

    return jsonify({"labels": labels, "values": values})
