from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

import os, json 

config = os.path.join(os.getcwd(), os.pardir, "data", "config.json")

with open(config) as f:
    r = json.load(f)
    uri = r['database']['connection_string']

bot = ChatBot(
    "Dimitri",
    storage_adapter="chatterbot.storage.MongoDatabaseAdapter",
    database_uri=uri,
    logic_adapters=[
        'chatterbot.logic.TimeLogicAdapter',
        'chatterbot.logic.MathematicalEvaluation',
        'chatterbot.logic.BestMatch'
    ]
)

trainer = ChatterBotCorpusTrainer(bot)

trainer.train(
    "chatterbot.corpus.english" 
)
