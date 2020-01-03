from imports import *

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Allows you to change the prefix that the bot recognizes for this server. (Maximum of 7 characters and no spaces)", usage="set_custom_prefix <new_prefix>")
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
            "set_by": ctx.author.id,
            "set_in_channel": ctx.channel.id,
            "set_at": int(time.time()),
            "allow_default_prefix": True
        }

        if db.prefixes.count_documents({"guild_id": ctx.guild.id}):
            oldPrefixData = db.prefixes.find_one({"guild_id": ctx.guild.id})
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
                    
                    db.prefixes.update_one({"guild_id": data['guild_id']}, {"$set": data})
                    logger.log(loggerMessage)

                    return await ui.embed(self, ctx, title="Successfully overwrote the server prefix.", description=description)
                elif str(reaction.emoji) == "❌":
                    return await ui.embed(self, ctx, title="Canceled, nothing has changed.")
            except asyncio.TimeoutError:
                await ui.embed(self, ctx, title="Timeout, nothing has changed.", color=ui.colors['red'])
            return

        db.prefixes.insert_one(data)
        logger.log(loggerMessage)

        await ui.embed(self, ctx, title="Successfully changed the server prefix.", description=allowPrefixMessage)

    @commands.command(description="Toggles the default prefix on and off for this server. (Can only be used if you have a custom prefix for this server)", usage="toggle_default_prefix")
    @commands.has_permissions(manage_guild=True)
    async def toggle_default_prefix(self, ctx):
        # TODO Add confirmation before toggling 
        prefixData = db.prefixes.find_one({"guild_id": ctx.guild.id})

        prefix = bot.getPrefix(ctx.guild, db)
        defaultPrefix = bot.getDefaultPrefix()

        if not prefixData:
            return await ui.embed(self, ctx, title="You have to set a custom prefix for this server first before disabling the default prefix.", description=f"To set a custom a prefix simply use the `{prefix}set_custom_prefix` command.")
        
        newValue = not prefixData['allow_default_prefix']
        
        db.prefixes.update_one({"guild_id": ctx.guild.id}, {"$set": {"allow_default_prefix": newValue}})
        logger.log(f"Server : {ctx.guild.id} has changed its allow_default_prefix to : {newValue}")

        if newValue:
            description = f"You can once again use the default prefix `{defaultPrefix}` in this server while still being able to use the custom prefix `{prefix}`."
        else:
            description = f"You can no longer use the default prefix `{defaultPrefix}`. You must use the custom prefix `{prefix}` in order to run commands."

        await ui.embed(self, ctx, title="Successfully toggled the default prefix for this server.", description=description)

    @commands.command(description="Deletes the custom prefix. If you have the default prefix turned off this will automatically turn it on.", usage="delete_custom_prefix")
    @commands.has_permissions(manage_guild=True)
    async def delete_custom_prefix(self, ctx):
        prefixData = db.prefixes.find_one({"guild_id": ctx.guild.id})
        defaultPrefix = bot.getDefaultPrefix()

        if not prefixData:
            return await ui.embed(self, ctx, title="You have nothing to delete.", description=f"You haven't set a custom prefix yet, to do so use the `{defaultPrefix}set_custom_prefix` command.")

        async def _continue():
            db.prefixes.delete_one({"guild_id": ctx.guild.id})
            logger.log(f"Server : {ctx.guild.id} has deleted its custom prefix.")
            await ui.embed(self, ctx, title="Successfully deleted the custom prefix for this server.")
        
        async def cancel():
            await ui.embed(self, ctx, title="Canceled, nothing has changed.")

        reactions = {
            "✅": _continue,
            "❌": cancel
        }

        confirmationEmbed = await ui.embed(self, ctx, title="Are you sure you want to do this?", description="Please keep in mind that this cannot be undone. \nUse the buttons below to either confirm or deny.", send=False)
        confirmation = ui.reactionConfirmation(self.bot, ctx, confirmationEmbed, reactions)

        await confirmation.start()

def setup(bot):
    bot.add_cog(Moderation(bot))
