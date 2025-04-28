from flask import Blueprint, request, jsonify, render_template, redirect
from app.calculation import calculate_portfolio_metrics, get_portfolio_timeseries, get_spy_cumulative_returns

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("dashboard.html")

# 1. Summary statistics
@main.route("/api/portfolio-summary", methods=["POST"])
def portfolio_summary():
    data = request.json
    result = calculate_portfolio_metrics(
        allocation=data["weights"],
        start_date=data["start_date"],
        initial_amount=data["initial_investment"]
    )

    if not result:
        return jsonify({"error": "No valid price data"}), 400

    summary = {
        "netWorth": result["current_value"],
        "initial": data["initial_investment"],
        "profit": result["profit"],
        "cumulativeReturn": result["return_percent"], 
        "cagr": result["cagr"],                      
        "volatility": result["volatility"],          
        "maxDrawdown": result["max_drawdown"],
        "longestDD": result["longestDD"]        
    }
    return jsonify(summary)

# 2. Time series data for plotting
@main.route("/api/timeseries", methods=["POST"])
def timeseries():
    data = request.json

    ts_data = get_portfolio_timeseries(
        allocation=data["weights"],
        start_date=data["start_date"],
        initial_amount=data["initial_investment"]
    )

    if not ts_data or "cumulative_returns_series" not in ts_data:
        return jsonify({"error": "No time series data"}), 400

    labels = list(ts_data["cumulative_returns_series"].keys())
    strategy = list(ts_data["cumulative_returns_series"].values())

    benchmark = get_spy_cumulative_returns(
        start_date=data["start_date"],
        match_dates=labels
    )

    return jsonify({
        "labels": labels,
        "strategy": strategy,   
        "benchmark": benchmark   
    })

# Portfolio List View
@main.route("/portfolios")
def portfolio_list():
    # TODO: Retrieve portfolio data from database
    portfolios = []
    return render_template("portfolio_list.html", portfolios=portfolios)

# Create New Portfolio
@main.route("/portfolios/new", methods=["GET", "POST"])
def portfolio_new():
    if request.method == "POST":
        portfolio_name = request.form.get("portfolio_name")
        allocation_json = request.form.get("allocation_json")

        # TODO: Validate portfolio_name is unique for the current user
        # TODO: Replace current_user.id with actual user id once integrated
        user_id = 1  # placeholder user_id

        # TODO: Check portfolio name uniqueness here

        # Parse allocation
        import json
        allocation = json.loads(allocation_json)

        # Fixed system defaults
        initial_amount = 1000.0
        start_date = "2015-01-01"

        # Calculate financial metrics
        metrics = calculate_portfolio_metrics(
            allocation=allocation,
            start_date=start_date,
            initial_amount=initial_amount
        )

        # TODO: Insert new portfolio into database with calculated metrics

        return redirect("/portfolios")
    return render_template("portfolio_form.html", portfolio=None)

# Edit Existing Portfolio
@main.route("/portfolios/<int:portfolio_id>/edit", methods=["GET", "POST"])
def portfolio_edit(portfolio_id):
    # TODO: Retrieve portfolio data from database
    portfolio = None
    if request.method == "POST":
        portfolio_name = request.form.get("portfolio_name")
        allocation_json = request.form.get("allocation_json")

        # TODO: Validate updated portfolio name is unique if changed

        # Parse allocation
        import json
        allocation = json.loads(allocation_json)

        # Fixed system defaults
        initial_amount = 1000.0
        start_date = "2015-01-01"

        # Recalculate financial metrics
        metrics = calculate_portfolio_metrics(
            allocation=allocation,
            start_date=start_date,
            initial_amount=initial_amount
        )

        # TODO: Update portfolio in database with new allocation and recalculated metrics

        return redirect("/portfolios")
    return render_template("portfolio_form.html", portfolio=portfolio)
