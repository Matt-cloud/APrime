from imports import *

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['dice'], description="Rolls the dice", usage="rolladice")
    async def rolladice(self, ctx):
        dice = random.randint(1, 6)
        fp = f"dice{dice}.gif"
        fp = os.path.join("data", "Dice", fp)

        f = discord.File(fp, filename="dice.gif")
        e = await ui.embed(self, ctx, title=f"You rolled the dice and got {dice}", image="attachment://dice.gif", send=False, thumbnail=0)

        await ctx.send(file=f, embed=e)
    
def setup(bot):
    bot.add_cog(Fun(bot))
