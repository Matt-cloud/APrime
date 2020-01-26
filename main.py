from pathlib import Path
from discord.ext import commands
from termcolor import colored 
from lib.utils.globals import db, logger
from lib.utils import bot

import asyncio
import datetime
import json
import discord
import os

def config_load():
    configPath = os.path.join(os.getcwd(), "data", "config.json")
    with open(configPath) as doc:
        data =  json.load(doc)
    return data


async def run():
    """
    Where the bot gets started. If you wanted to create an database connection pool or other session for the bot to use,
    it's recommended that you create it here and pass it to the bot as a kwarg.
    """

    config = config_load()
    bot = Bot(config=config,
              description=config['description'])
    try:
        await bot.start(config['token'])
    except KeyboardInterrupt:
        exit() # well it's faster


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=self.get_prefix_,
            description=kwargs.pop('description')
        )
        self.start_time = None
        self.app_info = None

        self.config = kwargs.pop('config')

        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())

    async def track_start(self):
        await self.wait_until_ready()
        self.start_time = datetime.datetime.utcnow()

    async def get_prefix_(self, bot_, message):
        prefix = bot.getPrefix(message.guild, db, asList=True)
        return commands.when_mentioned_or(*prefix)(bot_, message)

    async def load_all_extensions(self):
        await self.wait_until_ready()
        await asyncio.sleep(1)

        cogs = [x.stem for x in Path('cogs').glob('*.py')]

        for extension in cogs:

            try:
                self.load_extension(f'cogs.{extension}')
                logger.log(f"Extension : {extension} is loaded")
            except Exception as e:
                logger.log(f"Failed to load extension : {extension}")


    async def on_ready(self):
        self.remove_command("help")
        self.app_info = await self.application_info()
        x = self.app_info

        customPrefixes = db.prefixes.count_documents({})
        savedMemes = db.memes.count_documents({})

        ui = f"""
# Discord.py Version : {discord.__version__}
# Name : {x.name}
# ID : {x.id}
# Owner : {x.owner}
# Default Prefix : {self.config['prefix']}
# {customPrefixes} custom prefix{'s' if customPrefixes > 1 else ''}
# {savedMemes} saved meme{'s' if savedMemes > 1 else ''}
"""
        logger.log(ui)

    async def on_message(self, message):
        if message.author.bot:
            return  # ignore all bots

        await self.process_commands(message)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
