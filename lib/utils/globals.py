from pymongo import MongoClient 
from lib import logger as _logger

import json 
import os

with open(os.path.join(os.getcwd(), "data", "config.json"), "rb") as f:
    config = json.load(f)

client = MongoClient(f"mongodb+srv://{config['database']['user']}:{config['database']['password']}@aprime-tnuy3.mongodb.net/test?retryWrites=true&w=majority")
db = client.aprime
logger = _logger.Logger(loggingFile=os.path.join(os.getcwd(), "data", "main.log"), database=db)
