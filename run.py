from app import create_app, db
from app.models.asset import Price
from app.services.fetch_price import fetch_all_history
from sqlalchemy import func
from datetime import date, timedelta

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        last_date = db.session.query(func.max(Price.date)).scalar()
        yesterday = date.today() - timedelta(days=1)

        if not last_date or last_date < yesterday:
            app.logger.warning(f"⚠️ Price data outdated (latest: {last_date}), fetching…")
            fetch_all_history()
            app.logger.info("✅ Price data fetched.")
        else:
            app.logger.info(f"✅ Price data is up-to-date (latest: {last_date}).")

    app.run(debug=app.config.get('DEBUG', False))
