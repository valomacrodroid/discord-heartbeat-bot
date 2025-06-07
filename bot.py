import os
import os
import discord
from discord import app_commands  # így importáld explicit az app_commands-ot
from discord.ext import tasks
import platform
import psutil
import time
import random
import asyncio
from datetime import datetime, time as dt_time

VERSION = "Miyuki Bot v2.4"
OWNER_ID = 586431935165759491
start_time = time.time()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1378040995102588989

intents = discord.Intents.default()
intents.members = True  # fontos!

bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

status_list = [
    discord.Game(name="Maybe Im Back?"),
    discord.Activity(type=discord.ActivityType.listening, name="Miyuki back 😍"),
    discord.Activity(type=discord.ActivityType.watching, name="Miyuki welcome 🥰🥰❤️"),
]
current_status = 0

active_ping_tasks = {}
active_timer_tasks = {}

# --- Segédfüggvény az idő ellenőrzésére ---
def is_within_active_hours():
    now = datetime.now().time()
    start = dt_time(10, 0)  # 10:00
    end = dt_time(15, 0)    # 15:00
    return start <= now < end

# --- Feladat, ami figyeli az aktív időszakot, és leállítja a botot ha kilép az időablakból ---
async def monitor_active_hours():
    while True:
        if not is_within_active_hours():
            print("Kívül vagyunk az aktív időablakon (10:00-15:00), leállítom a botot.")
            await bot.close()
            break
        await asyncio.sleep(60)  # minden percben ellenőrzünk

@bot.event
async def on_ready():
    print(f"Bejelentkezve: {bot.user}")

    # Ha most nem az aktív időszakban vagyunk, akkor leállunk azonnal
    if not is_within_active_hours():
        print("Nem az aktív időszakban indult a bot, leállítom.")
        await bot.close()
        return

    send_heartbeat.start()
    cycle_status.start()
    asyncio.create_task(monitor_active_hours())  # Indítjuk az időfigyelést
    await tree.sync()  # szinkronizálja a slash parancsokat

# --- Parancsok és egyéb funkciók ugyanazok, változatlanul ---

@tree.command(name="info", description="Információk a Miyuki botról")
async def info(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("Ezt a parancsot csak Mizuki használhatja. 🚫", ephemeral=True)
        return

    uptime_seconds = int(time.time() - start_time)
    uptime_string = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s"
    process = psutil.Process()
    mem_mb = process.memory_info().rss / 1024 / 1024
    cpu_percent = process.cpu_percent(interval=0.1)

    embed = discord.Embed(
        title="🤖 Miyuki Bot Információk",
        description=VERSION,
        color=discord.Color.blue()
    )
    embed.add_field(name="🕒 Uptime", value=uptime_string, inline=True)
    embed.add_field(name="💻 Python verzió", value=platform.python_version(), inline=True)
    embed.add_field(name="🖥️ Memóriahasználat", value=f"{mem_mb:.2f} MB", inline=True)
    embed.add_field(name="⚙️ CPU kihasználtság", value=f"{cpu_percent:.1f} %", inline=True)
    embed.add_field(name="📡 Szerver neve", value=interaction.guild.name if interaction.guild else "Privát üzenet", inline=True)
    embed.add_field(name="👥 Felhasználók száma", value=str(sum(g.member_count for g in bot.guilds)), inline=True)
    embed.set_footer(text="Csak Miyuki számára elérhető parancs.")
    await interaction.response.send_message(embed=embed)

@tree.command(name="ping", description="Pong vissza!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@tree.command(name="whoami", description="Megmutatja, ki vagy (viccesen).")
async def whoami(interaction: discord.Interaction):
    user = interaction.user
    funny_messages = [
        f"Lássuk csak, ki is vagy te, {user.display_name}... 🧐",
        f"A nagy Mizuki vizsgálja a kiléted, {user.mention}! 🔍",
        f"Kíváncsi vagy magadra, {user.display_name}? Íme az aktád: 📂",
        f"Nyisd ki a dossziét... {user.display_name}, te következel! 🗃️",
    ]

    embed = discord.Embed(title="🆔 Whoami eredmény", color=discord.Color.purple())
    embed.add_field(name="Név", value=f"{user.display_name} ({user.name}#{user.discriminator})", inline=False)
    embed.add_field(name="User ID", value=user.id, inline=False)
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    embed.add_field(name="Fiók létrehozva", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    await interaction.response.send_message(random.choice(funny_messages), embed=embed)

@tree.command(name="pingme", description="Pingel X perc múlva (max 120 perc).")
@discord.app_commands.describe(minutes="Hány perc múlva pingeljen?")
async def pingme(interaction: discord.Interaction, minutes: int):
    if minutes <= 0 or minutes > 120:
        await interaction.response.send_message("⛔ Csak 1 és 120 perc közötti időt adhatsz meg!", ephemeral=True)
        return

    if interaction.user.id in active_ping_tasks:
        active_ping_tasks[interaction.user.id].cancel()

    async def ping_task():
        try:
            await asyncio.sleep(minutes * 60)
            funny_pings = [
                f"⏰ Ahogy kérted, itt a pinged, {interaction.user.mention}! Mizuki sosem felejt. 😉",
                f"⌛ Idő letelt! Itt vagyok, {interaction.user.mention}! 🛎️",
                f"🔔 DING DING! {interaction.user.mention}, itt az idő! Mizuki stílusban természetesen.",
            ]
            await interaction.followup.send(random.choice(funny_pings))
        except asyncio.CancelledError:
            pass

    task = asyncio.create_task(ping_task())
    active_ping_tasks[interaction.user.id] = task

    await interaction.response.send_message(f"✅ Oké {interaction.user.display_name}, {minutes} perc múlva pingellek!")

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

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)  # így használd

if __name__ == "__main__":
    bot.run(TOKEN)
