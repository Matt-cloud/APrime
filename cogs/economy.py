from imports import * 

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.commandsCount = 0
        self.icons = ui.Icons(bot)
    
    async def update_profile_xp(self, xp, user_id):
        if await db.profiles.count_documents({"id": user_id}):

            data = await db.profiles.find_one({"id": user_id})

            if data['xp'] >= data['total_xp'] or data['xp'] + xp >= data['total_xp']:
                data['total_xp'] = int(data['total_xp'] * 1.5)
                data['xp'] = 0
                data['level'] = data['level'] + 1

                coins_reward = random.randint(300, 800)
                data['coins'] = data['coins'] + coins_reward

                await db.profiles.update_one({"id": user_id}, {"$set": data})
            else:
                await db.profiles.update_one({"id": user_id}, {"$inc": {"xp": xp}})

        else:
            data = {
                "id": user_id,
                "xp": 0,
                "total_xp": 250,
                "level": 1,
                "coins": 500,
                "description": "",
                "gender": "Male",
                "reputation": []
            }
            await db.profiles.insert_one(data)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        # XP fucking "algorithm"

        if ctx.author.bot:
            return

        self.commandsCount += 1
        
        value = len(ctx.prefix) + len(ctx.command.name) + len(ctx.author.name) + int(ctx.author.discriminator) + self.commandsCount

        if ctx.message.content:
            value += len(ctx.message.content)

        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                if attachment.width and attachment.height:
                    value += attachment.width + attachment.height
        
        if ctx.guild:
            value += len(ctx.guild.name)

            if ctx.guild.description:
                value += len(ctx.guild.description)

            value += len(ctx.guild.members)
            
            randomMember = random.choice(ctx.guild.members)

            value += len(randomMember.display_name) + randomMember.color.r + randomMember.color.g + randomMember.color.b + int(randomMember.discriminator) + int(randomMember.id)
        
        value = [int(x) for x in str(value)]
        random.shuffle(value)

        sampleSize = random.randint(1, 2)
        sample = random.sample(value, sampleSize)

        await self.update_profile_xp(sum(sample), ctx.author.id)
    
    async def handle_commands_count(self):
        while True:

            await db.config.update_one({"foo": "bar"}, {"$inc": {"command_count": self.commandsCount}})

            self.commandsCount = 0
            await asyncio.sleep(60)
    
    @commands.command(description="Shows you information about your profile or other's", usage="profile <mention a user (optional)>")
    async def profile(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        
        prefix = bot.getPrefix(ctx.guild, db)
        
        if not await db.profiles.count_documents({"user_id": user.id}):
            await self.update_profile_xp(1, user.id)
        
        info = await db.profiles.find_one({"user_id": user.id})

        fields = [
            {"XP": f"**{info['xp']}/{info['total_xp']}**"},
            {f"Coins {self.icons.coin}": str(info['coins'])},
            {"Level": str(info['level'])},
            {"Reputation": str(len(info['reputation']))},
            {"Gender": info['gender']}
        ]

        s = "'s"
        if user.name.endswith("s"):
            s = "'"
        elif user.name.endswith(("'s", "'")):
            s = ""
        
        if info['description'].strip() == "":
            description = "No description set."
            if ctx.author == user:
                description += " You can set a description using the `{prefix}set_profile_description` command."

        await ui.embed(self, ctx, title=f"{user.name}{s} Profile Information", description=description, fields=fields, thumbnail=user.avatar_url)
        

def setup(bot):
    bot.add_cog(Economy(bot))
