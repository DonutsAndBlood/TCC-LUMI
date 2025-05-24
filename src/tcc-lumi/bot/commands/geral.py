from discord.ext import commands
import discord

class Geral(commands.Cog, name="Comandos Gerais"):  # Categoriza o Cog como "Comandos Gerais"
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="oi", help="Receba uma saudação do bot")
    async def oi(self, ctx):
        await ctx.send(f"E aí, {ctx.author.display_name}! Tudo certo por aqui.💡")

    @commands.command(name="ping", help="Veja a latência do bot")
    async def ping(self, ctx):
        await ctx.send(f"Pong! 🏓 Latência: `{round(self.bot.latency * 1000)}ms`")

    @commands.command(name="ajuda", help="Mostra os comandos disponíveis")
    async def ajuda(self, ctx):
        embed = discord.Embed(
            title="Comandos Disponíveis",
            description="Aqui estão os comandos básicos do bot:",
            color=discord.Color.blue()
        )
        embed.add_field(name="!oi", value="Receba uma saudação do bot", inline=False)
        embed.add_field(name="!ping", value="Veja a latência do bot", inline=False)
        embed.add_field(name="!ajuda", value="Mostra essa mensagem de ajuda", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="desligar", help="Desliga o bot")
    async def desligar(self, ctx):
        await ctx.send("Indo dormir... 😴")
        await self.bot.close()

def setup(bot):
    print("Geral carregando")
    bot.add_cog(Geral(bot))
    print("Geral carregado")
    return [Geral(bot)]