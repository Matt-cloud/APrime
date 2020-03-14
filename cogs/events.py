from imports import * 
from lib import exceptions

import traceback

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.commonErrors = (discord.HTTPException)
        self.ignoredErrors = (commands.CommandNotFound)

        self.bot.loop.create_task(self.meme_finder())
        self.bot.loop.create_task(self.dadjoke_finder())
        self.bot.loop.create_task(self.clean_database())
        self.bot.loop.create_task(self.clean_requested_by())
        self.bot.loop.create_task(self.handle_reminders())

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, 'on_error'):
            return
        
        if isinstance(error, self.ignoredErrors):
            return
        
        if isinstance(error, exceptions.OwnerOnlyCommand):
            p = dict(title="This command can only be used by the bot owner.")
        
        elif isinstance(error, commands.errors.MissingPermissions):
            p = dict(title="Missing Permissions", description=f"You are missing the following permission(s) : `{', '.join([' '.join(x.split('_')).title() for x in error.missing_perms])}`")
        elif isinstance(error, commands.DisabledCommand):
            p = dict(title="This command is currently disabled.")
        elif isinstance(error, self.commonErrors):
            p = dict(title="Common Error", description=f"```{error}```")
        elif isinstance(error, commands.errors.BadArgument):
            p = dict(title="Bad Argument", description=f"{error}")
        else:
            fullTB = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            p = dict(title="Error", description=f"```{fullTB}```")
            await logger.log(fullTB, level="error")

        await ui.embed(self, ctx, color=ui.colors['red'], **p)
    
    async def clean_database(self):
        await logger.log("Database cleaner started")
        while True:
            async for item in db.dadjokes.find({}):
                if item['selftext'].strip() == "":
                    item_id = item['id']
                    await db.dadjokes.delete_one({"id": item_id})

                    await logger.log(f"Deleted dad joke {item_id} for empty punchline.")
            
            async for item in db.memes.find({}):
                if item['url'].startswith("https://v.re"):
                    item_id = item['id']
                    await db.memes.delete_one({"id": item_id})

                    await logger.log(f"Deleted meme {item_id} for being a video.")

            await asyncio.sleep(32400)
    
    async def clean_requested_by(self):
        await logger.log("Requested by cleaner started")
        # PLEASE FUCKING CHECK LOL IT'S POORLY WRITTEN
        while True:
            async for item in db.memes.find({}):

                change = False
                toDelete = []

                if item['requested_by']:
                    for i, r in enumerate(item['requested_by']):
                        if int(time.time()) - r['timestamp'] >= 129600:
                            await logger.log(f"Deleted requested by {r['id']} in meme {item['id']}")
                            del item['requested_by'][i]
                            change = True

                if change:
                    await db.memes.update_one({"id": item['id']}, {"$set": item})
            
            async for item in db.dadjokes.find({}):

                change = False
                toDelete = []

                if item['requested_by']:
                    for i, r in enumerate(item['requested_by']):
                        if int(time.time()) - r['timestamp'] >= 129600:
                            await logger.log(f"Deleted requested by {r['id']} in dadjoke {item['id']}")
                            del item['requested_by'][i]
                            change = True

                if change:
                    await db.dadjokes.update_one({"id": item['id']}, {"$set": item})

            await asyncio.sleep(36000)
    
    async def handle_reminders(self):
        await logger.log("Reminders handler started")
        while True:
            
            async for reminder in db.reminders.find({}):
                if int(time.time()) - reminder['timestamp'] >= reminder['total_seconds']:
                    user = self.bot.get_user(reminder['user'])
                    
                    if user:
                        await ui.embed(self, user, title="Just a friendly reminder.", description=reminder['reminder'])
                        await db.reminders.delete_one({"id": reminder['id']})

            await asyncio.sleep(60)
    
    async def meme_finder(self):
        await logger.log("Meme finder started")
        while True:
            subreddits = await db.config.find_one({"foo": "bar"})
            subreddits = subreddits['meme_subreddits']
            subreddits_string = "+".join(subreddits)

            for post in reddit.subreddit(subreddits_string).hot():
                if not await db.memes.count_documents({"id": post.id}) and not post.url.startswith("https://v.re"):
                    try:
                        data = {
                            "url": post.url,
                            "shortlink": post.shortlink,
                            "title": post.title,
                            "id": post.id,
                            "author": post.author.name,
                            "timestamp": int(time.time()),
                            "nsfw": post.over_18,
                            "requested_by": []
                        }
                        await db.memes.insert_one(data)
                        await logger.log(f"New Meme Added : {data['id']}", level="info")
                    except praw.exceptions.APIException as e:
                        await logger.log("Error with the reddit API", level="error")
                    except AttributeError:
                        pass
                await asyncio.sleep(1.5)

            await asyncio.sleep(1800)
    
    async def dadjoke_finder(self):
        await logger.log("Dad joke finder started")
        while True:
            subreddit = reddit.subreddit("dadjokes")

            for submission in subreddit.hot():
                if not await db.dadjokes.count_documents({"id": submission.id}) and submission.selftext.strip() != "":
                    try:
                        data = {
                            "shortlink": submission.shortlink,
                            "title": submission.title,
                            "selftext": submission.selftext,
                            "author": submission.author.name,
                            "timestamp": int(time.time()),
                            "id": submission.id,
                            "verified": False,
                            "requested_by": []
                        }
                        await db.dadjokes.insert_one(data)
                        await logger.log(f"New Dad Joke Added : {data['id']}", level="info")
                    except praw.exceptions.APIException as e:
                        await logger.log("Error with the reddit API", level="error")
                    except AttributeError:
                        pass

                await asyncio.sleep(1.5)
            await asyncio.sleep(1500)
    
def setup(bot):
    bot.add_cog(Events(bot))
