from flask import Blueprint, request, jsonify, render_template
from app.models import db, Price
from app.calculation import calculate_portfolio_metrics, get_portfolio_timeseries, get_spy_cumulative_returns
import pandas as pd

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
        "maxDrawdown": result["max_drawdown"]          
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