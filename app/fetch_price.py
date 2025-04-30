import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_all_history():
    from app import db
    from app.models import Asset, Price
    
    asset_metadata = {
        "AAPL":  ("AAPL", "Apple Inc.", "stock", "USD"),
        "MSFT":  ("MSFT", "Microsoft Corp", "stock", "USD"),
        "TSLA":  ("TSLA", "Tesla Inc.", "stock", "USD"),
        "NVDA":  ("NVDA", "NVIDIA Corp", "stock", "USD"),
        "AMZN":  ("AMZN", "Amazon.com Inc.", "stock", "USD"),
        "GOOGL": ("GOOGL", "Alphabet Inc.", "stock", "USD"),
        "BRK-B": ("BRK.B", "Berkshire Hathaway", "stock", "USD"),
        "BTC-USD": ("BTC", "Bitcoin", "crypto", "USD"),
        "MSTR":  ("MSTR", "MicroStrategy", "stock", "USD"),
        "AMD":   ("AMD", "Advanced Micro Devices", "stock", "USD"),
        "SPY":   ("SPY", "S&P 500 ETF", "etf", "USD")
    }

    # Insert or update asset metadata in the database
    for code, (display, full, typ, curr) in asset_metadata.items():
        asset = Asset(
            asset_code=code,
            display_name=display,
            full_name=full,
            type=typ,
            currency=curr
        )
        db.session.merge(asset)

    start_date = "2015-01-01"
    end_date = datetime.today().strftime("%Y-%m-%d")

    for ticker in asset_metadata:
        print(f"📈 Fetching: {ticker}")
        try:
            df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)
            if "Close" not in df:
                print(f"⚠️  Skipped {ticker}, no 'Close' column.")
                continue

            df = df.reset_index()[["Date", "Close"]]
            df.columns = ["date", "close_price"]
            df["asset_code"] = ticker
            df["date"] = pd.to_datetime(df["date"]).dt.date

            for _, row in df.iterrows():
                price = Price(
                    asset_code=row["asset_code"],
                    date=row["date"],
                    close_price=row["close_price"]
                )
                db.session.merge(price)
        except Exception as e:
            print(f"❌ Error fetching {ticker}: {e}")

    db.session.commit()
    print("✅ Historical price data saved to database.")

# Command-line interface for fetching historical prices
import click
from flask.cli import with_appcontext

@click.command("refresh-history")
@with_appcontext
def refresh_history_command():
    """Fetch all historical asset prices using ORM"""
    fetch_all_history()
    click.echo("✅ Prices refreshed.")
