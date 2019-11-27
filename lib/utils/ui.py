from discord.embeds import Embed
from lib.utils import bot

import discord 
import datetime
import random

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

async def properUsage(self, ctx, example, send=True):
    fields = [
        {
            "Proper Usage": f"{bot.getPrefix()}{ctx.command.usage}",
            "inline": False
        },
        {
            "Example": f"`{bot.getPrefix()}{example}`",
            "inline": False
        }
    ]
    
    e = await embed(self, ctx, fields=fields, color=colors['red'], send=False)
    if send:
        return await ctx.send(embed=e)
    return e

async def embed(self, ctx, title=None, description=None, url=None, fields=None, color=None, thumbnail=None, image=None, footer=defaultFooter, showTimeStamp=True, send=True):
    print(locals().values())
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

        if "//author.avatar//" in footer['icon']:
            if ctx.author.avatar_url:
                icon = ctx.author.avatar_url
        
        e.set_footer(text=text, icon_url=icon)
    
    if send:
        return await ctx.send(embed=e)
    return e
