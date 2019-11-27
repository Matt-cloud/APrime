from discord.ext import commands
from lib import exceptions

import os 
import json

configFile = os.path.join(os.getcwd(), "data", "config.json")

with open(configFile, "rb") as f:
    config = json.load(f)

def is_owner():
    async def predicate(ctx):
        if ctx.author.id in config['owners']:
            return True 
        raise exceptions.OwnerOnlyCommand
    return commands.check(predicate)
