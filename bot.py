import os
import asyncio
import requests
import discord

from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK = os.getenv("N8N_WEBHOOK")


class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()


bot = MyBot()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


def trigger_webhook(slug):
    try:
        response = requests.post(
            WEBHOOK,
            json={
                "contest_slug": slug
            },
            timeout=60
        )

        print(f"n8n Response: {response.status_code}")

    except Exception as e:
        print(f"Webhook error: {e}")


@bot.tree.command(
    name="update",
    description="Update HackerRank leaderboard"
)
async def update(interaction: discord.Interaction, contest_slug: str):

    await interaction.response.send_message(
        f"🔄 Started updating the leaderboard for **{contest_slug}**..."
    )

    asyncio.create_task(
        asyncio.to_thread(trigger_webhook, contest_slug)
    )


bot.run(TOKEN)