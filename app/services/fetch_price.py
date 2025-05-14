import os
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
        code: f"/static/icons/{code.lower().replace('.', '-')}.svg"
        for code in asset_metadata
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

    print(f"Starting asset metadata upsert for {len(asset_metadata)} assets...")
    # Insert or update asset metadata
    for code, (display, full, typ, curr) in asset_metadata.items():
        existing = db.session.get(Asset, code)
        logo = existing.logo_url if existing else default_logos.get(code)
        asset = Asset(
            asset_code=code,
            display_name=display,
            full_name=full,
            type=typ,
            currency=curr,
            logo_url=logo,
            strategy_description=ASSET_STRATEGY.get(code)
        )
        db.session.merge(asset)
    db.session.commit()
    print("✔ Asset metadata upsert complete.")

    start_date = "2015-01-01"
    end_date = datetime.today().strftime("%Y-%m-%d")
    print(f"Fetching price data from {start_date} to {end_date}...")

    # Download and insert historical price data
    for ticker in asset_metadata:
        print(f"📈 Fetching: {ticker}")
        df = None
        # Primary: yfinance
        try:
            df = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                interval="1d",
                progress=False,
                session=session
            )
            if df.empty or "Close" not in df:
                raise ValueError("No 'Close' data returned")
        except Exception as e:
            print(f"✘ yfinance failed for {ticker}: {e}")
            # Fallback 1: Stooq
            try:
                sym = ticker.lower().replace("-", ".")
                if ".us" not in sym:
                    sym += ".us"
                d1 = start_date.replace("-", "")
                d2 = end_date.replace("-", "")
                url = f"https://stooq.com/q/d/l/?s={sym}&d1={d1}&d2={d2}&i=d"
                df = pd.read_csv(
                    url,
                    parse_dates=["Date"],
                    index_col="Date",
                    usecols=["Date", "Close"]
                )
                print(f"Using Stooq data source for {ticker}")
            except Exception as e1:
                print(f"✘ Stooq failed for {ticker}: {e1}")
                # Fallback 2: Local CSV cache
                cache_file = os.path.join('data', f"{ticker}.csv")
                if os.path.exists(cache_file):
                    try:
                        df = pd.read_csv(
                            cache_file,
                            parse_dates=["date"],
                            index_col="date"
                        )
                        df.index.name = "Date" 
                        df.rename(columns={"close_price": "Close"}, inplace=True)
                        print(f"Loaded cache for {ticker} from {cache_file}")
                    except Exception as e2:
                        print(f"✘ Loading cache failed for {ticker}: {e2}")
                else:
                    print(f"✘ All data sources failed for {ticker}")

        if df is None or df.empty or "Close" not in df:
            print(f"Skipped {ticker}, no 'Close' data available.")
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
    db.session.commit()
    print("✔ All historical prices saved successfully!")

# Flask CLI command to refresh prices
@click.command("refresh-history")
@with_appcontext

def refresh_history_command():
    """Fetch all historical asset prices and update asset metadata"""
    click.echo("Starting full history refresh...")
    fetch_all_history()
    click.echo("✔ Full history refresh complete.")
