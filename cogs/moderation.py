from imports import *

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Allows you to change the prefix that the bot recognizes for this server. (Maximum of 7 characters and no spaces)", usage="set_custom_prefix <new_prefix>")
    @commands.cooldown(1, 120, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def set_custom_prefix(self, ctx, new_prefix: str = None):
        if not new_prefix:
            return await ui.properUsage(self, ctx, "set_custom_prefix ?")

        if len(new_prefix) > 7:
            return await ui.embed(self, ctx, title="Prefix should not be greater than 7 characters.", color=ui.colors['red'])

        allowPrefixMessage = f"By default the default prefix `--` can still be used. If you want to disable the default prefix use the `{new_prefix}toggle_default_prefix`"
        loggerMessage = f"Server : {ctx.guild.id} has changed its server prefix to {new_prefix}"
        
        data = {
            "guild_id": ctx.guild.id,
            "prefix": new_prefix,
            "allow_default_prefix": True,
            "additional_data": ui.ctxAdditonalData(ctx)
        }

        if await db.prefixes.count_documents({"guild_id": ctx.guild.id}):
            oldPrefixData = await db.prefixes.find_one({"guild_id": ctx.guild.id})
            myEmbed = await ui.embed(self, ctx, title=f"This server already has a custom  prefix.", description=f"""
Custom Prefix : `{oldPrefixData['prefix']}`

To overwrite click ✅.
To cancel click ❌.
""")        
            reactions = ["✅", "❌"]
            for reaction in reactions:
                await myEmbed.add_reaction(reaction)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in reactions

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                if str(reaction.emoji) == "✅":
                    description = None 
                    data['allow_default_prefix'] = oldPrefixData['allow_default_prefix']

                    if oldPrefixData['allow_default_prefix']:
                        description = allowPrefixMessage
                    
                    await db.prefixes.update_one({"guild_id": data['guild_id']}, {"$set": data})
                    await logger.log(loggerMessage)

                    return await ui.embed(self, ctx, title="Successfully overwrote the server prefix.", description=description, color=ui.colors['green'])
                elif str(reaction.emoji) == "❌":
                    return await ui.embed(self, ctx, title="Canceled, nothing has changed.", color=ui.colors['red'])
            except asyncio.TimeoutError:
                await ui.embed(self, ctx, title="Timeout, nothing has changed.", color=ui.colors['red'])
            return

        await db.prefixes.insert_one(data)
        await logger.log(loggerMessage)

        await ui.embed(self, ctx, title="Successfully changed the server prefix.", description=allowPrefixMessage, color=ui.colors['green'])

    @commands.command(description="Toggles the default prefix on and off for this server. (Can only be used if you have a custom prefix for this server)", usage="toggle_default_prefix")
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def toggle_default_prefix(self, ctx):
        prefixData = await db.prefixes.find_one({"guild_id": ctx.guild.id})

        prefix = await bot.getPrefix(ctx.guild, db)
        defaultPrefix = bot.getDefaultPrefix()

        if not prefixData:
            return await ui.embed(self, ctx, title="You have to set a custom prefix for this server first before disabling the default prefix.", description=f"To set a custom a prefix simply use the `{prefix}set_custom_prefix` command.", color=ui.colors['red'])
        
        newValue = not prefixData['allow_default_prefix']
        
        await db.prefixes.update_one({"guild_id": ctx.guild.id}, {"$set": {"allow_default_prefix": newValue}})
        await logger.log(f"Server : {ctx.guild.id} has changed its allow_default_prefix to : {newValue}")

        if newValue:
            description = f"You can once again use the default prefix `{defaultPrefix}` in this server while still being able to use the custom prefix `{prefix}`."
        else:
            description = f"You can no longer use the default prefix `{defaultPrefix}`. You must use the custom prefix `{prefix}` in order to run commands."

        await ui.embed(self, ctx, title="Successfully toggled the default prefix for this server.", description=description, color=ui.colors['green'])

    @commands.command(description="Deletes the custom prefix. If you have the default prefix turned off this will automatically turn it on.", usage="delete_custom_prefix")
    @commands.cooldown(1, 120, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def delete_custom_prefix(self, ctx):
        prefixData = await db.prefixes.find_one({"guild_id": ctx.guild.id})
        defaultPrefix = bot.getDefaultPrefix()

        if not prefixData:
            return await ui.embed(self, ctx, title="You have nothing to delete.", description=f"You haven't set a custom prefix yet, to do so use the `{defaultPrefix}set_custom_prefix` command.", color=ui.colors['red'])

        async def _continue():
            await db.prefixes.delete_one({"guild_id": ctx.guild.id})
            await logger.log(f"Server : {ctx.guild.id} has deleted its custom prefix.")
            await ui.embed(self, ctx, title="Successfully deleted the custom prefix for this server.", color=ui.colors['green'])
        
        async def cancel():
            await ui.embed(self, ctx, title="Canceled, nothing has changed.", color=ui.colors['red'])

        reactions = {
            "✅": _continue,
            "❌": cancel
        }

        confirmationEmbed = await ui.embed(self, ctx, title="Are you sure you want to do this?", description="Please keep in mind that this cannot be undone. \nUse the buttons below to either confirm or deny.", send=False)
        confirmation = ui.reactionConfirmation(self.bot, ctx, confirmationEmbed, reactions)

        await confirmation.start()
    
    @commands.command(description="Allows you to setup a report channel so that members can report other members.", usage="set_report_channel <mention a channel>")
    @commands.cooldown(1, 120, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def set_report_channel(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            return await ui.properUsage(self, ctx, f"set_report_channel {ctx.channel.mention}")
        
        data = {
            "channel_id": channel.id,
            "guild_id": ctx.guild.id,
            "additional_data": ui.ctxAdditonalData(ctx)
        }

        if await db.report_channels.count_documents({"guild_id": ctx.guild.id, "channel_id": channel.id}):
            return await ui.embed(self, ctx, title="That's already the report channel for this server.", color=ui.colors['red'])
        
        if await db.report_channels.count_documents({"guild_id": ctx.guild.id}):
            prevReport = await db.report_channels.find_one({"guild_id": ctx.guild.id})
            prevReportChannel = self.bot.get_channel(prevReport['channel_id'])

             # TODO: If overwrite then ask user if he wants to move all reports to that channel or keep it in the old channel.
                # TODO: If move, only move it with an interval of 5 seconds to avoid api abuse (tell to user)
                # NOTE: If bot goes down while moving reports, handle it magically so that it starts moving the next time it goes up.
                # NOTE: Handle stuff like if one of the channels get deleted.

            async def yes():
                await db.report_channels.update_one({"guild_id": data['guild_id']}, {"$set": data})
                await ui.embed(self, ctx, title="Success!", description=f"Successfully overwrote the report channel to {channel.mention}", color=ui.colors['green'])
            
            async def no():
                await ui.embed(self, ctx, title="Canceled, Nothing has changed.", color=ui.colors['red'], description=f"{prevReportChannel.mention} is still the current report channel.")
            
            reactions = {
                "✅": yes,
                "❌": no
            }
            confirmation = ui.reactionConfirmation(
                self.bot,
                ctx,
                await ui.embed(
                    self,
                    ctx,
                    title="There's already a report channel set for this server.",
                    description=f"The current report channel for this server is {prevReportChannel.mention}, Do you want to overwrite it?",
                    color=ui.colors['red'],
                    send=False
                ),
                reactions
            )

            return await confirmation.start()

        await db.report_channels.insert_one(data)
        await ui.embed(self, ctx, title="Success!", description=f"Report channel successfully set to {channel.mention}. If you want to restore it back to a regular channel use the `{await bot.getPrefix(ctx.guild, db)}restore_report_channel` command.", color=ui.colors['green'])
    
    @commands.command(description="Restores the report channel to just a regular channel. (This does not delete the channel)", usage="delete_report_channel")
    @commands.cooldown(1, 120, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def restore_report_channel(self, ctx):
        if await db.report_channels.count_documents({"guild_id": ctx.guild.id}):
            channelData = await db.report_channels.find_one({"guild_id": ctx.guild.id})
            channel = self.bot.get_channel(channelData['channel_id'])

            async def yes():
                await db.report_channels.delete_one({"guild_id": ctx.guild.id})
                await ui.embed(self, ctx, title="Success!", description=f"Successfully restored {channel.mention} to a regular channel.", color=ui.colors['green'])
            
            async def no():
                await ui.embed(self, ctx, title="Canceled, Nothing has changed", description=f"{channel.mention} is still a report channel.", color=ui.colors['red'])
            
            reactions = {
                "✅": yes,
                "❌": no
            }
            confirmation = ui.reactionConfirmation(
                self.bot, ctx, 
                await ui.embed(
                    self, ctx, send=False, color=ui.colors['red'],
                    title="Are you sure you want to restore the current report channel to a regular channel?"
                ),
                reactions 
            )
            
            return await confirmation.start()
        
        await ui.embed(
            self, ctx, color=ui.colors['red'],
            title="There is no report channel in this server.",
            description=f"To set one use the `{await bot.getPrefix(ctx.guild, db)}set_report_channel` command."
        )
    
    @commands.command(description="A chatbot channel let's you talk to a 'machine learning' powered chatbot that responds like a human.", usage="set_chatbot_channel <mention a channel>")
    @commands.cooldown(1, 120, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def set_chatbot_channel(self, ctx, channel: discord.TextChannel = None):

        delete_old = False 

        if channel is None:
            return await ui.properUsage(self, ctx, f"set_chatbot_channel {ctx.channel.mention}")
        
        if await db.chatbots.count_documents({"guild_id": ctx.guild.id}):

            channel_id = await db.chatbots.find_one({"guild_id": ctx.guild.id})
            channel_id = channel_id['channel_id']
            channel_old = ctx.guild.get_channel(int(channel_id))

            if channel_old:

                async def yes():
                    await db.chatbots.update_one({"guild_id": ctx.guild.id}, {"$set": {"channel_id": channel.id}})
                    await ui.embed(self, ctx, description=f"Successfully replaced the old chatbot channel with {channel.mention}", color=ui.colors['green'])
                    
                async def no():
                    await ui.embed(self, ctx, title="Canceled, Nothing has changed.", color=ui.colors['red'])
                
                reactions = {
                    "✅": yes,
                    "❌": no
                }

                confirmation = ui.reactionConfirmation(
                    self.bot, ctx, 
                    await ui.embed(
                        self, ctx, send=False, color=ui.colors['red'],
                        title="This server already has a chatbot channel, Do you want to replace it?",
                        description=f"The current chatbot channel for this server is {channel_old.mention}"
                    ),
                    reactions 
                )
                return await confirmation.start()
            else:
                delete_old = True
        
        if delete_old:
            await db.chatbots.delete_many({"guild_id": ctx.guild.id})

        data = {
            "guild_id": ctx.guild.id,
            "channel_id": channel.id,
            "additional_data": ui.ctxAdditonalData(ctx)
        }

        await db.chatbots.insert_one(data)

        await ui.embed(
            self, ctx, color=ui.colors['green'],
            description=f"Successfully set the chatbot channel to {channel.mention}"
        )
    
    @commands.command(description="Restores the chatbot channel back to a regular channel. (This does not delete the channel)", usage="restore_chatbot_channel")
    @commands.cooldown(1, 120, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def restore_chatbot_channel(self, ctx):
        if not await db.chatbots.count_documents({"guild_id": ctx.guild.id}):
            return await ui.embed(self, ctx, title="There is no chatbot channel in this server.", description=f"To set one use the `{await bot.getPrefix(ctx.guild, db)}set_chatbot_channel` command.", color=ui.colors['red'])
        
        async def yes():
            await db.chatbots.delete_many({"guild_id": ctx.guild.id})
            await ui.embed(self, ctx, title="Successfully deleted the chatbot channel.", color=ui.colors['green'])
            
        async def no():
            await ui.embed(self, ctx, title="Canceled, Nothing has changed.", color=ui.colors['red'])
        
        reactions = {
            "✅": yes,
            "❌": no
        }

        confirmation = ui.reactionConfirmation(
            self.bot, ctx,
            await ui.embed(
                self, ctx, send=False, color=ui.colors['red'],
                title="Are you sure you want to restore the chatbot channel back to a regular channel?"
            ),
            reactions
        )

        await confirmation.start()
    
    @commands.command(description="DM's you the server's report channel and other information about it,", usage="report_channel", aliases=["reports"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def report_channel(self, ctx):

        if await db.report_channels.count_documents({"guild_id": ctx.guild.id}):
            channel = await db.report_channels.find_one({"guild_id": ctx.guild.id})
            channel = self.bot.get_channel(channel['channel_id'])

            reports = []
            users = []

            async for item in db.reports.find({}):
                if item['report_from']['guild_id'] == ctx.guild.id:
                    reports.append(item)
                    users.append(item['user'])

            frequent = ui.most_frequent(users)
            user = self.bot.get_user(frequent)

            fields = [
                {"Name": channel.name, "inline": False},
                {"Server": channel.guild.name, "inline": False},
                {"Reports Count": len(reports), "inline": False},
                {"Frequently Reported": ui.discrim(user), "inline": False}
            ]

            info = await ui.embed(self, ctx, send=False, title="Report Channel Information", fields=fields, thumbnail=ctx.guild.icon_url)
            await ctx.author.send(embed=info)

            await ui.embed(self, ctx, title="Report Channel Information Sent", description=f"{ctx.author.mention} I have successfully sent you the basic information for the report channel of this server.")
            # TODO : Add a dashboard for reports (MOOoore info)

def setup(bot):
    bot.add_cog(Moderation(bot))
