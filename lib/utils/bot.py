import os 
import json 

configFile = os.path.join(os.getcwd(), "data", "config.json")

with open(configFile) as f:
    config = json.load(f)

def getPrefix():
    return config['prefix']
    