# app/routes.py
from flask import Blueprint, request, jsonify, render_template
from app.models import Price
from app import db
from sqlalchemy.orm import sessionmaker
import pandas as pd
import quantstats as qs

main = Blueprint("main", __name__)

def run_backtest(weights, start_date, initial_investment):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    all_df = []

    for asset in weights:
        records = session.query(Price).filter(
            Price.asset_code == asset,
            Price.date >= start_date
        ).order_by(Price.date.asc()).all()

        if not records:
            continue

        df = pd.DataFrame([{
            "date": r.date,
            "close_price": r.close_price
        } for r in records])
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        df.rename(columns={"close_price": asset}, inplace=True)
        all_df.append(df)

    session.close()

    combined = pd.concat(all_df, axis=1, join="inner").dropna()
    start_prices = combined.iloc[0]
    shares = {a: (initial_investment * w) / start_prices[a] for a, w in weights.items()}

    portfolio_value = pd.Series(0.0, index=combined.index)
    for asset in weights:
        portfolio_value += combined[asset] * shares[asset]

    returns = portfolio_value.pct_change().dropna()
    stats = qs.reports.metrics(returns, mode="full")

    return {
        "portfolio_value": portfolio_value,
        "returns": returns,
        "stats": stats,
        "initial": initial_investment
    }

@main.route("/")
def home():
    return render_template("dashboard.html")

@main.route("/api/portfolio-summary", methods=["POST"])
def portfolio_summary():
    data = request.json
    result = run_backtest(data["weights"], data["start_date"], data["initial_investment"])
    final = result["portfolio_value"].iloc[-1]
    summary = {
        "netWorth": round(final, 2),
        "initial": result["initial"],
        "profit": round(final - result["initial"], 2),
        "cumulativeReturn": round((final - result["initial"]) / result["initial"] * 100, 2),
        "cagr": float(result["stats"].loc["CAGR (%)"]),
        "volatility": float(result["stats"].loc["Volatility (ann.)"]),
        "maxDrawdown": float(result["stats"].loc["Max Drawdown (%)"]),
        "longestDD": int(result["stats"].loc["Longest DD Days"])
    }
    return jsonify(summary)

@main.route("/api/cumulative", methods=["POST"])
def cumulative():
    data = request.json
    result = run_backtest(data["weights"], data["start_date"], data["initial_investment"])
    cum_returns = (1 + result["returns"]).cumprod()
    labels = [str(d.date()) for d in cum_returns.index]
    values = [round(v, 2) for v in cum_returns]
    return jsonify({
        "labels": labels,
        "strategy": values,
        "benchmark": []
    })

@main.route("/api/backtest", methods=["POST"])
def backtest():
    data = request.json
    result = run_backtest(data["weights"], data["start_date"], data["initial_investment"])
    final = result["portfolio_value"].iloc[-1]
    return jsonify({
        "summary": {
            "netWorth": round(final, 2),
            "initial": result["initial"],
            "profit": round(final - result["initial"], 2),
            "cumulativeReturn": round((final - result["initial"]) / result["initial"] * 100, 2),
            "cagr": float(result["stats"].loc["CAGR (%)"]),
            "volatility": float(result["stats"].loc["Volatility (ann.)"]),
            "maxDrawdown": float(result["stats"].loc["Max Drawdown (%)"]),
            "longestDD": int(result["stats"].loc["Longest DD Days"])
        },
        "cumulative_returns": (1 + result["returns"]).cumprod().tolist(),
        "daily_returns": result["returns"].tolist(),
        "monthly_returns": qs.stats.monthly_returns(result["returns"]).to_dict()
    })