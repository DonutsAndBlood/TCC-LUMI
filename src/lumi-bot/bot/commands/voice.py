import asyncio
import logging
from io import BytesIO
from typing import Any, Coroutine, Dict, Optional

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
from websocket import transcript


class Voice(commands.Cog, name="Comandos de Voz"):
    bot: discord.Bot
    recording_running: bool
    recording_paused: bool
    connections: Dict[int, VoiceClient]

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.recording_running = False
        self.view: VoiceControlView
        self.connections = {}

    @commands.command()
    async def gravar(self, ctx: ApplicationContext):
        if isinstance(ctx.author, discord.User):
            return

        voice = ctx.author.voice

        if voice is None or voice.channel is None:
            await ctx.send("Você não está em um canal de voz!")
            return

        vc: discord.VoiceClient = await voice.channel.connect()
        self.connections.update({ctx.guild.id: vc})

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

    async def start_recording_loop(self, ctx, vc: VoiceClient):
        self.recording_running = True

        while self.recording_running:
            sink = discord.sinks.OGGSink()

            # Começar a gravar
            try:
                vc.start_recording(sink, self.once_done, ctx)
            except RecordingException:
                await ctx.send("Já está gravando")
                return

            await asyncio.sleep(10)  # TEMPO DE GRAVAÇÃO
            if vc.recording:
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
            self.recording_running = False
            return

        audio_data: dict[int, discord.sinks.AudioData] = sink.audio_data
        for user_id, audio in audio_data.items():
            audio_file: BytesIO = audio.file

            try:
                # denoised = reduce_noise(audio_file)
                print(audio.finished)
                audio_array = load_audio_ndarray(audio_file)
                texto = transcribe_audio(audio_array)
                transcript.queue.put(texto)
                await ctx.send(f"🎙️ Transcrição do <@{user_id}>: {texto}")
            except Exception:  # pylint: disable=W0718
                logging.critical(
                    "Erro durante transcrição ou envio da mensagem",
                    exc_info=True,
                )

    async def stop_recording(self, ctx):
        self.recording_running = False

        # Verificar se está gravando antes de tentar parar
        if ctx.guild.id in self.connections:
            vc = self.connections[ctx.guild.id]
            if vc.recording:
                try:
                    vc.stop_recording()
                except RecordingException:
                    pass

            await vc.disconnect()
            self.connections.pop(ctx.guild.id)

        await ctx.send("Gravação finalizada!")


def setup(bot: discord.Bot):
    obj = Voice(bot)
    bot.add_cog(obj)
    print("Voice loaded")
    return [obj]


class VoiceControlView(discord.ui.View):

    def __init__(
        self,
        cog: Voice,
        ctx: ApplicationContext,
        vc: VoiceClient,
    ):
        super().__init__(timeout=None)
        self.cog = cog
        self.ctx = ctx
        self.vc = vc
        self.loop_coro: Optional[Coroutine[Any, Any, Any]] = None

    @discord.ui.button(label="▶️ Iniciar", style=ButtonStyle.success)
    async def start(
        self,
        _button: discord.ui.Button[Any],
        interaction: Interaction,
    ):
        if not self.cog.recording_running:
            await self.send_response(
                interaction,
                "🟢 Iniciando gravação...",
            )
            self.loop_coro = self.cog.start_recording_loop(self.ctx, self.vc)
            await self.loop_coro
        else:
            self.cog.recording_paused = False
            await self.send_response(
                interaction,
                "⏯️ Gravação retomada!",
            )

    # @discord.ui.button(label="⏸️ Pausar", style=ButtonStyle.primary)
    # async def pause(
    #     self,
    #     _button: discord.ui.Button[Any],
    #     interaction: Interaction,
    # ):
    #     if self.cog.gravando:
    #         self.cog.gravando = False
    #         self.cog.pausado = True
    #         if self.loop_coro is not None:
    #             await self.loop_coro
    #         await self.send_response(
    #             interaction,
    #             "⏸️ Gravação pausada!",
    #         )
    #     else:
    #         await self.send_response(
    #             interaction,
    #             "⚠️ Gravação não está ativa.",
    #         )

    @discord.ui.button(label="⏹️ Parar", style=ButtonStyle.danger)
    async def stop(  # type: ignore[override] # pylint: disable=W0236
        self,
        _button: discord.ui.Button[Any],
        interaction: Interaction,
    ):
        self.cog.recording_running = False
        self.cog.recording_paused = False

        # Verificar se está gravando antes de tentar parar
        self.cog.stop_recording(self.ctx)
        if interaction.message is not None:
            await interaction.message.delete()
        await self.send_response(
            interaction,
            "🔴 Gravação encerrada!",
        )

    async def send_response(self, interaction: Interaction, message: str):
        channel: Optional[TextChannel] = interaction.channel
        if channel is not None:
            vc_members = channel.members
            mentions_str = " ".join(
                [member.mention for member in vc_members if not member.bot]
            )
            await interaction.response.send_message(f"{message}\n{mentions_str}")

    def create_access_url(self, user_id: int) -> str:
        return f"http://lumi.myddns.me/{user_id}"
