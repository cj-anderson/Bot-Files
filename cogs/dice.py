import random
import re
from discord.ext import commands

class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='roll')
    async def roll(self, ctx, *, args: str):
        """
        Rolls multiple dice groups with drop lowest.
        Usage example:
          !roll 4d6d1 6 3d20d1 2
        Rolls 6 groups of 4d6 drop lowest 1, and 2 groups of 3d20 drop lowest 1.
        """
        tokens = args.split()
        if len(tokens) % 2 != 0:
            await ctx.send("❌ Please provide pairs of dice and group counts, e.g. `4d6d1 6 3d20d1 2`.")
            return

        pattern = re.compile(r'(\d+)d(\d+)(?:d(\d+))?')

        try:
            response_lines = []

            for i in range(0, len(tokens), 2):
                dice_str = tokens[i].lower()
                groups = int(tokens[i+1])

                match = pattern.fullmatch(dice_str)
                if not match:
                    raise ValueError(f"Invalid dice format: {dice_str}")

                num = int(match.group(1))
                die = int(match.group(2))
                drop = int(match.group(3)) if match.group(3) else 0

                if num < 1 or die < 1 or drop < 0 or drop >= num:
                    raise ValueError(f"Invalid numbers in dice: {dice_str}")

                # Header line before this dice group results
                drop_text = f" drop lowest {drop}" if drop > 0 else ""
                group_word = "group" if groups == 1 else "groups"
                response_lines.append(f"Rolling {num}d{die}{drop_text} — {groups} {group_word}:")

                for g in range(1, groups + 1):
                    rolls = [random.randint(1, die) for _ in range(num)]
                    sorted_rolls = sorted(rolls)
                    kept_rolls = sorted_rolls[drop:]
                    total = sum(kept_rolls)

                    line = (f"Group {g}: Rolls: [{', '.join(map(str, rolls))}], "
                            f"Dropped: [{', '.join(map(str, sorted_rolls[:drop]))}], "
                            f"Kept: [{', '.join(map(str, kept_rolls))}] (Total: **{total}**)")
                    response_lines.append(line)

                response_lines.append("")  # blank line for spacing between groups

            await ctx.send("\n".join(response_lines))

        except ValueError as e:
            await ctx.send(f"❌ {e}")

async def setup(bot):
    await bot.add_cog(Dice(bot))
