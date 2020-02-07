from imports import *

config = os.path.join(os.getcwd(), "data", "config.json")

with open(config) as f:
    config = json.load(f)
    uri = config['database']['connection_string']

class ChatBotHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chatbot = ChatBot(
            "Dimitri",
            storage_adapter="chatterbot.storage.MongoDatabaseAdapter",
            database_uri=uri,
            logic_adapters=[
                'chatterbot.logic.BestMatch'
            ]
        )
    
    async def getResponse(self, content):
        return self.chatbot.get_response(content)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        channel_id, guild_id = message.channel.id, message.guild.id

        if message.author.bot:
            return # Ignore all bots
        
        if message.content == "" or message.content is None:
            return # Ignore empty messages

        if db.chatbots.count_documents({"guild_id": guild_id, "channel_id": channel_id}):
            content = message.content
            response = await self.bot.loop.create_task(self.getResponse(content))
            
            await message.channel.send(response)
    
def setup(bot):
    bot.add_cog(ChatBotHandler(bot))
