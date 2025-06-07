import os
import asyncio
from discord import Client

TOKEN = os.getenv("DISCORD_TOKEN")
client = Client()

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await asyncio.sleep(5)
    await client.close()

if __name__ == "__main__":
    client.run(TOKEN)
