from pymongo import MongoClient 
from lib import logger as _logger

import json 
import os
import praw

with open(os.path.join(os.getcwd(), "data", "config.json"), "rb") as f:
    config = json.load(f)

redditConfig = config['apis']['reddit']
client = MongoClient(f"mongodb+srv://{config['database']['user']}:{config['database']['password']}@aprime-tnuy3.mongodb.net/test?retryWrites=true&w=majority")
db = client.aprime
logger = _logger.Logger(loggingFile=os.path.join(os.getcwd(), "data", "main.log"), database=db)
reddit = praw.Reddit(
    client_id=redditConfig['client_id'],
    client_secret=redditConfig['client_secret'],
    user_agent=redditConfig['user_agent'],
    username=redditConfig['username'],
    password=redditConfig['password']
)
