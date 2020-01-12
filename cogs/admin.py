from imports import *
from pathlib import Path

import traceback
import ast
import os

def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

class AdminStuff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @checks.is_owner()
    async def shutdown(self, ctx):
        # bruh
        exit() 

    @commands.command(hidden=True)
    @checks.is_owner()
    async def load(self, ctx, *, cog):
        try:
            start = time.monotonic()
            self.bot.load_extension(f"cogs.{cog}")
            latency = time.monotonic() - start

            await ui.embed(self, ctx, title="Successfully loaded extension", description=f"`cogs.{cog}`\nThat took about : `{round(latency*1000, 5)}ms`")
        except commands.ExtensionError as e:
            await ui.embed(self, ctx, title="Failed to load extension", description=f"```{traceback.format_exc()}```")
    
    @commands.command(hidden=True)
    @checks.is_owner()
    async def unload(self, ctx, *, cog):
        try:
            start = time.monotonic()
            self.bot.unload_extension(f"cogs.{cog}")
            latency = time.monotonic() - start

            await ui.embed(self, ctx, title="Successfully unloaded extension", description=f"`cogs.{cog}`\nThat took about : `{round(latency*1000, 5)}ms`")
        except commands.ExtensionError as e:
            await ui.embed(self, ctx, title="Failed to unload extension", description=f"```{traceback.format_exc()}```")
    
    @commands.command(hidden=True)
    @checks.is_owner()
    async def reload_all(self, ctx):
        cogs = [x.stem for x in Path(os.path.join(os.getcwd(), "cogs")).glob("*.py")]
        for cog in cogs:
            try:
                start = time.monotonic()
                self.bot.reload_extension(f"cogs.{cog}")
                latency = time.monotonic() - start

                await ui.embed(self, ctx, title="Successfully reloaded extension", description=f"`cogs.{cog}`\nThat took about : `{round(latency*1000, 5)}ms`")
            except commands.errors.ExtensionNotLoaded:
                pass
            except commands.errors.ExtensionAlreadyLoaded:
                pass 
            except Exception as e:
                await ui.embed(self, ctx, title="Failed to reload extension", description=f"```{traceback.format_exc()}```")

    @commands.command(hidden=True, name='reload')
    @checks.is_owner()
    async def _reload(self, ctx, *, cog):
        try:
            start = time.monotonic()
            self.bot.reload_extension(f"cogs.{cog}")
            latency = time.monotonic() - start

            await ui.embed(self, ctx, title="Successfully reloaded extension", description=f"`cogs.{cog}`\nThat took about : `{round(latency*1000, 5)}ms`")
        except commands.ExtensionError as e:
            await ui.embed(self, ctx, title="Failed to reload extension", description=f"```{traceback.format_exc()}```")
    
    @commands.command(hidden=True, name="reloadpkg")
    @checks.is_owner()
    async def reload_pkg(self, ctx, *, pkg):
        start = time.monotonic()

        toReload = importlib.import_module(pkg)
        reloaded = importlib.reload(toReload)

        latency = round((time.monotonic() - start)*1000, 2)
        await ui.embed(self, ctx, title="Successfully reloaded module", description=f"`{reloaded}`")
    
    @commands.command(hidden=True, name="test", usage="test <new_name>")
    @checks.is_owner()
    async def testCommand(self, ctx):
        e = await ui.embed(self, ctx, title="kek", send=False)
        print(e.footer.text)
    
    @commands.command(name="eval", hidden="true")
    @checks.is_owner()
    async def eval_fn(self, ctx, *, cmd):
        """Evaluates input.
        Input is interpreted as newline seperated statements.
        If the last statement is an expression, that is the return value.
        Usable globals:
        - `bot`: the bot instance
        - `discord`: the discord module
        - `commands`: the discord.ext.commands module
        - `ctx`: the invokation context
        - `__import__`: the builtin `__import__` function
        Such that `>eval 1 + 1` gives `2` as the result.
        The following invokation will cause the bot to send the text '9'
        to the channel of invokation and return '3' as the result of evaluating
        >eval ```
        a = 1 + 2
        b = a * 2
        await ctx.send(a + b)
        a
        ```
        """
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        result = (await eval(f"{fn_name}()", env))
        if result:
            await ctx.send(result)
        else:
            await ctx.send("None")

def setup(bot):
    bot.add_cog(AdminStuff(bot))