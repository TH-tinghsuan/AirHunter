import os
from dotenv import load_dotenv

load_dotenv

class Config(object):
    # Database
    
    DB_HOST = os.environ.get("DB_HOST")
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_DATABASE = os.environ.get("DB_DATABASE")
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_DATABASE}:3306/{DB_DATABASE}"

