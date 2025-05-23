import asyncio
import os

import discord
from discord.ext import commands
from pydub import AudioSegment, silence
from bot.voice.transcriber import transcribe_audio

connections = {}


class Voice(commands.Cog, name="Comandos de Voz"):
    def __init__(self, bot):
        self.bot = bot
        self.gravando = False

    @commands.command()
    async def gravar(self, ctx: discord.ApplicationContext):
        if isinstance(ctx.author, discord.User):
            return

        voice = ctx.author.voice

        if voice is None or voice.channel is None:
            await ctx.send("Você não está em um canal de voz!")
            return

        vc: discord.VoiceClient = await voice.channel.connect()
        connections.update({ctx.guild.id: vc})

        await ctx.send("Iniciando gravação contínua...")
        self.gravando = True

        await self.gravar_loop(ctx, vc)

    async def gravar_loop(self, ctx, vc: discord.VoiceClient):
        while self.gravando:
            sink = discord.sinks.WaveSink()

            # Começar a gravar
            try:
                vc.start_recording(sink, self.once_done, ctx)
            except:
                await ctx.send("Já está gravando")
                await asyncio.sleep(10)
                continue

            await asyncio.sleep(10)  # TEMPO DE GRAVAÇÃO

            if self.gravando:
                vc.stop_recording()

            # Esperar o sink processar
            await asyncio.sleep(1)

    async def once_done(
        self,
        sink: discord.sinks.WaveSink,
        ctx: discord.context,
        *args,
    ):
        for user_id, audio in sink.audio_data.items():
            file_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "temp_audio",
                f"temp_{user_id}.wav",
            )

            # Salvar o arquivo corretamente na pasta temp_audio
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(audio.file.getbuffer())

            texto = transcribe_audio(file_path)
            await ctx.send(f"🎙️ Transcrição do <@{user_id}>: {texto}")

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


def setup(bot: discord.Bot):
    print("Voice carregando")
    obj = Voice(bot)
    bot.add_cog(obj)
    print("Voice carregado")
    return [obj]
