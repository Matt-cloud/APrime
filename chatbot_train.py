from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

import os, json 

config = os.path.join(os.getcwd(), "data", "config.json")
trainingFile = os.path.join(os.getcwd(), "data", "Chatbot Training Data", "train.txt")

with open(config) as f:
    r = json.load(f)
    uri = r['database']['connection_string']

bot = ChatBot(
    "Dimitri",
    storage_adapter="chatterbot.storage.MongoDatabaseAdapter",
    database_uri=uri,
    logic_adapters=[
        'chatterbot.logic.BestMatch'
    ]
)

trainer = ListTrainer(bot)

with open(trainingFile, "r", encoding="utf-8") as f:
    statements = [line.strip() for line in f if line.strip() != ""] # It's probably not efficient to put everything in train.txt into a list but whatever

trainer.train(statements)
