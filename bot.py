import os
import discord
from discord.ext import commands, tasks
import platform
import psutil
import time

VERSION = "Miyuki Bot v2.3"
OWNER_ID = 586431935165759491
start_time = time.time()

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

@bot.slash_command(name="info", description="Információk a Miyuki botról")
async def info(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.respond("Ezt a parancsot csak Mizuki használhatja. 🚫", ephemeral=True)
        return

    # Uptime kiszámítása
    uptime_seconds = int(time.time() - start_time)
    uptime_string = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s"

    # Memória és CPU
    process = psutil.Process()
    mem_mb = process.memory_info().rss / 1024 / 1024
    cpu_percent = process.cpu_percent(interval=0.1)

    # Embed létrehozás
    embed = discord.Embed(
        title="🤖 Miyuki Bot Információk",
        description=f"{VERSION}",
        color=discord.Color.blue()
    )
    embed.add_field(name="🕒 Uptime", value=uptime_string, inline=True)
    embed.add_field(name="💻 Python verzió", value=platform.python_version(), inline=True)
    embed.add_field(name="🖥️ Memóriahasználat", value=f"{mem_mb:.2f} MB", inline=True)
    embed.add_field(name="⚙️ CPU kihasználtság", value=f"{cpu_percent:.1f} %", inline=True)
    embed.add_field(name="📡 Szerver neve", value=ctx.guild.name if ctx.guild else "Privát üzenet", inline=True)
    embed.add_field(name="👥 Felhasználók száma", value=str(sum(g.member_count for g in bot.guilds)), inline=True)
    embed.set_footer(text="Csak Miyuki számára elérhető parancs.")

    await ctx.respond(embed=embed)

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
