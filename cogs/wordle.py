import discord
from discord.ext import commands
import random
import json
import os
from datetime import datetime

WORD_LIST = []
with open("wordlist.txt") as f:
    WORD_LIST = [line.strip().lower() for line in f if len(line.strip()) == 5]

STATE_FILE = "daily_wordle.json"
DAILY_WORD_FILE = "daily_word.json"

class Wordle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_words = self.load_daily_words()
        self.today = datetime.utcnow().strftime("%Y-%m-%d")
        # Initialize today's word if not set
        if self.today not in self.daily_words:
            seed = sum(ord(c) for c in self.today)
            random.seed(seed)
            self.daily_words[self.today] = random.choice(WORD_LIST)
            self.save_daily_words()
        self.delete_guesses = False
        self.games = {}
        self.load_state()

    def load_state(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                self.games = json.load(f)

    def save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.games, f, indent=2)

    def load_daily_words(self):
        if os.path.exists(DAILY_WORD_FILE):
            with open(DAILY_WORD_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_daily_words(self):
        with open(DAILY_WORD_FILE, "w") as f:
            json.dump(self.daily_words, f, indent=2)

    def get_word_of_the_day(self):
        return self.daily_words.get(self.today)

    def get_hint(self, guess, target):
        result = ""
        for i in range(5):
            if guess[i] == target[i]:
                result += "🟩"
            elif guess[i] in target:
                result += "🟨"
            else:
                result += "⬛"
        return result

    def format_result(self, guesses, answer):
        return "\n".join([self.get_hint(g, answer) for g in guesses])

    @commands.command()
    async def startwordle(self, ctx):
        user_id = str(ctx.author.id)
        today = self.today

        game = self.games.get(user_id)
        if game and game.get("date") == today:
            await ctx.send("You've already started today's Wordle!")
            return

        # Create new game state
        self.games[user_id] = {
            "date": today,
            "attempts": 0,
            "guesses": [],
            "complete": False
        }
        self.save_state()
        await ctx.send("✅ Wordle started! Use `!wguess yourword` to make a guess.")

    @commands.command()
    async def wguess(self, ctx, word: str):
        word = word.lower()
        user_id = str(ctx.author.id)
        today = self.today

        game = self.games.get(user_id)
        if not game or game.get("date") != today:
            await ctx.send("Start today's Wordle with `!startwordle` first!")
            return
        if game.get("complete"):
            await ctx.send("✅ You've already completed today's Wordle!")
            return
        if len(word) != 5 or word not in WORD_LIST:
            await ctx.send("❌ Invalid word.")
            return

        answer = self.get_word_of_the_day()
        hint = self.get_hint(word, answer)

        game["guesses"].append(word)
        game["attempts"] += 1
        self.save_state()

        await ctx.send(f"{ctx.author.mention} {hint} ({game['attempts']}/6)")

        if word == answer:
            game["complete"] = True
            self.save_state()
            result_block = self.format_result(game["guesses"], answer)
            await ctx.send(f"🎉 You solved it in {game['attempts']} tries!\n```\n{result_block}\n```")
        elif game["attempts"] >= 6:
            game["complete"] = True
            self.save_state()
            result_block = self.format_result(game["guesses"], answer)
            await ctx.send(f"❌ Out of attempts! The word was **{answer}**.\n```\n{result_block}\n```")

        if self.delete_guesses:
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                await ctx.send("I don't have permission to delete messages!", delete_after=5)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def toggle_delete_guesses(self, ctx):
        self.delete_guesses = not self.delete_guesses
        status = "enabled" if self.delete_guesses else "disabled"
        await ctx.send(f"Guess message deletion is now **{status}**.")

    # Optional: command to reveal yesterday's word
    # @commands.command()
    # async def yesterdayword(self, ctx):
    #     from datetime import timedelta
    #     yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    #     word = self.daily_words.get(yesterday)
    #     if word:
    #         await ctx.send(f"Yesterday's Wordle answer was **{word}**.")
    #     else:
    #         await ctx.send("No word found for yesterday.")

async def setup(bot):
    await bot.add_cog(Wordle(bot))
