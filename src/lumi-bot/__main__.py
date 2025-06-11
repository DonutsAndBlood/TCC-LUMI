import asyncio

import bot.main as bot
import config
import websocket as ws
from bot.whisper import Model
from service import Service, ServicesHandler
from websocket import process_transcripts


async def monitor_loop():
    while True:
        start_time = asyncio.get_running_loop().time()
        await asyncio.sleep(1)
        delta_time = asyncio.get_running_loop().time() - start_time
        if delta_time > 1.2:
            print(f"[Loop blocked for {delta_time:.2f}s]")


if __name__ == "__main__":

    async def start():
        handler = ServicesHandler()
        handler.add_service(Service(ws.start_websocket, name="Socket.IO API"))
        handler.add_service(
            Service(
                bot.start_bot,
                name="Discord Bot",
                # loops=[asyncio.get_event_loop()],
            )
        )
        handler.add_service(
            Service(
                process_transcripts,
                name="Transcripts Queue Consumer",
            )
        )
        handler.add_service(Service(monitor_loop))
        await handler.run_all_services()

    config.load_variables()
    Model.load_model()

    asyncio.run(start())
    # bot.run_bot()
