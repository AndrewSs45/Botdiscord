import discord
from discord import app_commands
from discord.ext import commands


class SlashCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! {latency}ms")

    @app_commands.command(name="search", description="Search the web with AI")
    @app_commands.describe(query="What do you want to search?")
    async def search(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        from skills.internet_search import search_web
        results = await search_web(query)
        if results:
            text = "\n".join([f"• {r.get('title', '?')}: {r.get('link', '?')}" for r in results[:3]])
        else:
            text = "No results found."
        await interaction.edit_original_response(content=text[:1990])

    @app_commands.command(name="weather", description="Get weather for a city")
    @app_commands.describe(city="City name")
    async def weather(self, interaction: discord.Interaction, city: str):
        await interaction.response.defer()
        from skills.weather import get_weather
        result = await get_weather(city)
        await interaction.edit_original_response(content=result[:1990])

    @app_commands.command(name="time", description="Get current time for a timezone")
    @app_commands.describe(timezone="IANA timezone (e.g. America/Bogota)")
    async def time(self, interaction: discord.Interaction, timezone: str):
        from skills.time_skill import get_time_for_timezone
        result = get_time_for_timezone(timezone)
        await interaction.response.send_message(result[:1990])


async def setup(bot: commands.Bot):
    await bot.add_cog(SlashCommands(bot))
