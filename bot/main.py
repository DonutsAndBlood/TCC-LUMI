import discord
from discord.ext import commands
from bot.commands import geral
from bot.config import DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

async def run_bot():
    await bot.add_cog(geral.Geral(bot))
    await bot.start(DISCORD_TOKEN)