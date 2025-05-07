# CITS5505 Group Project – The Richverse

This project is built using Flask and provides an interactive dashboard to visualize portfolio returns, benchmarks, and performance metrics.

## 🔧 Requirements

- Python **3.10** or higher (due to modern type hinting syntax). However, python **3.13** is currently not recommended due to compatibility issues with certain dependencies (e.g., setuptools, pkgutil, and others).
- `pip` (latest recommended)
- Virtual environment setup (`venv`)

## 📦 Setup Instructions

```bash
# Clone the repo
git clone https://github.com/YifanG10062/CITS5505_GroupProject.git
cd CITS5505_GroupProject

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate       # On Windows
# source venv/bin/activate   # On Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Initialize the database
flask db upgrade

# Populate historical asset price data
# This will fetch prices from 2015-01-01 to today and inserts it into the database
flask --app run.py refresh-history

# Run the app
python run.py
