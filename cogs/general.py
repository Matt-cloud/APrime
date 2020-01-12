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
        
        if db.report_channels.count_documents({"guild_id": ctx.guild.id}):
            channelData = db.report_channels.find_one({"guild_id": ctx.guild.id})
            channel = self.bot.get_channel(channelData['channel_id'])
            
            reportData = { # Maybe store in database when database is upgraded
                "user": user.id,
                "reason": reason,
                "report_by": ctx.author.id,
                "report_date":  int(time.time()),
                "report_from": {
                    "channel_id": ctx.channel.id,
                    "guild_id": ctx.guild.id,
                    "jump_url": ctx.message.jump_url 
                }
            }

            report_embed = await ui.embed(
                self, ctx, send=False, footer=None, thumbnail=user.avatar_url,
                title=f"Report for {ui.discrim(user)} submitted by {ui.discrim(ctx.author)}",
                fields=[
                    {
                        "Reason": reportData['reason']
                    },
                    {
                        "Report Date": f"(UTC) {datetime.datetime.utcfromtimestamp(reportData['report_date']).strftime(ui.strftime)}"
                    }
                ],
                description=f"""
From channel : {self.bot.get_channel(reportData['report_from']['channel_id']).mention}
From server : {self.bot.get_guild(reportData['report_from']['guild_id']).name}
Jump Url : {reportData['report_from']['jump_url']}
"""
            )
            await channel.send(embed=report_embed)
            await ui.embed(self, ctx, title=f"A report for {ui.discrim(user)} has been successfully submitted.", description=reason, color=ui.colors['green'], thumbnail=user.avatar_url)
            return
        
        await ui.embed(self, ctx, title="No report channel for this server", description=f"In order to report users that are violating the rules of the server, a server moderator must first set a report channel using the `{bot.getPrefix(ctx.guild, db)}set_report_channel` where reports will be sent to.", color=ui.colors['red'])
        
        # TODO : Add message if trying to report self

def setup(bot):
    bot.add_cog(General(bot))
