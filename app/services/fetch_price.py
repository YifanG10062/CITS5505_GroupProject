import yfinance as yf
import pandas as pd
from datetime import datetime
import click
from flask.cli import with_appcontext
from curl_cffi import requests

# Create a browser-like session to avoid being blocked
session = requests.Session(impersonate="chrome")

def fetch_all_history():
    from app import db
    from app.models import Asset, Price

    # Asset metadata: display name, full name, type, currency
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

    # Default logo URLs for each asset
    default_logos = {
        "AAPL": "/static/icons/aapl.svg",
        "MSFT": "/static/icons/msft.svg",
        "TSLA": "/static/icons/tsla.svg",
        "NVDA": "/static/icons/nvda.svg",
        "AMZN": "/static/icons/amzn.svg",
        "GOOGL": "/static/icons/googl.svg",
        "BRK-B": "/static/icons/brk-b.svg",
        "BTC-USD": "/static/icons/btc-usd.svg",
        "MSTR": "/static/icons/mstr.svg",
        "AMD": "/static/icons/amd.svg",
        "SPY": "/static/icons/spy.svg"
    }

    # Strategy description for each asset
    ASSET_STRATEGY = {
        "AAPL": "Tech giant, stable long-term growth",
        "MSFT": "Strong earnings, cloud leader",
        "TSLA": "High-growth, electric vehicle pioneer",
        "NVDA": "AI & GPU leader, explosive performance",
        "AMZN": "eCommerce & cloud infrastructure leader",
        "GOOGL": "Digital ad powerhouse",
        "BRK-B": "Low-volatility, value investing benchmark",
        "BTC-USD": "High volatility, alternative asset",
        "MSTR": "Bitcoin proxy with leveraged exposure",
        "AMD": "Chipmaker with strong recent growth in CPUs and GPUs",
        "SPY": "Tracks the S&P 500, broad-market exposure"
    }

    # Insert or update asset metadata into the database
    for code, (display, full, typ, curr) in asset_metadata.items():
        # Use existing logo if available
        existing = db.session.get(Asset, code)
        logo = existing.logo_url if existing else default_logos.get(code)

        # Create or update Asset record
        asset = Asset(
            asset_code=code,
            display_name=display,
            full_name=full,
            type=typ,
            currency=curr,
            logo_url=logo,
            strategy_description=ASSET_STRATEGY.get(code)
        )
        db.session.merge(asset)  # Merge ensures insert or update

    start_date = "2015-01-01"
    end_date = datetime.today().strftime("%Y-%m-%d")

    # Download and insert historical price data
    for ticker in asset_metadata:
        print(f"📈 Fetching: {ticker}")
        try:
            df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False, session=session)

            if "Close" not in df:
                print(f"⚠️  Skipped {ticker}, no 'Close' column.")
                continue

            df = df.reset_index()[["Date", "Close"]]
            df.columns = ["date", "close_price"]
            df["asset_code"] = ticker
            df["date"] = pd.to_datetime(df["date"]).dt.date

            # Insert or update daily prices
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
    print("✅ Historical price data and asset metadata saved.")

# Flask CLI command to refresh prices from yfinance
@click.command("refresh-history")
@with_appcontext
def refresh_history_command():
    """Fetch all historical asset prices and update asset metadata"""
    fetch_all_history()
    click.echo("✅ Prices refreshed.")
