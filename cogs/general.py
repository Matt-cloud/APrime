from imports import *

class General(commands.Cog):
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
        prefix = bot.getPrefix(ctx.guild, db)

        for command in self.bot.commands:
            # First turn it into an array so we could sort it
            if not command.hidden:
                data = {
                    "prefix": prefix,
                    "name": command.name,
                    "description": command.description,
                    "usage": command.usage,
                    "category": command.cog.qualified_name
                }
                commands.append(data)

        # Sort it
        output = []

        # Convert the array of command into a readeable output
        for command in commands:
            data = f"**{command['prefix']}{command['name']}**\n{command['description']}\nCategory: `{command['category']}`\n**Usage: {command['prefix']}{command['usage']}**\n\n"
            output.append(data)
        output = "".join(output)

        await ui.embed(self, ctx, title="Command List", description=output)

    @commands.command(description="Allows you to report members to the server moderator.", usage="report <mention a member> <reason for being reported>")
    async def report(self, ctx, user: discord.Member = None, *, reason: str = None):
        if user is None or reason is None:
            return await ui.properUsage(self, ctx, f"report {ctx.author.mention} reported for being too cool :)")
        
        # TODO: If there is no report channel then cancel the process (return a message)
        # TODO: If there is a report channel then send the report to that channel

        # NOTE: Template
        # Date: (seperate from embed timestamp)
        # Report by: ctx.author
        # Reported member: user
        # Reason: reason

def setup(bot):
    bot.add_cog(General(bot))
