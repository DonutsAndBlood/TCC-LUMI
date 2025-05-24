import discord
from discord.ext import commands
import requests
import asyncio
import os

BASE_URL = "https://traducao2.vlibras.gov.br/translate"


class Tradutor(commands.Cog, name="Comando Tradutor"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="traduzir", help="Traduz texto para Libras e envia o vídeo")
    async def traduzir(self, ctx, *, texto):
        await ctx.send(f"Traduzindo: `{texto}` para Libras... 🔄")

        try:
            # 1. Obter glosa
            glosa_resp = requests.get(f"{BASE_URL}/translate", params={"text": texto})
            glosa_resp.raise_for_status()
            glosa = glosa_resp.text

            # 2. Requisitar vídeo
            video_resp = requests.post(f"{BASE_URL}/video", data={"gloss": glosa})
            video_resp.raise_for_status()
            video_id = video_resp.text

            # 3. Esperar processamento
            for _ in range(15):  # ~30s
                status_resp = requests.get(f"{BASE_URL}/video/status/{video_id}")
                status_resp.raise_for_status()
                status = status_resp.json()

                if status.get("status") == "DONE":
                    break
                await asyncio.sleep(2)
            else:
                await ctx.send(
                    "⏳ Tradução demorou demais. Tente novamente mais tarde."
                )
                return

            # 4. Baixar vídeo
            video_url = f"{BASE_URL}/video/{video_id}"
            video_data = requests.get(video_url)
            video_data.raise_for_status()

            filename = "libras_video.mp4"
            with open(filename, "wb") as f:
                f.write(video_data.content)

            await ctx.send(file=discord.File(filename))
            os.remove(filename)

        except Exception as e:
            await ctx.send(f"❌ Erro ao traduzir: `{str(e)}`")


def setup(bot):
    print("Tradutor carregando")
    bot.add_cog(Tradutor(bot))
    print("Tradutor carregado")
    return [Tradutor(bot)]
