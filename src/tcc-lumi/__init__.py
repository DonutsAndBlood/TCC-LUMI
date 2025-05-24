import discord
from discord.ext import commands

from bot.config import DISCORD_TOKEN
from bot.whisper import Model

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
cogs = [
    "bot.commands.geral",
    "bot.commands.voice",
    "bot.commands.tradutor",
]


@bot.event
async def on_ready():
    try:
        bot.load_extensions(*cogs)
        print(f"Loaded all cogs")
    except Exception as e:
        print(f"Failed to load: {e}")
    print(f"Bot conectado como {bot.user}")


Model.load_model()
bot.run(DISCORD_TOKEN)
