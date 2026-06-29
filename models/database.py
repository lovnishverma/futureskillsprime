import os
from pymongo import MongoClient

# Database client will be initialized globally but configured in app.py
mongo_client = None
db_client = None
nominations_col = None
config_col = None

def init_db(app):
    global mongo_client, db_client, nominations_col, config_col
    mongo_client = MongoClient(app.config["MONGO_URI"])
    db_client = mongo_client["nielit_db"]
    nominations_col = db_client["nominations"]
    config_col = db_client["config"]
    nominations_col.create_index("token", unique=True)

def get_db():
    return nominations_col

def get_config_col():
    return config_col
