from flask import Flask
from config import Config
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from dash import Dash

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app) 


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from server.controllers import search_controller, user_controller
from server import dashboard