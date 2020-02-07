from chatterbot import ChatBot

import os, json 

config = os.path.join(os.getcwd(), os.pardir, "data", "config.json")

with open(config) as f:
    r = json.load(f)
    uri = r['database']['connection_string'].replace("/test", "/aprime")

bot = ChatBot(
    "Dimitri",
    storage_adapter="chatterbot.storage.MongoDatabaseAdapter",
    database_uri=uri,
    logic_adapters=[
        'chatterbot.logic.BestMatch'
    ]
)

while True:
    try:
        response = bot.get_response(input("You: "))
        print(response)
    except KeyboardInterrupt:
        quit()
