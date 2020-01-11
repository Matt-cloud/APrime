from imports import * 
from lib import exceptions

import traceback

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.commonErrors = (discord.HTTPException)
        self.ignoredErrors = (commands.CommandNotFound)
    
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
    
def setup(bot):
    bot.add_cog(Events(bot))
