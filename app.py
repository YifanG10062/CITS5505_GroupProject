from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("dashboard.html")

@app.route("/api/cumulative")
def cumulative():
    return jsonify({
        "labels": ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"],
        "strategy": [0, 50, 130, 300, 420, 600, 700, 800, 850, 900, 1100],
        "benchmark": [0, 20, 40, 60, 90, 110, 130, 150, 180, 190, 200]
    })
@app.route("/api/stats")
def stats():
    return jsonify({
        "netWorth": 120000,
        "profit": 119000,
        "cumulativeReturn": 1100,
        "cagr": 33.9,
        "volatility": 37.32,
        "maxDrawdown": -53.62
    })
@app.route("/api/portfolio-summary")
def portfolio_summary():
    return jsonify({
        "netWorth": 120000,
        "initial": 1000,
        "profit": 119000,
        "cumulativeReturn": 1100,
        "cagr": 33.9,
        "volatility": 37.32,
        "maxDrawdown": -53.62,
        "longestDD": 532
    })


if __name__ == "__main__":
    app.run(debug=True)
