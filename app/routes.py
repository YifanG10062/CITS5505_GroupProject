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
        "maxDrawdown": result["max_drawdown"],
        "longestDD": result["longestDD"]        
    }
    return jsonify(summary)

# 2. Time series data for plotting + heatmap
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

    # Monthly returns for heatmap 
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
        
        # Query all assets
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

@auth.route("/login")
def login():
    return render_template("error.html", 
                          code=501, 
                          title="Not Implemented",
                          heading="Feature Not Implemented", 
                          details="User authentication is not yet available.")

@auth.route("/register")
def register():
    return render_template("error.html", 
                          code=501, 
                          title="Not Implemented",
                          heading="Feature Not Implemented", 
                          details="User registration is not yet available.")

@auth.route("/profile")
def profile():
    return render_template("error.html", 
                          code=501, 
                          title="Not Implemented",
                          heading="Feature Not Implemented", 
                          details="User profile is not yet available.")

@auth.route("/settings")
def settings():
    return render_template("error.html", 
                          code=501, 
                          title="Not Implemented",
                          heading="Feature Not Implemented", 
                          details="User settings are not yet available.")

@auth.route("/logout")
def logout():
    return render_template("error.html", 
                          code=501, 
                          title="Not Implemented",
                          heading="Feature Not Implemented", 
                          details="User logout is not yet available.")
# =============================================================================
# END OF TEMPORARY USER AUTHENTICATION MODULE
# =============================================================================
