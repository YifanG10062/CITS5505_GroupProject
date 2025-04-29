from flask import Blueprint, request, jsonify
from app.calculation import calculate_portfolio_metrics, get_portfolio_timeseries, get_spy_cumulative_returns
import pandas as pd

api_bp = Blueprint('api', __name__, url_prefix='/api')

# 1. Summary statistics
@api_bp.route("/portfolio-summary", methods=["POST"])
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

# 2. Time series data for plotting + heatmap
@api_bp.route("/timeseries", methods=["POST"])
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

    try:
        daily_returns = pd.Series(ts_data["daily_returns_series"])
        daily_returns.index = pd.to_datetime(daily_returns.index)

        monthly = daily_returns.resample("M").apply(lambda x: (x + 1).prod() - 1)
        monthly_df = monthly.reset_index()
        monthly_df.columns = ["Date", "MonthlyReturn"]
        monthly_df["Year"] = monthly_df["Date"].dt.year
        monthly_df["Month"] = monthly_df["Date"].dt.strftime("%b")

        month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        pivot = (
            monthly_df.pivot(index="Year", columns="Month", values="MonthlyReturn")
            .reindex(columns=month_order)
            .fillna(0)
        )

        heatmap_labels = month_order
        heatmap_datasets = [
            {
                "year": int(year),
                "values": [round(val, 4) for val in row]
            }
            for year, row in pivot.iterrows()
        ]
    except Exception as e:
        print("Monthly heatmap generation failed:", e)
        heatmap_labels = []
        heatmap_datasets = []

    return jsonify({
        "labels": labels,
        "strategy": strategy,
        "benchmark": benchmark,
        "monthlyReturns": {
            "labels": heatmap_labels,
            "datasets": heatmap_datasets
        }
    })
