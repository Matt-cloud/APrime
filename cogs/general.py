from imports import *

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['latency'], description="Returns the bot latency", usage="ping")
    @commands.cooldown(1, 7, commands.BucketType.user)
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
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def help(self, ctx):

        # TODO : Improve this command
        commands = []
        prefix = await bot.getPrefix(ctx.guild, db)

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
    @commands.cooldown(1, 30, commands.BucketType.user)
    @checks.guild_only()
    async def report(self, ctx, user: discord.Member = None, *, reason: str = None):
        if user is None or reason is None:
            return await ui.properUsage(self, ctx, f"report {ctx.author.mention} reported for being too cool :)")

        if user == ctx.author:
            return await ui.embed(
                self, ctx,
                title="I wouldn't report my self if I were you.",
                color=ui.colors['red']
            )
        
        if await db.report_channels.count_documents({"guild_id": ctx.guild.id}):
            channelData = await db.report_channels.find_one({"guild_id": ctx.guild.id})
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
                },
                "additional_data": ui.ctxAdditonalData(ctx)
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
        
        await ui.embed(self, ctx, title="No report channel for this server", description=f"In order to report users that are violating the rules of the server, a server moderator must first set a report channel using the `{await bot.getPrefix(ctx.guild, db)}set_report_channel` where reports will be sent to.", color=ui.colors['red'])
    
    @commands.command(description="Returns a link for your google query.", usage="google <query>")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def google(self, ctx, *, query: str = None):
        if query is None:
            return await ui.properUsage(self, ctx, "google Top 10 stuff")
        
        url = "https://google.com/search?q=" + query.replace(" ", "+")
        await ui.embed(self, ctx, title="Here is your query.", description=url, thumbnail="https://cdn4.iconfinder.com/data/icons/new-google-logo-2015/400/new-google-favicon-512.png")
    
    @commands.command(description="Reminds you about something in x minutes or hours.", usage="remindme <when> <reminder>")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def remindme(self, ctx, *, x: str = None):
        if x is None:
            return await ui.properUsage(self, ctx, "remindme 12h wash the dishes")

        units = {
            "s": 1,
            "m": 60,
            "h": 3600,
            "d": 86400,
            "w": 604800
        }

        unitsConversion = {
            "second": "s",
            "minute": "m",
            "hour": "h",
            "day": "d",
            "week": "w"
        }

        intervals = []
        humanIntervals = []
        labels = []
        
        x = x.strip()
        x = x.split()

        reason = []

        keepGoing = True

        for index, i in enumerate(x):
            iNormal = i
            i = i.lower()
            
            success = True

            if keepGoing:
                _digits = re.findall(r'\d+', i) # Get all digits from string like 12h

                if _digits: # If there are any digits found then proceed
                    digits = int(_digits[0])
                    humanDigit = digits

                    unit = i.replace(_digits[0], "") # Get the letters only

                    # Convert units like second to single letters like s (If failed to do so then it's a game over)
                    if len(unit) > 1:
                        if unit.endswith("s"):
                            unit = unit[:-1] # Remove the s in the end

                        if unit in unitsConversion:
                            unit = unitsConversion[unit]
                        else:
                            success = False
                    

                    if unit in units:

                        interval = digits * units[unit]
                        label = {v:k for k,v in unitsConversion.items()}[unit]

                        if humanDigit > 1:
                            label = label + "s"

                        intervals.append(interval)
                        humanIntervals.append(humanDigit)
                        labels.append(label)

                    else:
                        success = False

                else: # If there are no digits found then it's a game over
                    success = False
            else:
                success = False
            
            if not success:
                keepGoing = False
                reason.append(iNormal)
        
        reason = " ".join(reason)
        totalSeconds = sum(intervals)
        title = "Successfully set the reminder."
        labelList = []

        if reason.strip() == "" or totalSeconds == 0:
            return await ui.properUsage(self, ctx, "remindme 12h wash the dishes")

        for interval, label in zip(humanIntervals, labels):
            labelList.append(f"{interval} {label}")
        
        if len(labelList) > 1:
            labelList.insert(-1, "and")

        completeLabel = " ".join(labelList)
        description = f"I will remind you to {reason} in `{completeLabel}`"

        while True:
            _id = ui.createToken()
            if not await db.reminders.count_documents({"id": _id}):
                break

        data = {
            "id": _id,
            "total_seconds": totalSeconds,
            "timestamp": int(time.time()),
            "completeLabel": completeLabel,
            "intervals": intervals,
            "labels": labels,
            "user": ctx.author.id,
            "reminder": reason,
            "additional_data": ui.ctxAdditonalData(ctx)
        }

        await db.reminders.insert_one(data)

        await ui.embed(self, ctx, title=title, description=description, color=ui.colors['green'])
    
    @commands.command(description="DMs you a link that lets you see and manage your reminders.", usage="myreminders", aliases=['reminders'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def myreminders(self, ctx):
        # TODO: Add to web dashboard
        pass

def setup(bot):
    bot.add_cog(General(bot))
