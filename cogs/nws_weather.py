import discord
from discord.ext import commands
import aiohttp

class NWSWeather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='nwsweather')
    async def nwsweather(self, ctx, *, location: str):
        """Get NWS forecast for a given city or county + state."""
        await ctx.send(f"🔍 Looking up weather for **{location}**...")

        headers = {"User-Agent": "discord-weather-bot"}
        geocode_url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"

        async with aiohttp.ClientSession() as session:
            async with session.get(geocode_url, headers=headers) as geo_resp:
                if geo_resp.status != 200:
                    await ctx.send("❌ Failed to geocode location.")
                    return
                geo_data = await geo_resp.json()
                if not geo_data:
                    await ctx.send("❌ Location not found.")
                    return
                lat = geo_data[0]['lat']
                lon = geo_data[0]['lon']

            points_url = f"https://api.weather.gov/points/{lat},{lon}"
            async with session.get(points_url, headers=headers) as points_resp:
                if points_resp.status != 200:
                    await ctx.send("❌ Could not get forecast data from NWS.")
                    return
                points_data = await points_resp.json()
                forecast_url = points_data['properties'].get('forecast')
                if not forecast_url:
                    await ctx.send("⚠️ No forecast data available.")
                    return

            async with session.get(forecast_url, headers=headers) as forecast_resp:
                forecast_data = await forecast_resp.json()
                periods = forecast_data['properties']['periods']
                first = periods[0]
                await ctx.send(f"🌤️ **{first['name']}**: {first['detailedForecast']}")

# Required to register the cog
async def setup(bot):
    await bot.add_cog(NWSWeather(bot))
