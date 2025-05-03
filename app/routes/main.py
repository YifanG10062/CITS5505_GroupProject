from flask import Blueprint, render_template, redirect, url_for

# Define main blueprint and portfolios blueprint
main = Blueprint("main", __name__)
portfolios = Blueprint("portfolios", __name__, url_prefix="/portfolios")

@main.route("/")
def home():
    return redirect(url_for('portfolios.list'))

@portfolios.route("/")
def list():
    return render_template("portfolio_list.html")