from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check the bot's response time."""
        latency = round(self.bot.latency * 1000)  # Convert seconds to milliseconds
        await ctx.send(f"🏓 Pong! Bot latency is {latency}ms.")

async def setup(bot):
    await bot.add_cog(Ping(bot))
