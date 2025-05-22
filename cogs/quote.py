import aiohttp
from discord.ext import commands

class Quote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="quote")
    async def quote(self, ctx):
        """Fetch a random famous quote from ZenQuotes API."""
        url = "https://zenquotes.io/api/random"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Couldn't fetch a quote right now.")
                    return
                data = await resp.json()
                # data is a list with one dict element
                quote = data[0].get('q')
                author = data[0].get('a')
                await ctx.send(f"💬 \"{quote}\" — {author}")

async def setup(bot):
    await bot.add_cog(Quote(bot))
