import asyncio
from io import BytesIO
from typing import Any, Coroutine, Optional

import discord
from discord import (
    ApplicationContext,
    ButtonStyle,
    Interaction,
    TextChannel,
    VoiceClient,
)
from discord.ext import commands
from discord.voice_client import RecordingException  # type: ignore[attr-defined]

from bot.voice.processing import load_audio_ndarray
from bot.voice.transcriber import transcribe_audio

connections = {}


class Voice(commands.Cog, name="Comandos de Voz"):
    def __init__(self, bot):
        self.bot = bot
        self.gravando = False
        self.pausado = False
        self.view: VoiceControlView

    @commands.command()
    async def gravar(self, ctx: ApplicationContext):
        if isinstance(ctx.author, discord.User):
            return

        voice = ctx.author.voice

        if voice is None or voice.channel is None:
            await ctx.send("Você não está em um canal de voz!")
            return

        vc: discord.VoiceClient = await voice.channel.connect()
        connections.update({ctx.guild.id: vc})

        # (fetch criar sessão) return:id para concatenar no link

        embed = discord.Embed(
            title="🎙️ Tradução de voz em libras",
            description=(
                "**Como funciona:**\n"
                "O bot irá transcrever o áudio do canal de voz em tempo real.\n"
                "As transcrições serão enviadas no link a seguir 10 segundos:\n\n"
                "https:teste.com.br\n\n"
                "- ▶️ Inicia a gravação.\n"
                # "- ⏸️ Pausa a gravação.\n"
                "- ⏹️ Desconecta da chamada.\n\n"
            ),
            color=discord.Color.blue(),
        )

        self.view = VoiceControlView(self, ctx, vc)
        await ctx.send(embed=embed, view=self.view)

    async def gravar_loop(self, ctx, vc: VoiceClient):
        while self.gravando:
            sink = discord.sinks.OGGSink()

            # Começar a gravar
            try:
                vc.start_recording(sink, self.once_done, ctx)
            except RecordingException:
                await ctx.send("Já está gravando")
                return

            await asyncio.sleep(10)  # TEMPO DE GRAVAÇÃO
            vc.stop_recording()

            # Esperar o sink processar
            await asyncio.sleep(1)

    async def once_done(
        self,
        sink: discord.sinks.OGGSink,
        ctx: ApplicationContext,
        *_args,
    ):
        if sink.vc is None or sink.vc.decoder is None:
            await ctx.send("Erro ao realizar transcrição.")
            print("Erro ao trancrever áudio: 'sink.vc.decoder' não encontrado")
            self.gravando = False
            return

        audio_data: dict[int, discord.sinks.AudioData] = sink.audio_data
        for user_id, audio in audio_data.items():
            audio_file: BytesIO = audio.file

            # denoised = reduce_noise(audio_file)
            print(audio.finished)
            audio_array = load_audio_ndarray(audio_file)
            texto = transcribe_audio(audio_array)
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


class VoiceControlView(discord.ui.View):
    def __init__(self, cog, ctx: discord.ApplicationContext, vc: discord.VoiceClient):
        super().__init__(timeout=None)
        self.cog = cog
        self.ctx = ctx
        self.vc = vc
        self.loop_task = None

    @discord.ui.button(label="▶️ Iniciar", style=discord.ButtonStyle.success)
    async def start(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not self.cog.gravando:
            self.cog.gravando = True
            self.cog.pausado = False
            await interaction.response.send_message(
                "🟢 Iniciando gravação...", ephemeral=True
            )
            self.loop_task = asyncio.create_task(
                self.cog.gravar_loop(self.ctx, self.vc)
            )
        else:
            self.cog.pausado = False
            await interaction.response.send_message(
                "⏯️ Gravação retomada!", ephemeral=True
            )

    @discord.ui.button(label="⏸️ Pausar", style=discord.ButtonStyle.primary)
    async def pause(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.cog.gravando:
            self.cog.pausado = True
            await interaction.response.send_message(
                "⏸️ Gravação pausada!", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "⚠️ Gravação não está ativa.", ephemeral=True
            )

    @discord.ui.button(label="⏹️ Parar", style=discord.ButtonStyle.danger)
    async def stop(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.cog.gravando = False
        self.cog.pausado = False
        if self.ctx.guild.id in connections:
            vc = connections[self.ctx.guild.id]
            vc.stop_recording()
            await vc.disconnect()
            del connections[self.ctx.guild.id]
        await interaction.response.send_message(
            "🔴 Gravação encerrada!", ephemeral=True
        )
        self.stop()
