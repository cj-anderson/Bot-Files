import json
import os
from discord.ext import commands

POINTS_FILE = 'points.json'

def get_points(user_id):
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, 'r') as f:
            points = json.load(f)
        return points.get(str(user_id), 0)
    return 0

def set_points(user_id, amount):
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, 'r') as f:
            points = json.load(f)
    else:
        points = {}

    points[str(user_id)] = amount
    with open(POINTS_FILE, 'w') as f:
        json.dump(points, f, indent=4)

class PointsManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='points')
    async def check_points(self, ctx):
        """Check your current points."""
        user_id = ctx.author.id
        current = get_points(user_id)
        await ctx.send(f"💰 You currently have {current} points.")

    @commands.command(name='setpoints')
    @commands.has_permissions(administrator=True)
    async def admin_set_points(self, ctx, member: commands.MemberConverter, amount: int):
        """[Admin] Set a user's point balance directly."""
        set_points(member.id, amount)
        await ctx.send(f"✅ Set {member.display_name}'s points to {amount}.")

    @commands.command(name='givepoints')
    @commands.has_permissions(administrator=True)
    async def admin_give_points(self, ctx, member: commands.MemberConverter, amount: int):
        """[Admin] Add points to a user's balance."""
        current = get_points(member.id)
        set_points(member.id, current + amount)
        await ctx.send(f"✅ Gave {amount} points to {member.display_name}. New balance: {current + amount}.")

# Setup function to register the Cog
async def setup(bot):
    await bot.add_cog(PointsManager(bot))
