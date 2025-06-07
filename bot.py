import os
import discord
from discord.ext import commands, tasks

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1378040995102588989

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# Lista a státuszokhoz
status_list = [
    discord.Game(name="Maybe Im Back?"),
    discord.Activity(type=discord.ActivityType.listening, name="Miyuki back 😍"),
    discord.Activity(type=discord.ActivityType.watching, name="Miyuki welcome 🥰🥰❤️"),
]

current_status = 0  # Index a status_list-ben

@bot.event
async def on_ready():
    print(f"Bejelentkezve: {bot.user}")
    send_heartbeat.start()
    cycle_status.start()

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

@tasks.loop(minutes=10)
async def cycle_status():
    global current_status
    await bot.change_presence(activity=status_list[current_status])
    current_status = (current_status + 1) % len(status_list)

if __name__ == "__main__":
    bot.run(TOKEN)
