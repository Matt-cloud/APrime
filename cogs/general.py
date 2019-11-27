from imports import *

class Sample(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['latency'], description="Returns the bot latency", usage="ping")
    async def ping(self, ctx, host: str = None):
        if host:
            code = None
            color = ui.colors['red']

            success = False

            async with aiohttp.ClientSession() as session:
                start = time.monotonic()
                try:
                    async with session.get(host) as resp:
                        code = str(resp.status)
                        success = True
                        color = ui.colors['green']
                except aiohttp.client_exceptions.InvalidURL:
                    title = "Invalid URL"
                    description = "Make sure the url you provided is valid."
                except Exception as e:
                    title = f"Error when sending request to : {host}"
                    description = str(e)
                latency = time.monotonic() - start
            
            if success:
                title = f"Request has been sent to {host}"
                description = f"The latency is `{round(latency*1000, 5)}ms`\nStatus Code : {code}"
            
            previousEmbed = await ui.embed(self, ctx, title, description, color=color)
            
            if success:
                icons = favicon.get(host)
                if icons:
                    icon = icons[0]
                    newEmbed = await ui.embed(self, ctx, title, description, color=color, thumbnail=icon.url, send=False)
                    await previousEmbed.edit(embed=newEmbed)
                
            return

        latency = round(self.bot.latency*1000, 2)
        return await ctx.send(f"Ping Pong! :ping_pong: `{latency}ms`")
    
    @commands.command(description="Returns the list of commands", usage="help")
    async def help(self, ctx):
        commands = []
        for command in self.bot.commands:
            if not command.hidden:
                data = f"**{bot.getPrefix()}{command.name}**\n{command.description}\n**Usage: {bot.getPrefix()}{command.usage}**\n\n"
                commands.append(data)
        commands = "".join(commands)
        
        await ui.embed(self, ctx, title="Command List", description=commands)

def setup(bot):
    bot.add_cog(Sample(bot))
