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
            logic_adapters=[
                'chatterbot.logic.BestMatch'
            ]
        )
        self.cooldowns = {}
        self.cooldownLimit = 2 # You have to wait for 5 seconds before chatting with the chatbot again
    
    async def getResponse(self, content):
        return self.chatbot.get_response(content)
    
    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return # Ignore all bots

        if message.guild:

            channel_id, guild_id = message.channel.id, message.guild.id # ??? why
            server_prefix = await bot.getPrefix(message.guild, db)
            
            if message.content == "" or message.content is None:
                return # Ignore empty messages
            
            if message.content.startswith(server_prefix):
                return

            if await db.chatbots.count_documents({"guild_id": guild_id, "channel_id": channel_id}):

                if message.guild.id in self.cooldowns: # Cooldown per guild
                    stamp = self.cooldowns[message.guild.id]
                    if int(time.time()) - stamp < self.cooldownLimit:
                        waitingTime = self.cooldownLimit - (int(time.time()) - stamp)
                        s = ""

                        if waitingTime > 1:
                            s = "s"

                        return await message.channel.send(f"Please wait `{waitingTime} second{s}` before chatting with me again.")
                    self.cooldowns.pop(message.guild.id)
                else:
                    self.cooldowns[message.guild.id] = int(time.time())

                content = message.content
                response = await self.bot.loop.create_task(self.getResponse(content))
                
                await message.channel.send(response)
    
def setup(bot):
    bot.add_cog(ChatBotHandler(bot))
