import traceback
import pandas as pd
import sqlite3
import time
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app, flash, g
from app.calculation import calculate_portfolio_metrics, get_portfolio_timeseries, get_spy_cumulative_returns

# Define main blueprint and portfolios blueprint
main = Blueprint("main", __name__)
portfolios = Blueprint("portfolios", __name__, url_prefix="/portfolios")

@main.route("/")
def home():
    return render_template("dashboard.html")

# Portfolio List View
@portfolios.route("/")
def list():
    # TODO: Retrieve portfolio data from database
    portfolios_list = []
    return render_template("portfolio/portfolio_list.html", portfolios=portfolios_list)

def get_assets():
    """Get assets directly from database without caching"""
    try:
        # Connect to portfolio database with correct path in db folder
        conn = sqlite3.connect('db/portfolio_data.db')
        cursor = conn.cursor()
        
        # First check if the assets table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assets'")
        if not cursor.fetchone():
            print("Error: 'assets' table does not exist in the database")
            conn.close()
            return []
        
        # Query all assets except those with type='eft'
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
                        # Convert percentage (e.g., 60) to decimal (e.g., 0.6)
                        allocation[asset_code] = int(value) / 100.0
                    except ValueError:
                        # Return error message
                        return render_template("portfolio/portfolio_form.html", portfolio=None, 
                                              error="Invalid allocation values")
            
            # Fixed system defaults
            initial_amount = 1000.0
            start_date = "2015-01-01"

            # Calculate metrics using the allocation dictionary
            try:
                metrics = calculate_portfolio_metrics(
                    allocation=allocation,  # Now correctly formatted as {"AAPL": 0.6, "TSLA": 0.4}
                    start_date=start_date,
                    initial_amount=initial_amount
                )
                
                # TODO: Create a new portfolio entry in the database with:
                # - portfolio_name
                # - user_id (current user)
                # - allocation_json (store the JSON representation of the allocation dict)
                # - metrics values from the calculation result
                
            except Exception as e:
                # Handle calculation errors
                print(f"Calculation error: {e}")
                return render_template("portfolio/portfolio_form.html", portfolio=None, 
                                      error="Error calculating portfolio metrics")
            
            return redirect(url_for('portfolios.list'))
        
        # Get assets directly from database
        assets = get_assets()
        
        # Render form with assets data
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
                asset_code = key[11:-1]  # Extract asset_code
                try:
                    # Convert percentage (e.g., 60) to decimal (e.g., 0.6)
                    allocation[asset_code] = int(value) / 100.0
                except ValueError:
                    # Return error message
                    return render_template("portfolio/portfolio_form.html", portfolio=portfolio, 
                                          error="Invalid allocation values")
        
        # Fixed system defaults
        initial_amount = 1000.0
        start_date = "2015-01-01"

        # Calculate metrics using the allocation dictionary
        try:
            metrics = calculate_portfolio_metrics(
                allocation=allocation,
                start_date=start_date,
                initial_amount=initial_amount
            )
            
            # TODO: Update the existing portfolio in the database with:
            # - Updated portfolio_name
            # - New allocation_json (store the JSON representation of the allocation dict)
            # - Updated metrics values from the calculation result
            # - Update input_updated_at timestamp
            
            # TODO: Record changes in PortfolioVersion and PortfolioChangeLog tables
            
        except Exception as e:
            # Handle calculation errors
            print(f"Calculation error: {e}")
            return render_template("portfolio/portfolio_form.html", portfolio=portfolio, 
                                  error="Error calculating portfolio metrics")
        
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

# =============================================================================
# TEMPORARY USER AUTHENTICATION MODULE - TO BE REPLACED
# =============================================================================
# WARNING: This is a placeholder implementation that will be removed once 
# the proper user management module is implemented.
# It provides minimal routing to prevent template errors with current_user.
# =============================================================================
auth = Blueprint("auth", __name__, url_prefix="/auth")

@auth.route("/account")
def account():
    return render_template("error.html", 
                          code=501, 
                          title="Not Implemented",
                          heading="Feature Not Implemented", 
                          details="User account is not yet available.")

# =============================================================================
# END OF TEMPORARY USER AUTHENTICATION MODULE
# =============================================================================
