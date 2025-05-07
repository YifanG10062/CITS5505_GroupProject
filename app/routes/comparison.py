from flask import Blueprint, render_template, abort, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models.portfolio import PortfolioSummary
from app.models.asset import Price, Asset
from app import db
import json
from datetime import datetime

# Blueprint for comparison views, mounted at '/comparison'
comparison = Blueprint("comparison", __name__, url_prefix="/comparison")

@comparison.route("/", strict_slashes=False)
@login_required
def view_comparison():
    # Fetch portfolio IDs from query params
    a_id = request.args.get("a", type=int)
    b_id = request.args.get("b", type=int)

    # Load Portfolio A or fallback
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
        p_a = None

    # Load Portfolio B or fallback
    if b_id:
        p_b = PortfolioSummary.query.get_or_404(b_id)
        if p_b.user_id != current_user.id and not p_b.is_shared:
            abort(403)
        weights_b = json.loads(p_b.allocation_json) or {}
        name_b = p_b.portfolio_name
    else:
        weights_b = {"MSFT": 0.5, "AMZN": 0.3, "AMD": 0.2}
        name_b = "Sample Portfolio B"
        p_b = None

    # Benchmark (SPY)
    weights_spy = {"SPY": 1.0}
    name_spy    = "SPY"

    # Combine asset codes
    asset_codes = list(set(weights_a) | set(weights_b) | set(weights_spy))

    # Acumulate start_date and end_date
    start_date_result = (
        db.session.query(func.min(Price.date))
                  .filter(Price.asset_code.in_(asset_codes))
                  .group_by(Price.asset_code)
                  .all()
    )
    start_date = max((r[0] for r in start_date_result), default=datetime(2015,1,1))
    start_str = start_date.strftime("%Y-%m-%d")

    end_date_result = (
        db.session.query(func.max(Price.date))
                  .filter(Price.asset_code.in_(asset_codes))
                  .group_by(Price.asset_code)
                  .all()
    )
    end_date = min((r[0] for r in end_date_result), default=datetime.today())
    end_str = end_date.strftime("%Y-%m-%d")

    # Get the last updated date
    if p_a and p_a.metric_updated_at:
        updated_at = p_a.metric_updated_at.strftime("%b %d %Y")
    else:
        updated_at = datetime.today().strftime("%b %d %Y") if not p_a else "Unknown"

    # Fetch asset info for descriptions
    assets_info_a = Asset.query.filter(Asset.asset_code.in_(weights_a.keys())).all()

    # Construct { name, description } list
    descriptions_a = [
        {"name": asset.asset_code, "description": asset.strategy_description}
        for asset in assets_info_a
        if asset.strategy_description
    ]

    assets_info_b = Asset.query.filter(Asset.asset_code.in_(weights_b.keys())).all()

    descriptions_b = [
        {"name": asset.asset_code, "description": asset.strategy_description}
        for asset in assets_info_b
        if asset.strategy_description
    ]

    # Render the template with the data
    return render_template(
        "comparison.html",
        weights_a=weights_a,
        weights_b=weights_b,
        weights_spy=weights_spy,
        name_a=name_a,
        name_b=name_b,
        name_spy=name_spy,
        start_date=start_str,
        end_date=end_str,
        initial_investment=initial_investment,
        updated_at=updated_at,
        descriptions_a=descriptions_a,
        descriptions_b=descriptions_b
    )
