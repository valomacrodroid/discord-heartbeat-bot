import os
import asyncio
import discord
from discord import Intents, Client

TOKEN = os.getenv("DISCORD_TOKEN")

intents = Intents.default()
client = Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await asyncio.sleep(5)
    await client.close()

if __name__ == "__main__":
    client.run(TOKEN)
