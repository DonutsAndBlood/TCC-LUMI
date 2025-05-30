import discord
from discord.ext import commands

from .config import DISCORD_TOKEN
from .whisper import Model

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


def start_bot():
    Model.load_model()
    bot.run(DISCORD_TOKEN)
