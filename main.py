from pathlib import Path
from discord.ext import commands
from termcolor import colored 

import asyncio
import datetime
import json
import discord
import lib
import os

def config_load():
    configPath = os.path.join(os.getcwd(), "data", "config.json")
    with open(configPath, "rb") as doc:
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
        await bot.logout()


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=self.get_prefix_,
            description=kwargs.pop('description')
        )
        self.start_time = None
        self.app_info = None

        self.config = kwargs.pop('config')
        self.logger = lib.logger.Logger(loggingFile=os.path.join(os.getcwd(), "app.log"))

        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())

    async def track_start(self):
        await self.wait_until_ready()
        self.start_time = datetime.datetime.utcnow()

    async def get_prefix_(self, bot, message):
        prefix = [self.config["prefix"]]
        return commands.when_mentioned_or(*prefix)(bot, message)

    async def load_all_extensions(self):
        await self.wait_until_ready()
        await asyncio.sleep(1)

        cogs = [x.stem for x in Path('cogs').glob('*.py')]

        for extension in cogs:

            try:
                self.load_extension(f'cogs.{extension}')
                print(f'loaded {extension}')
            except Exception as e:
                error = f'{extension}\n {type(e).__name__} : {e}'
                print(f'failed to load extension {error}')

            print('-' * 10)

    async def on_ready(self):
        self.app_info = await self.application_info()

        print('-' * 10)

        

        print('-' * 10)

    async def on_message(self, message):
        if message.author.bot:
            return  # ignore all bots

        await self.process_commands(message)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
