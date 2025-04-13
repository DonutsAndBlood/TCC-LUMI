from discord.ext import commands
import discord

class Voice(commands.Cog, name="Comandos de Voz"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="entrar", help="Faz o bot entrar no canal de voz do usuário")
    async def entrar(self, ctx):
        print("Comando !entrar chamado")
        
        if ctx.author.voice:
            canal = ctx.author.voice.channel
            print(f"Usuário está no canal: {canal}")

            if ctx.voice_client is not None:
                print("Bot já está em um canal de voz, movendo...")
                await ctx.voice_client.move_to(canal)
            else:
                print("Bot conectando no canal...")
                try:
                    await canal.connect()
                except Exception as e:
                    await ctx.send("Erro ao tentar conectar ao canal de voz.")
                    print(f"Erro ao conectar: {e}")
        else:
            print("Usuário não está em canal de voz")  # DEBUG
            await ctx.send("⚠️ Você precisa estar em um canal de voz pra eu entrar!")

async def setup(bot):
    await bot.add_cog(Voice(bot))
