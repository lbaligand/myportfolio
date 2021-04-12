# MyPortfolio
Dashboard to visualize and analyze personal financial stock portfolio. Currently it only has a connector with Degiro broker.

The app is built using Dash (plotly) with Yahoo Finance historical data.

- Yahoo Finance API: https://github.com/ranaroussi/yfinance
- Degiro unofficial API: https://github.com/lolokraus/DegiroAPI

## Getting started
1. Launch a SQL DB of any type but supported by SQLAlchemy
2. Modify `DB_PATH` in `dash_app/config.py`
3. Create `degiro_creds.json` with your credentials (do not share!)
4. Install requirements: `pip install -r requirements.txt`
5. Run the app: `python dash_app/index.py`

## Next steps
- [ ] Industry breakdown
- [ ] Dividend tab history and projected
