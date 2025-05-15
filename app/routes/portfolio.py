import json
import sqlite3
import traceback
import os
from datetime import datetime, timedelta 

from flask import Blueprint, redirect, render_template, request, url_for, abort, jsonify, current_app
from flask_login import login_required, current_user

from app.services.calculation import calculate_portfolio_metrics
from app.models.portfolio import PortfolioSummary, PortfolioChangeLog, PortfolioShareLog, PortfolioVersion
from app.models.asset import Price
from app.models.user import User 
from sqlalchemy import func
from app import db  

# Define portfolios blueprint
portfolios = Blueprint("portfolios", __name__, url_prefix="/portfolios")

# Portfolio List View
@portfolios.route("/")
@login_required
def list():
    # Get portfolios for the current user from database (only shown portfolios)
    user_portfolios = PortfolioSummary.query.filter_by(
        user_id=current_user.id, 
        is_shown=True
    ).all()
    
    # Check for recently shared portfolios (within the last 24 hours)
    one_day_ago = datetime.utcnow() - timedelta(hours=24)
    recent_shares = PortfolioSummary.query.filter(
        PortfolioSummary.user_id == current_user.id,
        PortfolioSummary.shared_from_id.isnot(None),
        PortfolioSummary.created_at >= one_day_ago,
        PortfolioSummary.is_shown == True
    ).all()
    
    # Prepare the alert message if there are recent shares
    share_alert = None
    if recent_shares:
        # Get unique sharers' usernames
        sharer_usernames = set(share.creator_username for share in recent_shares)
        portfolio_count = len(recent_shares)
        
        if len(sharer_usernames) == 1:
            # Single sharer
            sharer = next(iter(sharer_usernames))
            if portfolio_count == 1:
                share_alert = f"{sharer} has shared a portfolio with you."
            else:
                share_alert = f"{sharer} has shared {portfolio_count} portfolios with you."
        else:
            # Multiple sharers
            share_alert = f"{len(sharer_usernames)} users have shared {portfolio_count} portfolios with you."
    
    # If user has no portfolios, create a demo portfolio
    if not user_portfolios:
        try:
            print(f"No portfolios found for user {current_user.username}, creating demo portfolio")
            
            # Try different assets combinations in case some don't have price data
            demo_allocations = [
                {"NVDA": 0.5, "BTC-USD": 0.5},  # Original allocation
                {"AAPL": 0.5, "MSFT": 0.5},     # Alternative 1
                {"AAPL": 1.0},                  # Alternative 2 - single asset
            ]
            
            # Try each allocation until one works
            metrics = {}
            successful_allocation = None
            
            for demo_allocation in demo_allocations:
                print(f"Trying allocation: {demo_allocation}")
                # Calculate metrics for demo portfolio
                initial_amount = 1000.0
                start_date = "2015-01-01"
                
                try:
                    # Attempt to calculate metrics with this allocation
                    test_metrics = calculate_portfolio_metrics(
                        allocation=demo_allocation,
                        start_date=start_date,
                        initial_amount=initial_amount
                    )
                    
                    # If metrics has required keys, use this allocation
                    if test_metrics and 'current_value' in test_metrics:
                        print(f"Successfully calculated metrics for {demo_allocation}")
                        metrics = test_metrics
                        successful_allocation = demo_allocation
                        break
                except Exception as calc_error:
                    print(f"Error calculating metrics for {demo_allocation}: {str(calc_error)}")
                    continue
            
            # If no allocation worked, use default values
            if not metrics or 'current_value' not in metrics:
                print("All allocations failed, using default values")
                metrics = {
                    "current_value": initial_amount,
                    "return_percent": 0.0,
                    "cagr": 0.0,
                    "volatility": 0.0,
                    "max_drawdown": 0.0
                }
                successful_allocation = demo_allocations[0]  # Use first allocation as default
            
            # Create a new demo portfolio with successful allocation or defaults
            demo_portfolio = PortfolioSummary(
                portfolio_name=f"PortfolioDemoFor{current_user.username}",
                user_id=current_user.id,
                creator_id=current_user.id,
                allocation_json=json.dumps(successful_allocation),
                current_value=metrics.get('current_value', initial_amount),
                return_percent=metrics.get('return_percent', 0.0),
                cagr=metrics.get('cagr', 0.0),
                volatility=metrics.get('volatility', 0.0),
                max_drawdown=metrics.get('max_drawdown', 0.0),
                created_at=datetime.utcnow(),
                input_updated_at=datetime.utcnow(),
                metric_updated_at=datetime.utcnow(),
                is_shown=True,
                start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
                initial_amount=initial_amount,
                profit=metrics.get('profit', 0.0),
                calculated_at=datetime.strptime(start_date, "%Y-%m-%d").date(),
                is_editable=True,
                is_shareable=True,
                is_deletable=True
            )
            
            # Set user information
            demo_portfolio.user_username = current_user.username
            demo_portfolio.user_email = current_user.user_email
            demo_portfolio.creator_username = current_user.username
            demo_portfolio.creator_email = current_user.user_email
            
            # Save to database
            db.session.add(demo_portfolio)
            db.session.commit()
            
            # Create initial version record
            initial_version = PortfolioVersion(
                portfolio_id=demo_portfolio.portfolio_id,
                version_number=1,  # First version
                updated_by=current_user.id,
                updated_at=datetime.utcnow(),
                allocation_json=json.dumps(successful_allocation),
                portfolio_name=demo_portfolio.portfolio_name,
                start_date=demo_portfolio.start_date,
                initial_amount=initial_amount
            )
            db.session.add(initial_version)
            db.session.commit()
            
            # Get updated portfolio list including the demo (ALSO FILTER BY is_shown=True)
            user_portfolios = PortfolioSummary.query.filter_by(
                user_id=current_user.id,
                is_shown=True
            ).all()
            
        except Exception as e:
            print(f"Error creating demo portfolio: {str(e)}")
            print(traceback.format_exc())
    
    # Convert database objects to dictionaries for template
    portfolios_list = []
    for p in user_portfolios:
        # Convert allocation JSON string to a readable format
        allocation_dict = json.loads(p.allocation_json)
        allocation_str = ", ".join([f"{k}: {int(v*100)}%" for k, v in allocation_dict.items()])
        
        # Get share history for this portfolio
        share_history = []
        if p.creator_id == current_user.id:  # Only get share history for portfolios created by current user
            share_logs = PortfolioShareLog.query.filter_by(from_portfolio_id=p.portfolio_id).all()
            
            for log in share_logs:
                # Get the username of the user this portfolio was shared with
                shared_user = User.query.get(log.to_user_id)
                if shared_user:
                    # Convert UTC time to Perth time (+8 hours) for display
                    perth_time = log.shared_at + timedelta(hours=8)
                    share_history.append({
                        'username': shared_user.username,
                        'shared_at': perth_time.strftime('%d/%m/%Y %H:%M') 
                    })
        
        portfolios_list.append({
            "portfolio_id": p.portfolio_id,
            "portfolio_name": p.portfolio_name,
            "allocation": allocation_str,
            "creator_username": p.creator_username,
            "is_shared": p.shared_from_id is not None,
            "is_editable": p.is_editable and p.creator_id == current_user.id,  
            "is_shareable": p.is_shareable and p.creator_id == current_user.id, 
            "share_history": share_history,  # Add share history to the portfolio object
            "current_value": p.current_value,
            "return_percent": p.return_percent,
            "cagr": p.cagr,
            "volatility": p.volatility,
            "max_drawdown": p.max_drawdown
        })
    
    earliest_date = db.session.query(func.min(Price.date)).scalar()
    latest_date = db.session.query(func.max(Price.date)).scalar()
    return render_template("portfolio/portfolio_list.html", 
                          portfolios=portfolios_list, 
                          earliest_date=earliest_date, 
                          latest_date=latest_date,
                          share_alert=share_alert)

def get_assets():
    """Get assets directly from database without caching"""
    try:
        # Get database path from app config
        db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        
        # Extract SQLite file path from URI
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
        else:
            # If not using SQLite, raise exception
            raise Exception("Only SQLite database is supported for direct connection")
            
        conn = sqlite3.connect(db_path)
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
@login_required
def create():
    try:
        if request.method == "POST":
            # Use the user-provided portfolio name if provided, otherwise will be updated after creation
            portfolio_name = request.form.get("portfolio_name", "")
            
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
                                              error="Invalid allocation values", assets=get_assets())
            
            # Fixed system defaults
            initial_amount = 1000.0
            start_date = "2015-01-01"

            try:
                metrics = calculate_portfolio_metrics(
                    allocation=allocation,
                    start_date=start_date,
                    initial_amount=initial_amount
                )
                
                # Use dictionary get() method with defaults to handle missing keys
                new_portfolio = PortfolioSummary(
                    portfolio_name=portfolio_name or f"Temporary Name",  # Will be updated after ID is assigned
                    user_id=current_user.id,
                    creator_id=current_user.id,
                    allocation_json=json.dumps(allocation),  # Store allocation as JSON
                    current_value=metrics.get('current_value', initial_amount),
                    return_percent=metrics.get('return_percent', 0.0),
                    cagr=metrics.get('cagr', 0.0),
                    volatility=metrics.get('volatility', 0.0),
                    max_drawdown=metrics.get('max_drawdown', 0.0),
                    created_at=datetime.utcnow(),
                    input_updated_at=datetime.utcnow(),
                    metric_updated_at=datetime.utcnow(),
                    is_shown=True,
                    start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
                    initial_amount=initial_amount,
                    profit=metrics.get('profit', 0.0),
                    calculated_at=datetime.strptime(start_date, "%Y-%m-%d").date(),
                    is_editable=True,
                    is_shareable=True,
                    is_deletable=True
                )
                
                # Set user information
                new_portfolio.user_username = current_user.username
                new_portfolio.user_email = current_user.user_email
                new_portfolio.creator_username = current_user.username
                new_portfolio.creator_email = current_user.user_email
                
                # First save to get the portfolio_id
                db.session.add(new_portfolio)
                db.session.flush()
                
                # Now update the name with the portfolio_id if no custom name was provided
                if not portfolio_name:
                    new_portfolio.portfolio_name = f"{current_user.username}'s portfolio{new_portfolio.portfolio_id}"
                
                # Create initial version record
                initial_version = PortfolioVersion(
                    portfolio_id=new_portfolio.portfolio_id,
                    version_number=1,  # First version
                    updated_by=current_user.id,
                    updated_at=datetime.utcnow(),
                    allocation_json=json.dumps(allocation),
                    portfolio_name=new_portfolio.portfolio_name,
                    start_date=new_portfolio.start_date,
                    initial_amount=initial_amount
                )
                db.session.add(initial_version)
                
                # Commit the changes
                db.session.commit()
                
            except Exception as e:
                print(f"Calculation or DB error: {e}")
                print(traceback.format_exc())
                return render_template("portfolio/portfolio_form.html", portfolio=None,
                                       error="Error saving portfolio data", assets=get_assets())

            return redirect(url_for('portfolios.list', portfolio_id=new_portfolio.portfolio_id))

        # For GET request: prepare a suggested portfolio name for the form
        suggested_name = f"{current_user.username}'s portfolio"
        # Get assets from the database
        assets = get_assets()
        return render_template("portfolio/portfolio_form.html", portfolio=None, 
                              error=None, assets=assets, suggested_name=suggested_name)

    except Exception as e:
        # Log the full error with traceback
        print(f"Error in portfolio create route: {str(e)}")
        print(traceback.format_exc())
        return f"Server error: {str(e)}", 500

# Edit Existing Portfolio
@portfolios.route("/<int:portfolio_id>/edit", methods=["GET", "POST"])
def edit(portfolio_id):
    # Retrieve portfolio data from database
    portfolio = PortfolioSummary.query.get_or_404(portfolio_id)
    
    # Check if user has permission to edit this portfolio
    if portfolio.creator_id != current_user.id:
        abort(403, description="You can only edit portfolios you created")
    
    # Load current allocation from JSON
    try:
        current_allocation = json.loads(portfolio.allocation_json)
    except:
        current_allocation = {}
    
    if request.method == "POST":
        # Get the updated portfolio name from the form
        portfolio_name = request.form.get("portfolio_name")
        original_portfolio_name = portfolio.portfolio_name  # Store original name for comparison
        
        # Collect allocation data and convert to the correct format
        allocation = {}
        for key, value in request.form.items():
            if key.startswith('allocation[') and key.endswith(']'):
                asset_code = key[11:-1]
                try:
                    allocation[asset_code] = int(value) / 100.0
                except ValueError:
                    return render_template("portfolio/portfolio_form.html", 
                                          portfolio=portfolio,
                                          current_allocation=current_allocation,
                                          assets=get_assets(),
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
            portfolio.allocation_json = json.dumps(allocation)
            # Use dictionary get() method with original values as defaults
            portfolio.current_value = metrics.get('current_value', portfolio.current_value or initial_amount)
            portfolio.profit = metrics.get('profit', portfolio.profit or 0.0)  # Update profit
            portfolio.return_percent = metrics.get('return_percent', portfolio.return_percent or 0.0)
            portfolio.cagr = metrics.get('cagr', portfolio.cagr or 0.0)
            portfolio.volatility = metrics.get('volatility', portfolio.volatility or 0.0)
            portfolio.max_drawdown = metrics.get('max_drawdown', portfolio.max_drawdown or 0.0)
            portfolio.input_updated_at = datetime.utcnow()
            portfolio.metric_updated_at = datetime.utcnow()  # Update metric_updated_at
            
            # Update user information in case it changed
            portfolio.user_username = current_user.username
            portfolio.user_email = current_user.user_email
            
            # Get the latest version number
            latest_version = db.session.query(func.max(PortfolioVersion.version_number))\
                .filter_by(portfolio_id=portfolio.portfolio_id).scalar() or 0
            
            # Create a new version record
            new_version = PortfolioVersion(
                portfolio_id=portfolio.portfolio_id,
                version_number=latest_version + 1,
                updated_by=current_user.id,
                updated_at=datetime.utcnow(),
                allocation_json=json.dumps(allocation),
                portfolio_name=portfolio_name,
                start_date=portfolio.start_date,
                initial_amount=portfolio.initial_amount
            )
            db.session.add(new_version)
            
            db.session.commit()
            
            # Record change in portfolio history with correct field names
            try:
                # Create a log entry for this change using the correct model fields
                change_log = PortfolioChangeLog(
                    portfolio_id=portfolio.portfolio_id,
                    changed_by=current_user.id,
                    field_changed="allocation", 
                    old_value=json.dumps(current_allocation), 
                    new_value=json.dumps(allocation),
                    timestamp=datetime.utcnow()  
                )
                
                db.session.add(change_log)
                db.session.commit()
                
                if portfolio_name != original_portfolio_name:  # Compare with original name
                    name_change_log = PortfolioChangeLog(
                        portfolio_id=portfolio.portfolio_id,
                        changed_by=current_user.id,
                        field_changed="portfolio_name",
                        old_value=original_portfolio_name,
                        new_value=portfolio_name,
                        timestamp=datetime.utcnow() 
                    )
                    db.session.add(name_change_log)
                    db.session.commit()
                
            except Exception as log_error:
                print(f"Could not record portfolio change: {str(log_error)}")
                # Continue even if logging fails
            
        except Exception as e:
            print(f"Calculation or DB error: {e}")
            print(traceback.format_exc())
            return render_template("portfolio/portfolio_form.html", 
                                  portfolio=portfolio,
                                  current_allocation=current_allocation,
                                  assets=get_assets(),
                                  error="Error calculating or saving portfolio metrics")

        return redirect(url_for('portfolios.list', portfolio_id=portfolio.portfolio_id))
    
    # Fetch assets from the database, excluding 'etf' type
    try:
        # Get database path from app config
        db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        
        # Extract SQLite file path from URI
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
        else:
            # If not using SQLite, raise exception
            raise Exception("Only SQLite database is supported for direct connection")
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT asset_code, display_name, full_name, logo_url 
            FROM assets
            WHERE type != 'etf'  -- Exclude 'etf' assets
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
    
    # Show edit form for GET request with current portfolio data
    return render_template("portfolio/portfolio_form.html", 
                          portfolio=portfolio,
                          current_allocation=current_allocation, 
                          assets=assets)

# Delete Portfolio (Soft Delete)
@portfolios.route("/<int:portfolio_id>/delete", methods=["POST"])
@login_required
def delete(portfolio_id):
    # Get the portfolio by ID
    portfolio = PortfolioSummary.query.get_or_404(portfolio_id)
    
    # Check if user has permission to delete
    if portfolio.user_id != current_user.id:
        abort(403, description="You don't have permission to delete this portfolio")
    
    try:
        # Soft delete by setting is_shown to False
        portfolio.is_shown = False
        
        # Record the change in log - removing invalid fields
        change_log = PortfolioChangeLog(
            portfolio_id=portfolio.portfolio_id,
            changed_by=current_user.id,
            field_changed="visibility",
            old_value="visible",
            new_value="hidden",
            timestamp=datetime.utcnow()  
        )
        
        db.session.add(change_log)
        db.session.commit()
        
        return jsonify({"success": True, "message": "Portfolio deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting portfolio: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "message": "Failed to delete portfolio"}), 500

# API to get user list for sharing
@portfolios.route("/api/users", methods=["GET"])
@login_required
def get_users():
    """API endpoint to fetch all users except the current user"""
    # Query all users except the current user
    users = User.query.filter(User.id != current_user.id).all()
    
    # Format user data for response
    user_list = [
        {
            "id": user.id,
            "username": user.username
        }
        for user in users
    ]
    
    return jsonify({"users": user_list})

# API to share a portfolio
@portfolios.route("/api/portfolios/share", methods=["POST"])
@login_required
def share_portfolio():
    """API endpoint to share a portfolio with selected users"""
    data = request.json
    
    # Validate request data
    if not data or "portfolio_id" not in data or "user_ids" not in data:
        return jsonify({"error": "Invalid request data"}), 400
    
    portfolio_id = data["portfolio_id"]
    user_ids = data["user_ids"]
    
    # Validate the portfolio exists and belongs to the current user
    portfolio = PortfolioSummary.query.filter_by(
        portfolio_id=portfolio_id,
        user_id=current_user.id
    ).first()
    
    if not portfolio:
        return jsonify({"error": "Portfolio not found or not owned by you"}), 404
    
    # Ensure the portfolio is shareable
    if not portfolio.is_shareable:
        return jsonify({"error": "This portfolio cannot be shared"}), 403
    
    shared_with = []
    for user_id in user_ids:
        # Validate the target user exists
        target_user = User.query.get(user_id)
        if not target_user:
            continue
        
        # Create a new portfolio for the target user
        shared_portfolio = PortfolioSummary(
            portfolio_name=f"{portfolio.portfolio_name} (Shared by {current_user.username})",
            user_id=target_user.id,
            creator_id=current_user.id,
            shared_from_id=current_user.id,
            allocation_json=portfolio.allocation_json,
            start_date=portfolio.start_date,
            initial_amount=portfolio.initial_amount,
            current_value=portfolio.current_value,
            profit=portfolio.profit,
            return_percent=portfolio.return_percent,
            cagr=portfolio.cagr,
            volatility=portfolio.volatility,
            max_drawdown=portfolio.max_drawdown,
            created_at=datetime.utcnow(),
            input_updated_at=datetime.utcnow(),
            metric_updated_at=datetime.utcnow(),
            is_editable=False,  # Shared portfolios are read-only
            is_shareable=False,  # Shared portfolios cannot be shared further
            is_deletable=False   # Shared portfolios cannot be deleted
        )
        
        # Update user information for the shared portfolio
        shared_portfolio.user_username = target_user.username
        shared_portfolio.user_email = target_user.user_email
        shared_portfolio.creator_username = current_user.username
        shared_portfolio.creator_email = current_user.user_email
        
        db.session.add(shared_portfolio)
        db.session.flush()  # Flush to get the new portfolio ID
        
        # Record the share in the PortfolioShareLog
        share_log = PortfolioShareLog(
            from_user_id=current_user.id,
            to_user_id=target_user.id,
            from_portfolio_id=portfolio.portfolio_id,
            to_portfolio_id=shared_portfolio.portfolio_id,
            shared_at=datetime.utcnow()
        )
        db.session.add(share_log)
        
        # Create initial version for shared portfolio
        shared_version = PortfolioVersion(
            portfolio_id=shared_portfolio.portfolio_id,
            version_number=1,  
            updated_by=current_user.id,
            updated_at=datetime.utcnow(),
            allocation_json=portfolio.allocation_json,
            portfolio_name=shared_portfolio.portfolio_name,
            start_date=shared_portfolio.start_date,
            initial_amount=shared_portfolio.initial_amount
        )
        db.session.add(shared_version)
        
        shared_with.append(target_user.username)
    
    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": f"Portfolio shared with {len(shared_with)} users",
            "shared_with": shared_with
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error sharing portfolio: {str(e)}")
        return jsonify({"error": "Failed to share portfolio"}), 500
