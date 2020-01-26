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
            logger.log(fullTB, level="error")

        await ui.embed(self, ctx, color=ui.colors['red'], **p)
    
    async def clean_database(self):
        while True:
            for item in db.dadjokes.find({}):
                pass 

            await asyncio.sleep(100)
    
    async def meme_finder(self):
        while True:
            subreddits = db.config.find_one({"foo": "bar"})['meme_subreddits']
            subreddits_string = "+".join(subreddits)

            for post in reddit.subreddit(subreddits_string).hot():
                if not db.memes.count_documents({"id": post.id}) and not post.url.startswith("https://v.re"):
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
                        db.memes.insert_one(data)
                        logger.log(f"New Meme Added : {data['id']}", level="info")
                    except praw.exceptions.APIException as e:
                        logger.log("Error with the reddit API", level="error")
                    except AttributeError:
                        pass
                await asyncio.sleep(1.5)

            await asyncio.sleep(5)
    
    async def dadjoke_finder(self):
        while True:
            subreddit = reddit.subreddit("dadjokes")

            for submission in subreddit.hot():
                if not db.dadjokes.count_documents({"id": submission.id}) and submission.selftext != "":
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
                        db.dadjokes.insert_one(data)
                        logger.log(f"New Dad Joke Added : {data['id']}", level="info")
                    except praw.exceptions.APIException as e:
                        logger.log("Error with the reddit API", level="error")
                    except AttributeError:
                        pass

                await asyncio.sleep(1.5)
            await asyncio.sleep(5)
    
def setup(bot):
    bot.add_cog(Events(bot))
