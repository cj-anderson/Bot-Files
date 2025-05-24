import random
from discord.ext import commands
from .points import get_points, set_points  # ✅ Use shared point logic

class CoinFlip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='flip')
    async def flip(self, ctx, call: str, wager: int = 0):
        user_id = ctx.author.id
        call = call.lower()
        if call not in ['heads', 'tails']:
            await ctx.send("❌ Please choose 'heads' or 'tails' as your call.")
            return

        current_points = get_points(user_id)

        if wager < 0:
            await ctx.send("❌ Wager can't be negative.")
            return

        if wager > current_points:
            await ctx.send(f"❌ You only have {current_points} points to wager.")
            return

        result = random.choice(['heads', 'tails'])

        if wager == 0:
            if current_points == 0 and call == result:
                set_points(user_id, 1)
                await ctx.send(f"🎉 You called **{call}** and it was **{result}**! You had no points, so you gain 1 point.")
            else:
                await ctx.send(f"🪙 You called **{call}** and it was **{result}**. Your points remain at {current_points}.")
            return

        if call == result:
            new_points = current_points + wager
            set_points(user_id, new_points)
            await ctx.send(f"🎉 You won! The coin was **{result}**. You gained {wager} points and now have {new_points} points.")
        else:
            new_points = current_points - wager
            set_points(user_id, new_points)
            await ctx.send(f"😢 You lost! The coin was **{result}**. You lost {wager} points and now have {new_points} points.")



    @commands.command(name='slots')
    async def slots(self, ctx, wager: int):
        user_id = ctx.author.id
        current_points = get_points(user_id)

        if wager <= 0:
            await ctx.send("❌ You must wager at least 1 point.")
            return

        if wager > current_points:
            await ctx.send(f"❌ You only have {current_points} points to wager.")
            return

        symbols = ['🍒', '🍋', '🍊', '🍉', '⭐', '7️⃣', '💎']
        spin = [random.choice(symbols) for _ in range(3)]

        if spin[0] == spin[1] == spin[2]:
            winnings = wager * 3
            result_msg = "Jackpot! All three match!"
        elif spin[0] == spin[1] or spin[1] == spin[2] or spin[0] == spin[2]:
            winnings = int(wager * 1.5)
            result_msg = "Nice! Two of a kind!"
        else:
            winnings = -wager
            result_msg = "No match. Better luck next time!"

        new_points = max(0, current_points + winnings)
        set_points(user_id, new_points)

        spin_display = ' | '.join(spin)
        if winnings > 0:
            await ctx.send(f"🎰 {spin_display}\n{result_msg} You won {winnings} points! You now have {new_points} points.")
        else:
            await ctx.send(f"🎰 {spin_display}\n{result_msg} You lost {wager} points. You now have {new_points} points.")

    @commands.command(name='rps')
    async def rock_paper_scissors(self, ctx, choice: str, wager: int = 0):
        choice = choice.lower()
        user_id = ctx.author.id
        current_points = get_points(user_id)
        valid = ['rock', 'paper', 'scissors']

        if choice not in valid:
            await ctx.send("❌ Choose rock, paper, or scissors.")
            return

        if wager < 0:
            await ctx.send("❌ Wager can't be negative.")
            return

        if wager > current_points:
            await ctx.send(f"❌ You only have {current_points} points to wager.")
            return

        bot_choice = random.choice(valid)
        result = (
            'draw' if choice == bot_choice else
            'win' if (choice == 'rock' and bot_choice == 'scissors') or
                     (choice == 'paper' and bot_choice == 'rock') or
                     (choice == 'scissors' and bot_choice == 'paper') else
            'lose'
        )

        if wager == 0:
            await ctx.send(f"🤜 You chose **{choice}**, I chose **{bot_choice}**. It's a **{result}**! No points changed.")
            return

        if result == 'win':
            new_points = current_points + wager
            set_points(user_id, new_points)
            await ctx.send(f"🎉 You won! You chose **{choice}**, I chose **{bot_choice}**. You gained {wager} points. Now you have {new_points}.")
        elif result == 'lose':
            new_points = current_points - wager
            set_points(user_id, new_points)
            await ctx.send(f"😢 You lost! You chose **{choice}**, I chose **{bot_choice}**. You lost {wager} points. Now you have {new_points}.")
        else:
            await ctx.send(f"🤝 It's a draw! You chose **{choice}**, I chose **{bot_choice}**. Points unchanged.")

    @commands.command(name='guess')
    async def number_guess(self, ctx, guess: int, wager: int = 0):
        user_id = ctx.author.id
        current_points = get_points(user_id)

        if wager < 0:
            await ctx.send("❌ Wager can't be negative.")
            return

        if wager > current_points:
            await ctx.send(f"❌ You only have {current_points} points to wager.")
            return

        if guess < 1 or guess > 10:
            await ctx.send("❌ Please guess a number between 1 and 10.")
            return

        if wager == 0:
            await ctx.send("❌ You need to wager points to play this game.")
            return

        secret = random.randint(1, 10)

        if guess == secret:
            winnings = wager * 3
            new_points = current_points + winnings
            set_points(user_id, new_points)
            await ctx.send(f"🎉 Correct! The number was {secret}. You won {winnings} points and now have {new_points} points.")
        else:
            new_points = current_points - wager
            set_points(user_id, new_points)
            await ctx.send(f"😢 Wrong! The number was {secret}. You lost {wager} points and now have {new_points} points.")

async def setup(bot):
    await bot.add_cog(CoinFlip(bot))
