from flask import Flask
import dash

server = Flask(__name__)

app = dash.Dash(server=server,
                suppress_callback_exceptions=False,
                assets_url_path='assets',
                assets_folder='assets')

app.title = 'MyPortfolio'
