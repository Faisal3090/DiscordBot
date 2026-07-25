import os
import asyncio
import threading
import requests
import discord
import uvicorn

from fastapi import FastAPI
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK = os.getenv("N8N_WEBHOOK")

app = FastAPI()


@app.get("/")
def root():
    return {"status": "Discord Bot Running"}


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
        print("=" * 50)
        print("Calling webhook...")
        print("Webhook URL:", WEBHOOK)
        print("Contest:", slug)

        response = requests.post(
            WEBHOOK,
            json={"contest_slug": slug},
            timeout=60
        )

        print("Status Code:", response.status_code)
        print("Response Body:", response.text)
        print("=" * 50)

    except Exception as e:
        print("Webhook Error:", str(e))


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


def run_api():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )


threading.Thread(
    target=run_api,
    daemon=True
).start()


bot.run(TOKEN)