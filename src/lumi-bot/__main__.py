import asyncio
import functools
import logging

from config import ENV
from service import Service, ServicesHandler


async def monitor_loop():
    while True:
        start_time = asyncio.get_running_loop().time()
        await asyncio.sleep(1)
        delta_time = asyncio.get_running_loop().time() - start_time
        if delta_time > 1.2:
            print(f"[Loop blocked for {delta_time:.2f}s]")


if __name__ == "__main__":
    import bot.main as bot
    import websocket as ws
    from bot.whisper import Model

    async def start():
        handler = ServicesHandler()
        handler.add_service(Service(ws.start_websocket))
        handler.add_service(
            Service(
                functools.partial(
                    bot.start_bot,
                    asyncio.get_event_loop(),
                )
            )
        )
        handler.add_service(Service(monitor_loop))
        await handler.run_all_services()

    debug_mode = ENV == "development"
    if debug_mode:
        asyncio.get_event_loop().set_debug(True)
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    Model.load_model()

    asyncio.run(start(), debug=debug_mode)
    # bot.run_bot()
