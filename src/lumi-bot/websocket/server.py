import asyncio
import logging

import socketio
from aiohttp import web

import config
from config import Key

app = web.Application()
sio = socketio.AsyncServer(
    async_mode="aiohttp",
    cors_allowed_origins="*",
    transports=["websocket"],
)
sio.attach(app)

# Socket.IO Admin connection
sio.instrument(auth={"username": "admin", "password": "admin123lumi"})


async def start_websocket():
    logging.info("Starting Socket.IO server...")
    logging.debug("Running server with API_URL: %s", config.get(Key.API_URL))

    try:
        runner = web.AppRunner(app)
        await runner.setup()

        sites: list[web.TCPSite] = []
        for host in [config.get(Key.API_URL)]:
            site = web.TCPSite(
                runner=runner,
                host=host,
                port=int(config.get(Key.API_PORT)),
            )
            sites.append(site)

        for site in sites:
            await site.start()

        logging.info("Socket.IO server listening on port %s", config.get(Key.API_PORT))
    except (ValueError, TypeError):
        logging.critical(
            "Invalid API_URL or API_PORT environment variable."
            "Please check your configuration.",
            exc_info=True,
        )
        raise
    except Exception:
        logging.critical(
            "Unknown error while starting Socket.IO server",
            exc_info=True,
        )
        raise

    while True:
        await asyncio.sleep(3600)
