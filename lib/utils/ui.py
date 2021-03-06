from discord.embeds import Embed
from lib.utils import bot
from lib.utils.globals import db
from collections import Counter

import discord 
import datetime
import random
import time
import asyncio
import string

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

class Icons:
    def __init__(self, bot):
        self.bot = bot 
        self.fallback = ":grey_question:"
    
    def coin(self):
        icon = self.bot.get_emoji(689733706037854275)
        if icon is None:
            return self.fallback 
        return str(icon)

def createToken(length=10):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def most_frequent(x):
    oc = Counter(x)
    return oc.most_common(1)[0][0]

class DeltaTemplate(string.Template):
    delimiter = "%"

def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    d["H"], rem = divmod(tdelta.seconds, 3600)
    d["M"], d["S"] = divmod(rem, 60)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)

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

            if isinstance(self.ctx, (discord.User, discord.Member)):
                author = self.ctx 
            else:
                author = self.ctx.author 

            def check(reaction, user):
                return user == author and str(reaction.emoji) in self.reactions and reaction.message.id == message.id
        else:
            check = self.check
        
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=self.timeout, check=check)
            print(reaction.message.id, message.id, reaction.message.id == message.id)
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

def ctxAdditonalData(ctx):
    data = {
        "content": ctx.message.content,
        "prefix": ctx.prefix,
        "invoked_with": ctx.invoked_with,
        "timestamp": int(time.time()),
        "channel": None,
        "guild": None,
        "author": {
            "id": ctx.author.id,
            "name": ctx.author.name,
            "discriminator": ctx.author.discriminator
        }
    }

    if isinstance(ctx.channel, discord.TextChannel):
        data['channel'] = {
            "id": ctx.channel.id,
            "name": ctx.channel.name
        }

        data['guild'] = {
            "id": ctx.guild.id,
            "name": ctx.guild.name
        }
    
    return data

async def properUsage(self, ctx, example, send=True):
    
    if ctx.guild:
        prefix = await bot.getPrefix(ctx.guild, db)
    else:
        prefix = bot.getDefaultPrefix()

    fields = [
        {
            "Proper Usage": f"{prefix}{ctx.command.usage}",
            "inline": False
        },
        {
            "Example": f"{prefix}{example}",
            "inline": False
        }
    ]
    
    e = await embed(self, ctx, fields=fields, color=colors['red'], send=False)
    if send:
        return await ctx.send(embed=e)
    return e

async def loadingEmbed(self, ctx, title="Please wait...", description="Loading data", send=True):
    url = "https://storage.googleapis.com/discordstreet/emojis/loading.gif"
    return await embed(self, ctx, title=title, description=description, send=send, thumbnail=url)

async def embed(self, ctx, title=None, description=None, url=None, fields=None, color=None, thumbnail=None, image=None, footer=defaultFooter, showTimeStamp=True, send=True):
    if type(title) is dict:
        e = Embed.from_dict(title)
        if send:
            return await ctx.send(embed=e)
        return e 
    
    if not color:
        color = colors[random.choice(list(colors.keys()))]

    if isinstance(title, str):
        if len(title) >= 256:
            title = title[0:250] + "..."
    
    if isinstance(description, str):
        if len(description) >= 2048:
            description = description[0:2040] + "..."

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
    
    if isinstance(ctx, (discord.User, discord.Member)):
        author = ctx
    else:
        author = ctx.author
    
    if thumbnail != 0:
        if thumbnail:
            e.set_thumbnail(url=thumbnail)
        else:
            e.set_thumbnail(url=self.bot.user.avatar_url)
    
    if image:
        e.set_image(url=image)

    if footer:
        icon = self.bot.user.avatar_url
        text = footer["text"].replace("//author//", f"{author.name}#{author.discriminator}")

        if footer['icon']:
            icon = footer['icon']
            if "//author.avatar//" in footer['icon']:
                if author.avatar_url:
                    icon = author.avatar_url
        
        e.set_footer(text=text, icon_url=icon)
    
    if send:
        return await ctx.send(embed=e)
    return e
