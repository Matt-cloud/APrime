from imports import *

class RedditCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
    
    @commands.command(aliases=['findreddit', 'findsubreddit'], description="Lets you find a subreddit by using keywords or sentences.", usage="findareddit <query>")
    async def findareddit(self, ctx, *, query: str = None):
        if not query:
            return await ui.properUsage(self, ctx, "findareddit A subreddit with actually funny content.")

        base = "https://www.reddit.com"
        sub = reddit.subreddit("findareddit")
        results = []
        results_actual = []

        loadingEmbed = await ui.loadingEmbed(self, ctx, description="Searching for subreddits that match your query.", send=False)
        loading = await ctx.send(embed=loadingEmbed)
        
        if db.cached_subreddits.count_documents({"query": query.lower()}):
            t_start = time.perf_counter()
            results = db.cached_subreddits.find_one({"query": query.lower()})['results_md']
            t_stop = time.perf_counter()
            t_elapsed = t_stop - t_start
            searchTime = round(t_elapsed * 1000, 2)
        else:
            t_start = time.perf_counter()
            for item in sub.search(query, limit=5):
                for comment in item.comments:

                    splitted = comment.body.split(" ")
                    subredditsStarterPack = ("r/", "/r/")

                    for word in splitted:
                        totalLength = len(''.join(results))
                        if word.startswith(subredditsStarterPack):
                            if totalLength + len(word) < 2000:
                                sr = word.replace("\n", "").replace(".", "").replace("+", "").replace(",", "").replace("|", "").replace(";", "").replace(":", "").replace("?", "")
                                before = "/"
                                if sr.startswith("/"):
                                    before = ""
                                url = base + before + sr 
                                complete = f"[{sr}]({url})\n"
                                results.append(complete)
                                results_actual.append({
                                    "subreddit": sr,
                                    "url": url
                                })
            t_stop = time.perf_counter()
            data = {
                "query": query.lower(),
                "cached_by": ctx.author.id,
                "cached_on": int(time.time()),
                "results_md": results, #md = markdown k?
                "results": results_actual,
                "search_time": t_stop - t_start
            }
            if results:
                db.cached_subreddits.insert_one(data)
            searchTime = round(data['search_time']*1000, 2)
        
        await loading.delete()

        fields = [
            {
                "Search Time": f"`{searchTime}ms`"
            }
        ]
        
        if not results:
            description = f"Sorry but I cannot find any subreddit for the query `{query}`"
            if len(description) > 2000:
                description = description[0:2000] + "..."
            return await ui.embed(self, ctx, title="No subreddits found", description=description, color=ui.colors['red'], fields=fields)
        
        title = f"Subreddits for {query}"
        if len(title) > 255:
            title = title[0:251] + "..."
        description = "".join(results)

        await ui.embed(self, ctx, title=title, description=description, thumbnail="https://cdn3.iconfinder.com/data/icons/2018-social-media-logotypes/1000/2018_social_media_popular_app_logo_reddit-512.png", fields=fields)
    
    @commands.command(alias=['memes', 'dankmemes', 'me_irl', 'meirl'])
    async def meme(self, ctx):
        if not db.memes.count_documents({}):
            return await ui.embed(self, ctx, title="Memes out of stock", description="Just visit [reddit](https://reddit.com) dude.", color=ui.colors['red'])
            
        aggregate_opts = [
            {"$sample": {"size": 1}}
        ]
        if not ctx.channel.is_nsfw():
            aggregate_opts.append(
                {"$match": {"nsfw": False}}
            )
        
        for r in db.memes.aggregate(aggregate_opts):
            data = r
        await ui.embed(self, ctx, title=data['title'], url=data['shortlink'], image=data['url'], thumbnail=0)

def setup(bot):
    bot.add_cog(RedditCommands(bot))
