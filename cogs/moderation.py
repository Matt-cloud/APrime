from imports import *

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Allows you to change the prefix that the bot uses for this server.", usage="change_server_prefix <new_prefix>")
    @commands.has_permissions(manage_guild=True)
    async def change_server_prefix(self, ctx, *, new_prefix: str = None):
        if not new_prefix:
            return await ui.properUsage(self, ctx, "change_server_prefix ?")
        
        data = {
            "guild_id": ctx.guild.id,
            "prefix": new_prefix,
            "set_by": ctx.author.id,
            "set_in_channel": ctx.channel.id
        }

        if db.prefixes.count_documents({"guild_id": ctx.guild.id}):
            # TODO If server's prefix is already modified then ask the user if he wants to overwrite it.
            # TODO Update everything from guild_id to set_in_channel if yes
            # TODO Use the dpy-ui library i think for asking the user
            pass

        db.prefixes.insert_one(data)
        await ctx.send("Dun")

def setup(bot):
    bot.add_cog(Moderation(bot))
