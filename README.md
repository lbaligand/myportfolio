# MyPortfolio
Dashboard to visualize and analyze personal financial stock portfolio. Currently it only has a connector with Degiro broker.

The app is built using Dash (plotly) with Yahoo Finance historical data.

- Yahoo Finance API: https://github.com/ranaroussi/yfinance
- Degiro unofficial API: https://github.com/lolokraus/DegiroAPI

## Getting started
1. Launch a SQL DB (by default in `processed/master_portfolio.db`)
2. Create `degiro_creds.json` with your credentials (do not share!)
3. Install requirements: `pip install -r requirements.txt`
4. Run the app: `python dash_app/index.py`
