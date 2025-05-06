import json
import sqlite3
import traceback
from datetime import datetime  # Add datetime import

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from app.calculation import calculate_portfolio_metrics
from app.models.portfolio import PortfolioSummary  # Fix the import path
from app import db  # Import db from app

# Define portfolios blueprint
portfolios = Blueprint("portfolios", __name__, url_prefix="/portfolios")

# Portfolio List View
@portfolios.route("/")
@login_required
def list():
    # Mock portfolio data for testing the UI
    portfolios_list = [
        {
            "portfolio_id": 1,
            "portfolio_name": "Diversified Growth",
            "allocation": "AAPL: 30%, NVDA: 30%, BTC-USD: 40%",
            "creator_username": "johndoe",
            "is_shared": True,
            "is_editable": True,
            "is_shareable": True,
            "current_value": 14689.75,
            "return_percent": 0.4689,
            "cagr": 0.1586,
            "volatility": 0.2782,
            "max_drawdown": 0.3578
        },
        {
            "portfolio_id": 2,
            "portfolio_name": "Tech Focus",
            "allocation": "MSFT: 35%, AAPL: 35%, AMZN: 30%",
            "creator_username": "johndoe",
            "is_shared": False,
            "is_editable": True,
            "is_shareable": True,
            "current_value": 12879.24,
            "return_percent": 0.2879,
            "cagr": 0.1214,
            "volatility": 0.2215,
            "max_drawdown": 0.2843
        },
        {
            "portfolio_id": 3,
            "portfolio_name": "Crypto Mix",
            "allocation": "BTC-USD: 50%, ETH-USD: 50%",
            "creator_username": "janedoe",
            "is_shared": True,
            "is_editable": False,
            "is_shareable": False,
            "current_value": 18753.62,
            "return_percent": 0.8753,
            "cagr": 0.2489,
            "volatility": 0.4928,
            "max_drawdown": 0.5682
        }
    ]
    return render_template("portfolio/portfolio_list.html", portfolios=portfolios_list)

def get_assets():
    """Get assets directly from database without caching"""
    try:
        conn = sqlite3.connect('db/portfolio_data.db')
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assets'")
        if not cursor.fetchone():
            print("Error: 'assets' table does not exist in the database")
            conn.close()
            return []

        cursor.execute("""
            SELECT asset_code, display_name, full_name, logo_url 
            FROM assets
            WHERE type != 'etf'
        """)
        
        assets = []
        for row in cursor.fetchall():
            assets.append({
                'code': row[0],
                'name': row[1],
                'company': row[2],
                'logo_url': row[3]
            })

        conn.close()
        return assets

    except Exception as db_error:
        print(f"Database error when fetching assets: {str(db_error)}")
        print(traceback.format_exc())
        return []

# Create New Portfolio
@portfolios.route("/new", methods=["GET", "POST"])
def create():
    try:
        if request.method == "POST":
            portfolio_name = request.form.get("portfolio_name")
            
            # Collect allocation data and convert to the correct format
            allocation = {}
            for key, value in request.form.items():
                if key.startswith('allocation[') and key.endswith(']'):
                    asset_code = key[11:-1]  # Extract asset_code
                    try:
                        allocation[asset_code] = int(value) / 100.0
                    except ValueError:
                        # Return error message
                        return render_template("portfolio/portfolio_form.html", portfolio=None, 
                                              error="Invalid allocation values")
            
            # Fixed system defaults
            initial_amount = 1000.0
            start_date = "2015-01-01"

            try:
                metrics = calculate_portfolio_metrics(
                    allocation=allocation,
                    start_date=start_date,
                    initial_amount=initial_amount
                )
                
                # Create a new portfolio entry in the database
                new_portfolio = PortfolioSummary(
                    portfolio_name=portfolio_name,
                    user_id=current_user.id,
                    creator_id=current_user.id,
                    allocation_json=json.dumps(allocation),  # Store allocation as JSON
                    # Set other fields from metrics calculation
                    total_contributions=initial_amount,
                    current_value=metrics['final_value'],
                    return_percent=metrics['return_percent'],
                    cagr=metrics['cagr'],
                    volatility=metrics['volatility'],
                    max_drawdown=metrics['max_drawdown'],
                    input_created_at=datetime.utcnow(),
                    input_updated_at=datetime.utcnow()
                )
                
                # Set user information
                new_portfolio.user_username = current_user.username
                new_portfolio.user_email = current_user.user_email
                new_portfolio.creator_username = current_user.username
                new_portfolio.creator_email = current_user.user_email
                
                db.session.add(new_portfolio)
                db.session.commit()
                
            except Exception as e:
                print(f"Calculation or DB error: {e}")
                return render_template("portfolio/portfolio_form.html", portfolio=None,
                                       error="Error saving portfolio data")

            return redirect(url_for('dashboard.show', portfolio_id=new_portfolio.portfolio_id))

        # Get assets from the database
        assets = get_assets()
        return render_template("portfolio/portfolio_form.html", portfolio=None, error=None, assets=assets)

    except Exception as e:
        # Log the full error with traceback
        print(f"Error in portfolio create route: {str(e)}")
        print(traceback.format_exc())
        return f"Server error: {str(e)}", 500

# Edit Existing Portfolio
@portfolios.route("/<int:portfolio_id>/edit", methods=["GET", "POST"])
def edit(portfolio_id):
    # TODO: Retrieve portfolio data from database
    portfolio = None  # This should be a query result from database
    
    if request.method == "POST":
        portfolio_name = request.form.get("portfolio_name")
        
        # Collect allocation data and convert to the correct format
        allocation = {}
        for key, value in request.form.items():
            if key.startswith('allocation[') and key.endswith(']'):
                asset_code = key[11:-1]
                try:
                    allocation[asset_code] = int(value) / 100.0
                except ValueError:
                    return render_template("portfolio/portfolio_form.html", portfolio=portfolio,
                                           error="Invalid allocation values")

        initial_amount = 1000.0
        start_date = "2015-01-01"

        try:
            metrics = calculate_portfolio_metrics(
                allocation=allocation,
                start_date=start_date,
                initial_amount=initial_amount
            )
            
            # Update the existing portfolio in the database
            portfolio.portfolio_name = portfolio_name
            portfolio.allocation_json = json.dumps(allocation)  # Update allocation JSON
            # Update metrics fields
            portfolio.current_value = metrics['final_value']
            portfolio.return_percent = metrics['return_percent']
            portfolio.cagr = metrics['cagr']
            portfolio.volatility = metrics['volatility']
            portfolio.max_drawdown = metrics['max_drawdown']
            portfolio.input_updated_at = datetime.utcnow()  # Update timestamp
            
            # Update user information in case it changed
            portfolio.user_username = current_user.username
            portfolio.user_email = current_user.user_email
            
            db.session.commit()
            
            # TODO: Record changes in PortfolioVersion and PortfolioChangeLog tables
            
        except Exception as e:
            print(f"Calculation or DB error: {e}")
            return render_template("portfolio/portfolio_form.html", portfolio=portfolio,
                                   error="Error calculating or saving portfolio metrics")

        return redirect(url_for('portfolios.list'))
        
    # Fetch assets from database
    try:
        conn = sqlite3.connect('db/portfolio_data.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT asset_code, display_name, full_name, logo_url 
            FROM assets
            ORDER BY display_name
        """)
        assets = []
        for row in cursor.fetchall():
            assets.append({
                'code': row[0],
                'name': row[1],
                'company': row[2],
                'logo_url': row[3]
            })

        conn.close()
    except Exception as db_error:
        print(f"Database error when fetching assets: {str(db_error)}")
        assets = []
    
    # Show edit form for GET request
    return render_template("portfolio/portfolio_form.html", portfolio=portfolio, assets=assets)

