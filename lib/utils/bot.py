import json 
import os

configFile = os.path.join(os.getcwd(), "data", "config.json")

with open(configFile) as f:
    config = json.load(f)

def getDefaultPrefix():
    return config['prefix']

async def getPrefix(guild, db, asList=False):

    if not guild:
        return getDefaultPrefix()

    prefixes = []
    prefixData = await db.prefixes.find_one({"guild_id": guild.id})

    if prefixData:
        cPrefix = prefixData['prefix']

        if not asList:
            return cPrefix

        prefixes.append(cPrefix)
    
    defaultPrefix = getDefaultPrefix()

    if not asList:
        return defaultPrefix
    
    if prefixData:
        if not prefixData['allow_default_prefix']:
            return prefixes 
    
    prefixes.append(defaultPrefix)
    return prefixes
    