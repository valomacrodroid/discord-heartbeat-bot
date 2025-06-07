import os
import discord
from discord.ext import commands, tasks

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1378040995102588989  # vagy int(os.getenv("DISCORD_CHANNEL_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"Bejelentkezve: {bot.user}")
    send_heartbeat.start()

@bot.slash_command(name="ping", description="Pong vissza!")
async def ping(ctx):
    await ctx.respond("Pong!")

@tasks.loop(hours=1)
async def send_heartbeat():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("Jelenleg még aktív vagyok.")
    else:
        print(f"Nem találom a csatornát ID alapján: {CHANNEL_ID}")

if __name__ == "__main__":
    bot.run(TOKEN)
