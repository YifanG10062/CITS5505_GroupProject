import click
from flask.cli import with_appcontext

@click.command('refresh-user-info')
@with_appcontext
def refresh_user_info_command():
    """Refresh all user information in portfolio summaries."""
    # Move imports inside the function to avoid circular imports
    from app import db
    from app.models.portfolio import PortfolioSummary
    
    portfolios = PortfolioSummary.query.all()
    updated_count = 0
    
    for portfolio in portfolios:
        portfolio.update_user_info()
        updated_count += 1
    
    db.session.commit()
    click.echo(f"Updated user information for {updated_count} portfolios.")
