import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"Bejelentkezve: {bot.user}")

@bot.slash_command(name="ping", description="Pong vissza!")
async def ping(ctx):
    await ctx.respond("Pong!")

if __name__ == "__main__":
    bot.run(TOKEN)
