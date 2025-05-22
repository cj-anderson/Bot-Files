import re
import os
import discord
import random
import logging
from cogs.jackpot import DailyJackpot
from discord.ext import commands
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)

# Load env before anything else
load_dotenv()

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
    


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    # Load all cogs directly under cogs/
    for file in os.listdir("./cogs"):
        if file.endswith(".py") and not file.startswith("__"):
            ext = f"cogs.{file[:-3]}"
            try:
                await bot.load_extension(ext)
                print(f"Loaded {ext}")
            except Exception as e:
                print(f"Failed to load {ext}: {e}")

    # Load all cogs inside subfolders of cogs/
    for folder in os.listdir("./cogs"):
        folder_path = os.path.join("./cogs", folder)
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                if file.endswith(".py") and not file.startswith("__"):
                    ext = f"cogs.{folder}.{file[:-3]}"
                    try:
                        await bot.load_extension(ext)
                        print(f"Loaded {ext}")
                    except Exception as e:
                        print(f"Failed to load {ext}: {e}")

@bot.command()
async def hello(ctx):
    await ctx.send("hoi!")

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("ERROR: Discord token not found in environment variables.")
    else:
        try:
            bot.run(TOKEN)
        except discord.errors.LoginFailure as e:
            print(f"login failed: {e}")
        except Exception as e:
            print(f"error occurred: {e}")
