from flask import Blueprint, render_template, abort, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models.portfolio import PortfolioSummary
from app.models.asset import Price
from app import db
import json
from datetime import datetime

# Blueprint for comparison views, mounted at '/comparison'
comparison = Blueprint("comparison", __name__, url_prefix="/comparison")

@comparison.route("/", strict_slashes=False)
@login_required
def view_comparison():
    """
    Render the comparison page for two portfolios (A vs B).

    Query Parameters:
      a: Portfolio A ID
      b: Portfolio B ID
    """
    # Fetch portfolio IDs
    a_id = request.args.get("a", type=int)
    b_id = request.args.get("b", type=int)

    # Load Portfolio A or use fallback sample
    if a_id:
        p_a = PortfolioSummary.query.get_or_404(a_id)
        if p_a.user_id != current_user.id and not p_a.is_shared:
            abort(403)
        weights_a = json.loads(p_a.allocation_json) or {}
        name_a = p_a.portfolio_name
        initial_investment = p_a.initial_amount
    else:
        weights_a = {"BTC-USD": 0.2, "NVDA": 0.3, "AAPL": 0.5}
        name_a = "Sample Portfolio A"
        initial_investment = 1000

    # Load Portfolio B or use fallback sample
    if b_id:
        p_b = PortfolioSummary.query.get_or_404(b_id)
        if p_b.user_id != current_user.id and not p_b.is_shared:
            abort(403)
        weights_b = json.loads(p_b.allocation_json) or {}
        name_b = p_b.portfolio_name
    else:
        weights_b = {"MSFT": 0.5, "AMZN": 0.3, "AMD": 0.2}
        name_b = "Sample Portfolio B"

    # Combine assets from both portfolios
    asset_codes = list(set(weights_a) | set(weights_b))

    # Determine the overlapping date range for these assets (same as dashboard)
    start_date_result = (
        db.session.query(func.min(Price.date))
        .filter(Price.asset_code.in_(asset_codes))
        .group_by(Price.asset_code)
        .all()
    )
    # Max of individual asset start dates ensures all assets have data from that date
    start_date = max((r[0] for r in start_date_result), default=datetime(2015, 1, 1))
    start_str = start_date.strftime("%Y-%m-%d")

    end_date_result = (
        db.session.query(func.max(Price.date))
        .filter(Price.asset_code.in_(asset_codes))
        .group_by(Price.asset_code)
        .all()
    )
    # Min of individual asset end dates ensures all assets have data up to that date
    end_date = min((r[0] for r in end_date_result), default=datetime.today())
    end_str = end_date.strftime("%Y-%m-%d")

    # Render the comparison template
    return render_template(
        "comparison.html",
        weights_a=weights_a,
        weights_b=weights_b,
        name_a=name_a,
        name_b=name_b,
        start_date=start_str,
        end_date=end_str,
        initial_investment=initial_investment
    )
