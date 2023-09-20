from flask import Flask
#from config import Config
import pymysql.cursors
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
#app.config.from_object(Config)
app.config['JSON_SORT_KEYS'] = False
app.config['JSON_AS_ASCII'] = False


#connect to mysql
connection = pymysql.connect(host=os.environ.get("DB_HOST"),
                             user=os.environ.get("DB_USERNAME"),
                             password=os.environ.get("DB_PASSWORD"),
                             database=os.environ.get("DB_DATABASE"),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

#create mysql cusor
cursor = connection.cursor()
connection.ping(reconnect=True)

from server.controllers import search_controller