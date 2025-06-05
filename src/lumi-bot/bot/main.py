import asyncio

import discord
from discord.ext import commands

from config import DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
cogs = [
    "bot.commands.geral",
    "bot.commands.voice",
]


@bot.event
async def on_ready():
    bot.load_extensions(*cogs)
    print("Loaded all cogs")
    print(f"Bot conectado como {bot.user}")


def run_bot():
    if DISCORD_TOKEN is None:
        raise ValueError("DISCORD_TOKEN is not set in the environment variables.")
    bot.run(DISCORD_TOKEN)


async def start_bot() -> None:
    if DISCORD_TOKEN is None:
        raise ValueError("DISCORD_TOKEN is not set in the environment variables.")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_bot)
