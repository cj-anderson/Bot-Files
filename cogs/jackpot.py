import json
import os
import random
from cogs.points import get_points, set_points
from datetime import datetime
from discord.ext import commands

JACKPOT_FILE = "jackpot.json"

class DailyJackpot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jackpot = self.load_jackpot()

    def load_jackpot(self):
        if os.path.exists(JACKPOT_FILE):
            with open(JACKPOT_FILE, "r") as f:
                return json.load(f)
        return {
            "date": datetime.now().date().isoformat(),
            "pool": 0,
            "contributors": {}
        }

    def save_jackpot(self):
        with open(JACKPOT_FILE, "w") as f:
            json.dump(self.jackpot, f, indent=4)

    @commands.command(name="jackpot")
    async def contribute(self, ctx, amount: int):
        """Contribute to today's jackpot."""
        user_id = str(ctx.author.id)
        today = datetime.now().date().isoformat()

        if amount < 1:
            await ctx.send("❌ You must contribute at least 1 point.")
            return

        current_points = get_points(user_id)
        if current_points < amount:
            await ctx.send(f"❌ You only have {current_points} points.")
            return

        # Reset jackpot if it's a new day
        if self.jackpot["date"] != today:
            self.jackpot = {
                "date": today,
                "pool": 0,
                "contributors": {}
            }

        set_points(user_id, current_points - amount)
        self.jackpot["pool"] += 2.5 * amount
        self.jackpot["contributors"][user_id] = self.jackpot["contributors"].get(user_id, 0) + amount
        self.save_jackpot()

        await ctx.send(f"💰 You contributed {amount} points to today's jackpot. Total pool: {self.jackpot['pool']}.")

    @commands.command(name="drawjackpot")
    @commands.has_permissions(administrator=True)
    async def draw_jackpot(self, ctx):
        """Draw a daily jackpot winner from contributors."""
        today = datetime.now().date().isoformat()

        if self.jackpot["date"] != today:
            await ctx.send("❌ No contributions yet today.")
            return

        contributors = list(self.jackpot["contributors"].keys())
        if not contributors:
            await ctx.send("❌ No one has contributed to the jackpot today.")
            return

        winner_id = random.choice(contributors)
        winnings = self.jackpot["pool"]

        current = get_points(winner_id)
        set_points(winner_id, current + winnings)

        await ctx.send(f"🎉 <@{winner_id}> has won today's jackpot of {winnings} points!")

        # Reset for next day
        self.jackpot = {
            "date": today,
            "pool": 0,
            "contributors": {}
        }
        self.save_jackpot()

async def setup(bot):
    await bot.add_cog(DailyJackpot(bot))
