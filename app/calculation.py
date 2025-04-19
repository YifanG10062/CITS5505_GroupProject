import pandas as pd
import quantstats as qs
from app.models import db, Price

# This function calculates key performance metrics for a given portfolio allocation.
# You can optionally specify which metrics to return using the 'fields' argument.
# Example usage: calculate_portfolio_metrics(allocation, "2020-01-01", 10000, fields=["cagr", "return_percent"])
def calculate_portfolio_metrics(allocation: dict[str, float], start_date: str, initial_amount: float, fields: list[str] = None) -> dict:
    all_df = []

    # Query the database for price records of each asset starting from a given date
    for asset, weight in allocation.items():
        records = Price.query.filter(
            Price.asset_code == asset,
            Price.date >= start_date
        ).order_by(Price.date.asc()).all()

        if not records:
            continue

        # Convert the query result into a Pandas DataFrame
        df = pd.DataFrame([{
            "date": r.date,
            "close": r.close_price
        } for r in records])

        # Format the 'date' column and set it as the index
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)

        # Rename the 'close' column to the asset code for identification
        df.rename(columns={"close": asset}, inplace=True)

        # Append the processed DataFrame to the list
        all_df.append(df)

    # If no data was retrieved, return an empty dictionary
    if not all_df:
        return {}

    # Merge all asset DataFrames on the date index
    combined = pd.concat(all_df, axis=1, join="inner").dropna()
    if combined.empty:
        return {}

    # Get the starting price of each asset
    start_prices = combined.iloc[0]

    # Calculate the number of shares to buy for each asset based on the initial investment
    shares = {a: (initial_amount * w) / start_prices[a] for a, w in allocation.items()}

    # Initialize a time series for the total portfolio value
    portfolio_value = pd.Series(0.0, index=combined.index)

    # Sum the value of all asset holdings over time
    for asset in allocation:
        portfolio_value += combined[asset] * shares[asset]

    # Compute daily returns
    returns = portfolio_value.pct_change().dropna()

    # Generate performance metrics using QuantStats
    stats = qs.reports.metrics(returns, mode="full", display=False)

    # Extract the final date and final value of the portfolio
    calculated_at = combined.index[-1].strftime("%Y-%m-%d")
    current_value = portfolio_value.iloc[-1]
    profit = current_value - initial_amount
    return_percent = profit / initial_amount

    # Selectively return requested fields (or all if none specified)
    result = {}

    if fields is None or "calculated_at" in fields:
        result["calculated_at"] = calculated_at
    if fields is None or "current_value" in fields:
        result["current_value"] = float(current_value)
    if fields is None or "profit" in fields:
        result["profit"] = float(profit)
    if fields is None or "return_percent" in fields:
        result["return_percent"] = float(return_percent)
    if fields is None or "cagr" in fields:
        result["cagr"] = float(stats.loc['CAGR﹪'].iloc[0]) / 100
    if fields is None or "volatility" in fields:
        result["volatility"] = float(stats.loc['Volatility (ann.)'].iloc[0])
    if fields is None or "max_drawdown" in fields:
        result["max_drawdown"] = float(stats.loc['Max Drawdown'].iloc[0])

    return result


# This function returns time series data for plotting or visualization.
# It includes portfolio value over time, daily returns, and cumulative returns.
def get_portfolio_timeseries(allocation: dict[str, float], start_date: str, initial_amount: float) -> dict:
    all_df = []

    for asset, weight in allocation.items():
        records = Price.query.filter(
            Price.asset_code == asset,
            Price.date >= start_date
        ).order_by(Price.date.asc()).all()

        if not records:
            continue

        df = pd.DataFrame([{
            "date": r.date,
            "close": r.close_price
        } for r in records])
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        df.rename(columns={"close": asset}, inplace=True)
        all_df.append(df)

    if not all_df:
        return {}

    combined = pd.concat(all_df, axis=1, join="inner").dropna()
    if combined.empty:
        return {}

    start_prices = combined.iloc[0]
    shares = {a: (initial_amount * w) / start_prices[a] for a, w in allocation.items()}
    portfolio_value = pd.Series(0.0, index=combined.index)
    for asset in allocation:
        portfolio_value += combined[asset] * shares[asset]

    returns = portfolio_value.pct_change().dropna()
    cum_returns = (1 + returns).cumprod()

    return {
        "portfolio_value_series": portfolio_value.to_dict(),
        "daily_returns_series": returns.to_dict(),
        "cumulative_returns_series": cum_returns.to_dict(),
    }


# This function returns the cumulative returns of SPY from a given start date.
def get_spy_cumulative_returns(start_date: str, match_dates: list[str]) -> list[float]:
    records = db.session.query(Price).filter(
        Price.asset_code == "SPY",
        Price.date >= start_date
    ).order_by(Price.date.asc()).all()

    if not records:
        return []

    df = pd.DataFrame([{
        "date": r.date,
        "close": r.close_price
    } for r in records])
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)

    returns = df["close"].pct_change().dropna()
    cum_returns = (1 + returns).cumprod()
    cum_returns = cum_returns.loc[cum_returns.index.intersection(pd.to_datetime(match_dates))]

    return cum_returns.tolist()