import discord
from discord.ext import commands
from commands import geral, voice
from config import DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
 
async def setup():
    bot.add_cog(geral.Geral(bot))
    bot.add_cog(voice.Voice(bot))

if __name__ == "__main__":
    bot.loop.create_task(setup())
    bot.run(DISCORD_TOKEN)
