from discord.embeds import Embed
from lib.utils import bot
from lib.utils.globals import db

import discord 
import datetime
import random
import asyncio

colors = {
    "red": 0xF44336,
    "pink": 0xE91E63,
    "purple": 0x9c27b0,
    "deep purple": 0x673ab7,
    "indigo": 0x3f51b5,
    "blue": 0x2196f3,
    "light blue": 0x03a9f4,
    "cyan": 0x00bcd4,
    "teal": 0x009688,
    "green": 0x4caf50,
    "light green": 0x8bc34a,
    "lime": 0xcddc39,
    "yellow": 0xffeb3b,
    "amber": 0xffc107,
    "orange": 0xff9800,
    "deep orange": 0xff5722,
    "brown": 0x795548,
    "grey": 0x9e9e9e,
    "blue grey": 0x607d8b
}

defaultFooter = {
    "text": "Requested by //author//",
    "icon": "//author.avatar//"
}

strftime = "%b %m, %Y at %I:%M %p"

class reactionConfirmation:
    def __init__(self, bot, ctx, content, reactions, **kwargs):
        self.reactions = reactions
        self.ctx = ctx
        self.timeout = kwargs.get("timeout", 120.0)
        self.content = content
        self.bot = bot
        self.check = kwargs.get("check", None)
        self.timeout_content = kwargs.get("timeout_content", None)

    async def start(self):
        content, contentType = parseContent(self.content)
        if contentType == discord.embeds.Embed:
            if content['embed'].footer.text.startswith(defaultFooter['text'].replace("//author//", "")):
                content['embed'].set_footer(text="Use the buttons below to navigate", icon_url=content['embed'].footer.icon_url)

        message = await self.ctx.send(**content)

        for reaction in list(self.reactions.keys()):
            await message.add_reaction(reaction)
        
        if not self.check:
            def check(reaction, user):
                return user == self.ctx.author and str(reaction.emoji) in self.reactions and reaction.message.id == message.id
        else:
            check = self.check
        
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=self.timeout, check=check)
            function = self.reactions[str(reaction.emoji)]

            if asyncio.iscoroutinefunction(function):
                await function()
            else:
                function()

        except asyncio.TimeoutError:
            content = self.timeout_content
            if content:
                content, contentType = parseContent(content)
                await self.ctx.send(**content)

def parseContent(c):
    if isinstance(c, discord.embeds.Embed):
        content = dict(embed=c)
        contentType = discord.embeds.Embed
    elif isinstance(c, dict):
        content = c # You could also pass in your own dictionary
        contentType = dict 
    else:
        content = dict(content=c)
        contentType = str
    return content, contentType

def discrim(c):
    return f"{c.name}#{c.discriminator}"

async def properUsage(self, ctx, example, send=True):
    fields = [
        {
            "Proper Usage": f"{bot.getPrefix(ctx.guild, db)}{ctx.command.usage}",
            "inline": False
        },
        {
            "Example": f"{bot.getPrefix(ctx.guild, db)}{example}",
            "inline": False
        }
    ]
    
    e = await embed(self, ctx, fields=fields, color=colors['red'], send=False)
    if send:
        return await ctx.send(embed=e)
    return e

async def embed(self, ctx, title=None, description=None, url=None, fields=None, color=None, thumbnail=None, image=None, footer=defaultFooter, showTimeStamp=True, send=True):
    if type(title) is dict:
        e = Embed.from_dict(title)
        if send:
            return await ctx.send(embed=e)
        return e 
    
    if not color:
        color = colors[random.choice(list(colors.keys()))]

    e = Embed(title=title, description=description, url=url, color=color)

    if type(fields) is list:
        for field in fields:
            inline = True 
            if "inline" in list(field.keys()):
                inline = field['inline']
                del field['inline']
            
            for name, value in field.items():
                e.add_field(name=name, value=value, inline=inline)
    
    if showTimeStamp:
        e.timestamp = datetime.datetime.now()
    
    if thumbnail:
        e.set_thumbnail(url=thumbnail)
    else:
        e.set_thumbnail(url=self.bot.user.avatar_url)

    if image:
        e.set_image(url=image)

    if footer:
        icon = self.bot.user.avatar_url
        text = footer["text"].replace("//author//", f"{ctx.author.name}#{ctx.author.discriminator}")

        if footer['icon']:
            if "//author.avatar//" in footer['icon']:
                if ctx.author.avatar_url:
                    icon = ctx.author.avatar_url
        
        e.set_footer(text=text, icon_url=icon)
    
    if send:
        return await ctx.send(embed=e)
    return e
