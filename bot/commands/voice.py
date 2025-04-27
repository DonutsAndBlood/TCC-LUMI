import discord
from discord.ext import commands
import asyncio
import os
from pydub import AudioSegment, silence

connections = {}

class Voice(commands.Cog, name="Comandos de Voz"):
    def __init__(self, bot):
        self.bot = bot
        self.gravando = False

    @commands.command()
    async def gravar(self, ctx):
        voice = ctx.author.voice

        if not voice:
            await ctx.send("Você não está em um canal de voz!")
            return

        vc = await voice.channel.connect()
        connections.update({ctx.guild.id: vc})

        await ctx.send("Iniciando gravação contínua...")
        self.gravando = True

        await self.gravar_loop(ctx, vc)

    async def gravar_loop(self, ctx, vc):
        while self.gravando:
            sink = discord.sinks.WaveSink()

            # Começar a gravar
            vc.start_recording(
                sink,
                self.once_done,
                ctx
            )
            
            await asyncio.sleep(5)  # ← ajustar tempo ocioso
            
            if self.gravando:
                vc.stop_recording()

            # Esperar o sink processar
            await asyncio.sleep(1)  # Pequeno delay para evitar conflito

    async def once_done(self, sink: discord.sinks.WaveSink, ctx: discord.context, *args):
        for user_id, audio in sink.audio_data.items():
            file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'temp_audio', f'temp_{user_id}.wav')
            
            # Salvar o arquivo corretamente na pasta temp_audio
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(audio.file.getbuffer())

            # Se ainda está gravando, recomeçar a gravar
        if self.gravando:
            await self.gravar_loop(ctx, sink.vc)

    @commands.command()
    async def parar(self, ctx):
        self.gravando = False

        # Verificar se está gravando antes de tentar parar
        if ctx.guild.id in connections:
            vc = connections[ctx.guild.id]
            vc.stop_recording()
            await vc.disconnect()
            del connections[ctx.guild.id]

        await ctx.send("Gravação finalizada!")

async def setup(bot):
    await bot.add_cog(Voice(bot))
