import discord
from discord.ext import commands
from bot.config import DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
cogs_loaded = False

@bot.event
async def on_ready():
    global cogs_loaded
    if not cogs_loaded:
        for cog in ["bot.commands.geral", "bot.commands.voice", "bot.commands.tradutor"]:
            try:
                await bot.load_extension(cog)
                print(f"Loaded {cog}")
            except Exception as e:
                print(f"Failed to load {cog}: {e}")
        cogs_loaded = True
    print(f"Bot conectado como {bot.user}")

bot.run(DISCORD_TOKEN)