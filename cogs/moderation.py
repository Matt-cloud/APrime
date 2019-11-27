from imports import *

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def change_server_prefix(self, ctx, *, new_prefix: str = None):
        pass

# TODO : Show the command category when doing --help
# TODO : Command category must be written in the "help" parameter of @commands.command(help="category: general") Just parse it.
# TODO : --help <category_name>
# TODO : Test properUsage() function
# TODO : Add checks for moderation commands 

def setup(bot):
    bot.add_cog(Moderation(bot))
