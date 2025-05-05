from flask import Blueprint, render_template
from app.models import Asset

comparison = Blueprint("comparison", __name__, url_prefix="/comparison")

@comparison.route("/")
def view_comparison():
    # Define test allocations
    weights_a = {"BTC-USD": 0.2, "NVDA": 0.3, "AAPL": 0.5}
    weights_b = {"MSFT": 0.5, "AMZN": 0.3, "AMD": 0.2}

    asset_codes = set(weights_a) | set(weights_b)
    assets = Asset.query.filter(Asset.asset_code.in_(asset_codes)).all()

    strategy_map = {
        a.asset_code: {
            "display_name": a.display_name,
            "strategy": a.strategy_description,
            "logo_url": a.logo_url,
        } for a in assets
    }

    # Fake return data for example
    return_labels = [str(y) for y in range(2015, 2026)]
    cumulative_returns_a = [1.0, 1.2, 1.4, 1.5, 1.8, 2.1, 2.3, 2.7, 3.1, 3.4, 3.7]
    cumulative_returns_b = [1.0, 1.1, 1.3, 1.6, 1.7, 2.0, 2.2, 2.5, 2.8, 3.0, 3.2]

    return render_template(
        "comparison.html",
        weights_a=weights_a,
        weights_b=weights_b,
        strategy_map=strategy_map,
        return_labels=return_labels,
        cumulative_returns_a=cumulative_returns_a,
        cumulative_returns_b=cumulative_returns_b
    )
