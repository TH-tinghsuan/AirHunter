import os
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    JSON_SORT_KEYS = False
    JSON_AS_ASCII = False
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    # Database
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.environ.get('DB_USERNAME')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:3306/{os.environ.get('DB_DATABASE')}"
    DB_HOST = os.environ.get('DB_HOST')
    DB_USERNAME = os.environ.get('DB_USERNAME')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_DATABASE = os.environ.get('DB_DATABASE')

