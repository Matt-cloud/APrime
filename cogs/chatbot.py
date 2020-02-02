from imports import *

class ChatBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        pass
    
def setup(bot):
    bot.add_cog(ChatBot(bot))
